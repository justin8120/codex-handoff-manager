import base64
import json
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from openai import OpenAI

from app.models import MealAnalysisResult
from app.services.url_fetcher import fetch_url_summary


CONFIGURATION_ERROR = "AI analysis service is not configured. Please set OPENAI_API_KEY."

MEAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "id": {"type": "string"},
        "mealName": {"type": "string"},
        "mealType": {"type": "string"},
        "estimatedCalories": {"type": "number"},
        "estimatedProtein": {"type": "number"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "mainIngredients": {"type": "array", "items": {"type": "string"}},
        "allergens": {"type": "array", "items": {"type": "string"}},
        "recommendationReason": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "sourceType": {"type": "string", "enum": ["text", "image", "url"]},
        "createdAt": {"type": "string"},
        "isAiGenerated": {"type": "boolean"},
    },
    "required": [
        "id",
        "mealName",
        "mealType",
        "estimatedCalories",
        "estimatedProtein",
        "tags",
        "mainIngredients",
        "allergens",
        "recommendationReason",
        "confidence",
        "sourceType",
        "createdAt",
        "isAiGenerated",
    ],
}


def is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _client() -> OpenAI:
    if not is_configured():
        raise HTTPException(status_code=503, detail=CONFIGURATION_ERROR)
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def _instructions(source_type: str) -> str:
    return (
        "You are a nutrition assistant for a smart diet recommendation system. "
        "Analyze the meal input and return only JSON that matches the schema. "
        "Estimate calories and protein; do not claim exact nutrition values. "
        "Use Traditional Chinese for mealName, mealType, tags, mainIngredients, allergens, and recommendationReason. "
        "Allowed tags should be selected from: 低卡, 高蛋白, 低脂, 健康餐, 素食 when applicable. "
        "Allergens should focus on: 花生, 牛肉, 海鮮, 乳製品 when applicable. "
        "If the meal cannot be confidently identified, lower confidence instead of guessing with certainty. "
        f"Set sourceType to {source_type}, isAiGenerated to true, id to a stable string, and createdAt to the current ISO time."
    )


def _response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "name": "meal_analysis_result",
        "strict": True,
        "schema": MEAL_SCHEMA,
    }


def _normalize_payload(payload: dict[str, Any], source_type: str) -> MealAnalysisResult:
    payload["id"] = payload.get("id") or f"ai-{uuid4()}"
    payload["sourceType"] = source_type
    payload["createdAt"] = payload.get("createdAt") or datetime.now(timezone.utc).isoformat()
    payload["isAiGenerated"] = True
    return MealAnalysisResult.model_validate(payload)


def _parse_response(response: Any, source_type: str) -> MealAnalysisResult:
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise HTTPException(status_code=502, detail="OpenAI response did not include output text.")
    try:
        payload = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="OpenAI response was not valid JSON.") from exc
    return _normalize_payload(payload, source_type)


def analyze_text(description: str) -> MealAnalysisResult:
    response = _client().responses.create(
        model=_model(),
        input=[
            {"role": "system", "content": _instructions("text")},
            {"role": "user", "content": f"Analyze this meal description: {description}"},
        ],
        text={"format": _response_format()},
    )
    return _parse_response(response, "text")


async def analyze_image(file: UploadFile) -> MealAnalysisResult:
    content = await file.read()
    media_type = file.content_type or "image/jpeg"
    encoded = base64.b64encode(content).decode("ascii")
    data_url = f"data:{media_type};base64,{encoded}"
    response = _client().responses.create(
        model=_model(),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": _instructions("image")},
                    {"type": "input_image", "image_url": data_url, "detail": "auto"},
                ],
            },
        ],
        text={"format": _response_format()},
    )
    return _parse_response(response, "image")


async def analyze_url(url: str) -> MealAnalysisResult:
    summary = await fetch_url_summary(url)
    response = _client().responses.create(
        model=_model(),
        input=[
            {"role": "system", "content": _instructions("url")},
            {
                "role": "user",
                "content": f"Analyze the meal or menu information from this single URL.\nURL: {url}\nExtracted content:\n{summary}",
            },
        ],
        text={"format": _response_format()},
    )
    return _parse_response(response, "url")
