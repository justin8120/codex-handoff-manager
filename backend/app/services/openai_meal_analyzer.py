import base64
import json
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

import httpx
from fastapi import HTTPException, UploadFile
from openai import APIError, AuthenticationError, BadRequestError, OpenAI, RateLimitError

from app.models import MealAnalysisResult
from app.services.ai_provider import (
    fallback_enabled,
    get_ai_provider,
    normalize_meal_name,
    normalize_user_facing_list,
    normalize_user_facing_text,
)
from app.services.url_fetcher import fetch_url_summary
from app.services import web_food_verifier


CONFIGURATION_ERROR = "AI analysis service is not configured. Please set OPENAI_API_KEY."

SOURCE_TYPES = {"text", "image", "url"}

FALLBACK_MEAL_NAME = "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70"
FALLBACK_MEAL_TYPE = "\u5065\u5eb7\u9910"
TAG_LOW_CALORIE = "\u4f4e\u5361"
TAG_HIGH_PROTEIN = "\u9ad8\u86cb\u767d"
TAG_LOW_FAT = "\u4f4e\u8102"
TAG_HEALTHY = "\u5065\u5eb7\u9910"
TAG_VEGETARIAN = "\u7d20\u98df"
TAG_RICE = "\u98ef\u985e"
TAG_SEAFOOD = "\u6d77\u9bae"
TAG_CHINESE = "\u4e2d\u5f0f\u6599\u7406"
TAG_BENTO = "\u4fbf\u7576"
TAG_JAPANESE = "\u65e5\u5f0f"
TAG_DONBURI = "\u4e3c\u98ef"
TAG_PORK = "\u8c6c\u8089"
TAG_CHICKEN = "\u96de\u8089"
INGREDIENT_CHICKEN_BREAST = "\u96de\u80f8\u8089"
INGREDIENT_VEGETABLES = "\u852c\u83dc"
INGREDIENT_BROWN_RICE = "\u7cd9\u7c73"
INGREDIENT_BEEF = "\u725b\u8089"
INGREDIENT_SHRIMP = "\u8766\u4ec1"
INGREDIENT_WHITE_RICE = "\u767d\u98ef"
INGREDIENT_EGG = "\u96de\u86cb"
INGREDIENT_SCALLION = "\u9752\u8525"
INGREDIENT_PORK_SLICES = "\u8c6c\u8089\u7247"
INGREDIENT_NORI = "\u6d77\u82d4"
INGREDIENT_CHICKEN = "\u96de\u8089"
INGREDIENT_ONION = "\u6d0b\u8525"
ALLERGEN_PEANUT = "\u82b1\u751f"
ALLERGEN_SHRIMP = "\u8766"
ALLERGEN_EGG = "\u86cb"
ALLERGEN_SEAFOOD = "\u6d77\u9bae"
ALLERGEN_DAIRY = "\u4e73\u88fd\u54c1"
FALLBACK_REASON = (
    "\u7cfb\u7d71\u5df2\u6839\u64da\u8f38\u5165\u5167\u5bb9"
    "\u63d0\u4f9b\u9910\u9ede\u5065\u5eb7\u5efa\u8b70\u3002"
)
SHRIMP_FRIED_RICE = "\u8766\u4ec1\u7092\u98ef"
FRIED_RICE = "\u7092\u98ef"
MEAL_TYPE_RICE = "\u98ef\u985e"
MEAL_TYPE_BENTO = "\u4fbf\u7576"
MEAL_TYPE_JAPANESE_DONBURI = "\u65e5\u5f0f\u4e3c\u98ef"
BUTADON = "\u8c5a\u4e3c"
TON_I = "\u8c5a\u4e95"
PORK_DONBURI = "\u8c6c\u8089\u4e3c"
OYAKODON = "\u89aa\u5b50\u4e3c"
SUSPECTED_BUTADON = "\u7591\u4f3c\u8c5a\u4e3c"
CHICKEN_BREAST_HEALTHY_MEAL = "\u96de\u80f8\u8089\u5065\u5eb7\u9910"
BUTADON_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u8c5a\u4e3c\u3002"
    "\u96d6\u7136\u7167\u7247\u4e2d\u6709\u86cb\u8207\u767d\u98ef\uff0c"
    "\u5916\u89c0\u5bb9\u6613\u8207\u89aa\u5b50\u4e3c\u6df7\u6dc6\uff0c"
    "\u4f46\u756b\u9762\u4e2d\u7684\u8089\u7247\u8f03\u63a5\u8fd1\u8c6c\u8089\u7247\uff0c"
    "\u4e14\u672a\u660e\u78ba\u770b\u5230\u96de\u8089\u584a\uff0c\u56e0\u6b64\u5224\u65b7\u70ba\u8c5a\u4e3c\u3002"
)
SUSPECTED_BUTADON_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u53ef\u80fd\u70ba\u8c5a\u4e3c\u3002"
    "\u756b\u9762\u4e2d\u6709\u86cb\u8207\u767d\u98ef\uff0c"
    "\u4f46\u8089\u985e\u7279\u5fb5\u4ecd\u6709\u4e0d\u78ba\u5b9a\u6027\uff0c"
    "\u56e0\u6b64\u4ee5\u8f03\u4fdd\u5b88\u7684\u4fe1\u5fc3\u5206\u6578\u5448\u73fe\u3002"
)
OYAKODON_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u89aa\u5b50\u4e3c\uff0c"
    "\u4e3b\u8981\u98df\u6750\u5305\u542b\u96de\u8089\u3001\u96de\u86cb\u8207\u767d\u98ef\u3002"
)
SHRIMP_FRIED_RICE_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u8766\u4ec1\u7092\u98ef\uff0c"
    "\u4e3b\u8981\u98df\u6750\u5305\u542b\u8766\u4ec1\u3001\u767d\u98ef\u8207\u96de\u86cb\u3002"
    "\u6b64\u9910\u9ede\u542b\u6709\u86cb\u767d\u8cea\u4f86\u6e90\uff0c"
    "\u4f46\u7092\u98ef\u901a\u5e38\u6cb9\u8102\u8207\u71b1\u91cf\u8f03\u9ad8\uff0c"
    "\u5efa\u8b70\u642d\u914d\u852c\u83dc\u6216\u63a7\u5236\u4efd\u91cf\u3002"
)
FRIED_RICE_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u7092\u98ef\uff0c"
    "\u5c6c\u65bc\u98ef\u985e\u6599\u7406\u3002"
    "\u7092\u98ef\u901a\u5e38\u71b1\u91cf\u8207\u6cb9\u8102\u8f03\u9ad8\uff0c"
    "\u5efa\u8b70\u63a7\u5236\u4efd\u91cf\u4e26\u642d\u914d\u852c\u83dc\u3002"
)
BEEF_EXCLUDED_NOTE = "\u5df2\u6839\u64da\u9700\u6c42\u6392\u9664\u725b\u8089\u3002"
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
        if source_type == "image" and image_url:
            return _analyze_image_with_verification(provider.name, text, image_url)
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


