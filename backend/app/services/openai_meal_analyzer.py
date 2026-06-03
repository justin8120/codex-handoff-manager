import base64
import json
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

import httpx
from fastapi import HTTPException, UploadFile
from openai import APIError, AuthenticationError, BadRequestError, OpenAI, RateLimitError

from app.models import MealAnalysisResult
from app.services.ai_provider import fallback_enabled, get_ai_provider
from app.services.url_fetcher import fetch_url_summary


CONFIGURATION_ERROR = "AI analysis service is not configured. Please set OPENAI_API_KEY."

SOURCE_TYPES = {"text", "image", "url"}

FALLBACK_MEAL_NAME = "AI fallback \u9910\u9ede\u5065\u5eb7\u5efa\u8b70"
FALLBACK_MEAL_TYPE = "\u5065\u5eb7\u9910"
TAG_LOW_CALORIE = "\u4f4e\u5361"
TAG_HIGH_PROTEIN = "\u9ad8\u86cb\u767d"
TAG_LOW_FAT = "\u4f4e\u8102"
TAG_HEALTHY = "\u5065\u5eb7\u9910"
TAG_VEGETARIAN = "\u7d20\u98df"
INGREDIENT_CHICKEN_BREAST = "\u96de\u80f8\u8089"
INGREDIENT_VEGETABLES = "\u852c\u83dc"
INGREDIENT_BROWN_RICE = "\u7cd9\u7c73"
INGREDIENT_BEEF = "\u725b\u8089"
ALLERGEN_PEANUT = "\u82b1\u751f"
ALLERGEN_SEAFOOD = "\u6d77\u9bae"
ALLERGEN_DAIRY = "\u4e73\u88fd\u54c1"
FALLBACK_REASON = (
    "\u76ee\u524d\u4f7f\u7528 rule-based fallback\uff1bAI "
    "\u670d\u52d9\u7121\u6cd5\u4f7f\u7528\u6216\u5c1a\u672a\u8a2d\u5b9a\uff0c"
    "\u56e0\u6b64\u7cfb\u7d71\u6539\u7528\u898f\u5247\u5f0f\u5206\u6790"
    "\u63d0\u4f9b\u5c55\u793a\u7d50\u679c\u3002"
)
DEFAULT_MEAL_NAME = "\u672a\u547d\u540d\u9910\u9ede"
DEFAULT_MEAL_TYPE = "\u7d9c\u5408\u9910"
DEFAULT_REASON = "AI \u5df2\u5b8c\u6210\u9910\u9ede\u5206\u6790\u3002"


def is_configured() -> bool:
    return get_ai_provider().configured


def provider_status() -> dict[str, object]:
    provider = get_ai_provider()
    return {
        "aiProvider": provider.name,
        "aiConfigured": provider.configured,
        "model": provider.model,
        "fallbackEnabled": fallback_enabled(),
    }


def analyze_text(text: str) -> MealAnalysisResult:
    return _safe_analyze("text", text=text)


async def analyze_image(file: UploadFile) -> MealAnalysisResult:
    content = await file.read()
    media_type = file.content_type or "image/jpeg"
    encoded = base64.b64encode(content).decode("ascii")
    data_url = f"data:{media_type};base64,{encoded}"
    return _safe_analyze("image", text=file.filename or "uploaded meal image", image_url=data_url)


async def analyze_url(url: str) -> MealAnalysisResult:
    try:
        summary = await fetch_url_summary(url)
    except httpx.HTTPError as error:
        if fallback_enabled():
            return _fallback_result(f"URL fetch failed: {url}", "url", confidence=0.4)
        raise HTTPException(status_code=502, detail=f"URL fetch failed: {error}") from error
    return _safe_analyze("url", text=f"URL: {url}\nExtracted content:\n{summary}")


def _safe_analyze(source_type: str, text: str, image_url: str | None = None) -> MealAnalysisResult:
    provider = get_ai_provider()
    if provider.name == "mock":
        return _fallback_result(text, source_type)
    if not provider.configured:
        if fallback_enabled():
            return _fallback_result(text, source_type, confidence=0.4)
        raise HTTPException(status_code=503, detail=CONFIGURATION_ERROR)

    try:
        return _call_chat_completion(provider_name=provider.name, text=text, source_type=source_type, image_url=image_url)
    except (
        RateLimitError,
        AuthenticationError,
        BadRequestError,
        APIError,
        TimeoutError,
        json.JSONDecodeError,
        Exception,
    ) as error:
        print(f"AI provider error ({provider.name}): {error}")
        if fallback_enabled():
            return _fallback_result(text, source_type, confidence=0.45)
        raise HTTPException(status_code=502, detail=f"AI provider error: {error}") from error


def _call_chat_completion(
    provider_name: str,
    text: str,
    source_type: str,
    image_url: str | None,
) -> MealAnalysisResult:
    provider = get_ai_provider()
    client = (
        OpenAI(api_key=provider.api_key, base_url=provider.base_url)
        if provider.base_url
        else OpenAI(api_key=provider.api_key)
    )
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": _instructions(source_type),
        },
    ]

    if image_url:
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analyze this meal image. Context: {text}"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        )
    else:
        messages.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model=provider.model,
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise json.JSONDecodeError("empty model response", "", 0)
    payload = json.loads(content)
    return _normalize_payload(payload, source_type, provider_name)


def _instructions(source_type: str) -> str:
    allowed_tags = ", ".join([TAG_LOW_CALORIE, TAG_HIGH_PROTEIN, TAG_LOW_FAT, TAG_HEALTHY, TAG_VEGETARIAN])
    allergens = ", ".join([ALLERGEN_PEANUT, INGREDIENT_BEEF, ALLERGEN_SEAFOOD, ALLERGEN_DAIRY])
    return (
        "You are a nutrition assistant for a smart diet recommendation system. "
        "Return only valid JSON, no markdown. "
        "The JSON must use camelCase keys and match this shape: "
        "{id, mealName, mealType, estimatedCalories, estimatedProtein, tags, mainIngredients, allergens, "
        "recommendationReason, confidence, sourceType, createdAt, isAiGenerated}. "
        "Use Traditional Chinese for user-facing values. "
        "Calories and protein must be estimates. "
        "Allowed sourceType values are text, image, url. "
        f"Use sourceType={source_type}. "
        f"Allowed diet tags include {allowed_tags}. "
        f"Allergens should focus on {allergens} when applicable. "
        "If uncertain, lower confidence instead of using 1.0."
    )


def _normalize_payload(payload: dict[str, Any], source_type: str, provider_name: str) -> MealAnalysisResult:
    payload["id"] = str(payload.get("id") or f"{provider_name}-{uuid4()}")
    payload["mealName"] = str(payload.get("mealName") or DEFAULT_MEAL_NAME)
    payload["mealType"] = str(payload.get("mealType") or DEFAULT_MEAL_TYPE)
    payload["estimatedCalories"] = float(payload.get("estimatedCalories") or 0)
    payload["estimatedProtein"] = float(payload.get("estimatedProtein") or 0)
    payload["tags"] = _string_list(payload.get("tags"))
    payload["mainIngredients"] = _string_list(payload.get("mainIngredients"))
    payload["allergens"] = _string_list(payload.get("allergens"))
    payload["recommendationReason"] = str(payload.get("recommendationReason") or DEFAULT_REASON)
    payload["confidence"] = max(0, min(float(payload.get("confidence") or 0.5), 1))
    payload["sourceType"] = source_type
    payload["createdAt"] = str(payload.get("createdAt") or datetime.now(timezone.utc).isoformat())
    payload["isAiGenerated"] = True
    return MealAnalysisResult.model_validate(payload)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


def _fallback_result(text: str, source_type: str, confidence: float | None = None) -> MealAnalysisResult:
    normalized = text.lower()
    tags = [TAG_LOW_CALORIE, TAG_HIGH_PROTEIN]
    main_ingredients = [INGREDIENT_CHICKEN_BREAST, INGREDIENT_VEGETABLES, INGREDIENT_BROWN_RICE]
    allergens = [ALLERGEN_PEANUT]

    if _has_any(normalized, [TAG_LOW_CALORIE, "\u6e1b\u8102", "\u7626\u8eab"]):
        tags = _add_unique(tags, TAG_LOW_CALORIE)
    if _has_any(normalized, [TAG_HIGH_PROTEIN, "\u589e\u808c"]):
        tags = _add_unique(tags, TAG_HIGH_PROTEIN)
    if _has_any(normalized, ["\u4e0d\u8981\u725b\u8089", "\u4e0d\u5403\u725b\u8089", "\u907f\u514d\u725b\u8089"]):
        main_ingredients = [ingredient for ingredient in main_ingredients if ingredient != INGREDIENT_BEEF]
    if _has_any(normalized, ["\u82b1\u751f\u904e\u654f", "\u907f\u514d\u82b1\u751f", "\u4e0d\u8981\u82b1\u751f"]):
        allergens = _add_unique(allergens, ALLERGEN_PEANUT)

    return MealAnalysisResult(
        id=f"fallback-{uuid4()}",
        mealName=FALLBACK_MEAL_NAME,
        mealType=FALLBACK_MEAL_TYPE,
        estimatedCalories=420,
        estimatedProtein=32,
        tags=tags,
        mainIngredients=main_ingredients,
        allergens=allergens,
        recommendationReason=FALLBACK_REASON,
        confidence=confidence or 0.55,
        sourceType=_source_type(source_type),
        createdAt=datetime.now(timezone.utc).isoformat(),
        isAiGenerated=True,
    )


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)


def _add_unique(values: list[str], value: str) -> list[str]:
    return values if value in values else [*values, value]


def _source_type(value: str) -> Literal["text", "image", "url"]:
    return value if value in SOURCE_TYPES else "text"  # type: ignore[return-value]