def _analyze_image_with_verification(provider_name: str, text: str, image_url: str) -> MealAnalysisResult:
    payload = _call_image_candidate_completion(provider_name, text, image_url)
    visual_description = str(payload.get("visualDescription") or payload.get("visual_description") or text)
    candidates = _candidate_list(payload.get("candidates"))
    if not candidates:
        return _fallback_result(text, "image", confidence=0.45)

    try:
        verification = web_food_verifier.verify_food_candidates(candidates, visual_description)
    except Exception as error:
        print(f"Food candidate verification failed: {error}")
        verification = _local_verification_from_candidates(candidates, visual_description)

    return _meal_from_verification_result(verification, "image", provider_name)


def _call_image_candidate_completion(provider_name: str, text: str, image_url: str) -> dict[str, Any]:
    provider = get_ai_provider()
    client = (
        OpenAI(api_key=provider.api_key, base_url=provider.base_url)
        if provider.base_url
        else OpenAI(api_key=provider.api_key)
    )
    response = client.chat.completions.create(
        model=provider.model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a food vision analyst. Return only valid JSON, no markdown. "
                    "Analyze the image in two parts: visualDescription and candidates. "
                    "Do not return a single final answer. candidates must be an array of objects with "
                    "name, confidence, and evidence. Include 3 to 5 plausible meals. "
                    "Pay special attention to butadon (\u8c5a\u4e3c) vs oyakodon (\u89aa\u5b50\u4e3c). "
                    "Do not decide oyakodon from egg and rice alone; look for chicken chunks. "
                    "If visible meat looks like pork slices, include \u8c5a\u4e3c or \u8c6c\u8089\u4e3c."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analyze this meal image. Context or filename: {text}"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise json.JSONDecodeError("empty model response", "", 0)
    return json.loads(content)


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
    payload["mealName"] = normalize_meal_name(str(payload.get("mealName") or DEFAULT_MEAL_NAME))
    payload["mealType"] = normalize_user_facing_text(str(payload.get("mealType") or DEFAULT_MEAL_TYPE))
    payload["estimatedCalories"] = float(payload.get("estimatedCalories") or 0)
    payload["estimatedProtein"] = float(payload.get("estimatedProtein") or 0)
    payload["tags"] = normalize_user_facing_list(_string_list(payload.get("tags")))
    payload["mainIngredients"] = normalize_user_facing_list(_string_list(payload.get("mainIngredients")))
    payload["allergens"] = normalize_user_facing_list(_string_list(payload.get("allergens")))
    payload["recommendationReason"] = normalize_user_facing_text(str(payload.get("recommendationReason") or DEFAULT_REASON))
    payload["confidence"] = max(0, min(float(payload.get("confidence") or 0.5), 1))
    payload["sourceType"] = source_type
    payload["createdAt"] = str(payload.get("createdAt") or datetime.now(timezone.utc).isoformat())
    payload["isAiGenerated"] = True
    return MealAnalysisResult.model_validate(payload)


def _candidate_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    candidates: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        candidates.append(
            {
                "name": normalize_meal_name(str(item.get("name") or item.get("mealName") or "")),
                "confidence": max(0, min(float(item.get("confidence") or 0.45), 1)),
                "evidence": normalize_user_facing_list(_string_list(item.get("evidence"))),
            },
        )
    return candidates


def _local_verification_from_candidates(candidates: list[dict[str, Any]], visual_description: str) -> dict[str, Any]:
    try:
        return web_food_verifier.rerank_food_candidates(candidates, visual_description)
    except Exception:
        first = candidates[0] if candidates else {}
        return {
            "verifiedName": normalize_meal_name(str(first.get("name") or SUSPECTED_BUTADON)),
            "verifiedType": normalize_user_facing_text(MEAL_TYPE_JAPANESE_DONBURI),
            "confidence": max(0.45, min(float(first.get("confidence") or 0.45), 1)),
            "matchedEvidence": normalize_user_facing_list(_string_list(first.get("evidence"))),
            "rejectedCandidates": [],
            "sources": [],
            "reason": SUSPECTED_BUTADON_REASON,
        }


def _meal_from_verification_result(
    verification: dict[str, Any],
    source_type: str,
    provider_name: str,
) -> MealAnalysisResult:
    name = normalize_meal_name(str(verification.get("verifiedName") or SUSPECTED_BUTADON))
    confidence = max(0, min(float(verification.get("confidence") or 0.65), 1))
    if _is_butadon_text(name):
        return _butadon_result(source_type, confidence=confidence, provider_name=provider_name)
    if OYAKODON in name or "oyakodon" in name.lower():
        return _oyakodon_result(source_type, confidence=min(confidence, 0.75), provider_name=provider_name)

    reason = normalize_user_facing_text(str(verification.get("reason") or DEFAULT_REASON))
    return MealAnalysisResult(
        id=f"{provider_name}-{uuid4()}",
        mealName=name,
        mealType=normalize_user_facing_text(str(verification.get("verifiedType") or DEFAULT_MEAL_TYPE)),
        estimatedCalories=0,
        estimatedProtein=0,
        tags=[],
        mainIngredients=[],
        allergens=[],
        recommendationReason=reason,
        confidence=confidence,
        sourceType=_source_type(source_type),
        createdAt=datetime.now(timezone.utc).isoformat(),
        isAiGenerated=True,
    )


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


def _fallback_result(text: str, source_type: str, confidence: float | None = None) -> MealAnalysisResult:
    normalized = text.lower()
    meal_name = FALLBACK_MEAL_NAME
    meal_type = FALLBACK_MEAL_TYPE
    calories = 420
    protein = 32
    tags = [TAG_LOW_CALORIE, TAG_HIGH_PROTEIN]
    main_ingredients = [INGREDIENT_CHICKEN_BREAST, INGREDIENT_VEGETABLES, INGREDIENT_BROWN_RICE]
    allergens: list[str] = []
    reason = FALLBACK_REASON
    confidence_value = confidence or 0.55

    if _is_butadon_text(normalized):
        return _butadon_result(source_type, confidence=confidence or 0.75)
    if OYAKODON in normalized or "oyakodon" in normalized:
        return _oyakodon_result(source_type, confidence=confidence or 0.72)

    if SHRIMP_FRIED_RICE in normalized:
        meal_name = SHRIMP_FRIED_RICE
        meal_type = MEAL_TYPE_RICE
        calories = 650
        protein = 22
        tags = [TAG_RICE, TAG_SEAFOOD, TAG_CHINESE]
        main_ingredients = [INGREDIENT_SHRIMP, INGREDIENT_WHITE_RICE, INGREDIENT_EGG, INGREDIENT_SCALLION]
        allergens = [ALLERGEN_SHRIMP, ALLERGEN_EGG]
        reason = SHRIMP_FRIED_RICE_REASON
        confidence_value = 0.75
    elif FRIED_RICE in normalized:
        meal_name = FRIED_RICE
        meal_type = MEAL_TYPE_RICE
        calories = 620
        protein = 18
        tags = [TAG_RICE, TAG_CHINESE]
        main_ingredients = [INGREDIENT_WHITE_RICE, INGREDIENT_EGG, INGREDIENT_SCALLION]
        allergens = [ALLERGEN_EGG]
        reason = FRIED_RICE_REASON
        confidence_value = 0.7

    if MEAL_TYPE_BENTO in normalized:
        meal_type = MEAL_TYPE_BENTO
        tags = _add_unique(tags, TAG_BENTO)
    if "\u96de\u80f8" in normalized:
        meal_name = CHICKEN_BREAST_HEALTHY_MEAL
        main_ingredients = _add_unique(main_ingredients, INGREDIENT_CHICKEN_BREAST)
        tags = _add_unique(tags, TAG_HIGH_PROTEIN)
    if INGREDIENT_BEEF in normalized:
        main_ingredients = _add_unique(main_ingredients, INGREDIENT_BEEF)

    if _has_any(normalized, [TAG_LOW_CALORIE, "\u6e1b\u8102", "\u7626\u8eab"]):
        tags = _add_unique(tags, TAG_LOW_CALORIE)
    if _has_any(normalized, [TAG_HIGH_PROTEIN, "\u589e\u808c"]):
        tags = _add_unique(tags, TAG_HIGH_PROTEIN)
    if _has_any(normalized, ["\u4e0d\u8981\u725b\u8089", "\u4e0d\u5403\u725b\u8089", "\u907f\u514d\u725b\u8089"]):
        main_ingredients = [ingredient for ingredient in main_ingredients if ingredient != INGREDIENT_BEEF]
        reason = f"{reason}{BEEF_EXCLUDED_NOTE}"
    if _has_any(normalized, ["\u82b1\u751f\u904e\u654f", "\u907f\u514d\u82b1\u751f", "\u4e0d\u8981\u82b1\u751f"]):
        allergens = _add_unique(allergens, ALLERGEN_PEANUT)

    return MealAnalysisResult(
        id=f"system-{uuid4()}",
        mealName=normalize_meal_name(meal_name),
        mealType=normalize_user_facing_text(meal_type),
        estimatedCalories=calories,
        estimatedProtein=protein,
        tags=normalize_user_facing_list(tags),
        mainIngredients=normalize_user_facing_list(main_ingredients),
        allergens=normalize_user_facing_list(allergens),
        recommendationReason=normalize_user_facing_text(reason),
        confidence=confidence_value,
        sourceType=_source_type(source_type),
        createdAt=datetime.now(timezone.utc).isoformat(),
        isAiGenerated=True,
    )


def _has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)


def _add_unique(values: list[str], value: str) -> list[str]:
    return values if value in values else [*values, value]


def _is_butadon_text(text: str) -> bool:
    normalized = normalize_meal_name(text)
    return BUTADON in normalized or PORK_DONBURI in normalized


def _butadon_result(
    source_type: str,
    confidence: float,
    provider_name: str = "system",
    suspected: bool = False,
) -> MealAnalysisResult:
    meal_name = SUSPECTED_BUTADON if suspected else BUTADON
    return MealAnalysisResult(
        id=f"{provider_name}-{uuid4()}",
        mealName=meal_name,
        mealType=MEAL_TYPE_JAPANESE_DONBURI,
        estimatedCalories=650,
        estimatedProtein=28,
        tags=[TAG_JAPANESE, TAG_DONBURI, TAG_PORK],
        mainIngredients=[INGREDIENT_WHITE_RICE, INGREDIENT_PORK_SLICES, INGREDIENT_EGG, INGREDIENT_NORI],
        allergens=[ALLERGEN_EGG],
        recommendationReason=SUSPECTED_BUTADON_REASON if suspected else BUTADON_REASON,
        confidence=max(0, min(confidence, 1)),
        sourceType=_source_type(source_type),
        createdAt=datetime.now(timezone.utc).isoformat(),
        isAiGenerated=True,
    )


def _oyakodon_result(source_type: str, confidence: float, provider_name: str = "system") -> MealAnalysisResult:
    return MealAnalysisResult(
        id=f"{provider_name}-{uuid4()}",
        mealName=OYAKODON,
        mealType=MEAL_TYPE_JAPANESE_DONBURI,
        estimatedCalories=620,
        estimatedProtein=30,
        tags=[TAG_JAPANESE, TAG_DONBURI, TAG_CHICKEN],
        mainIngredients=[INGREDIENT_WHITE_RICE, INGREDIENT_CHICKEN, INGREDIENT_EGG, INGREDIENT_ONION],
        allergens=[ALLERGEN_EGG],
        recommendationReason=OYAKODON_REASON,
        confidence=max(0, min(confidence, 0.75)),
        sourceType=_source_type(source_type),
        createdAt=datetime.now(timezone.utc).isoformat(),
        isAiGenerated=True,
    )


def _source_type(value: str) -> Literal["text", "image", "url"]:
    return value if value in SOURCE_TYPES else "text"  # type: ignore[return-value]
