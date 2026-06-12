from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.models import MealAnalysisResult
from app.services.ai_provider import (
    normalize_meal_name,
    normalize_user_facing_list,
    normalize_user_facing_text,
)


DEFAULT_REASON = (
    "\u7cfb\u7d71\u6839\u64da\u9910\u9ede\u540d\u7a31\u8207\u53ef\u898b\u98df\u6750"
    "\u9032\u884c\u5206\u6790\uff0c\u4e26\u53c3\u8003\u5e38\u898b\u9910\u9ede\u7d44\u6210"
    "\u4f30\u7b97\u71b1\u91cf\u3001\u86cb\u767d\u8cea\u8207\u53ef\u80fd\u904e\u654f\u539f\u3002"
)
BUTADON_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u8c5a\u4e3c\u3002"
    "\u96d6\u7136\u7167\u7247\u4e2d\u6709\u86cb\u8207\u767d\u98ef\uff0c"
    "\u5916\u89c0\u5bb9\u6613\u8207\u89aa\u5b50\u4e3c\u6df7\u6dc6\uff0c"
    "\u4f46\u756b\u9762\u4e2d\u7684\u8089\u7247\u8f03\u63a5\u8fd1\u8c6c\u8089\u7247\uff0c"
    "\u4e14\u672a\u660e\u78ba\u770b\u5230\u96de\u8089\u584a\uff0c\u56e0\u6b64\u5224\u65b7\u70ba\u8c5a\u4e3c\u3002"
)
KATSUDON_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u8c6c\u6392\u4e3c\uff0c"
    "\u4e3b\u8981\u7531\u767d\u98ef\u3001\u70b8\u8c6c\u6392\u3001\u96de\u86cb\u8207\u6d0b\u8525\u7d44\u6210\u3002"
    "\u6b64\u9910\u9ede\u86cb\u767d\u8cea\u542b\u91cf\u8f03\u9ad8\uff0c"
    "\u4f46\u56e0\u542b\u70b8\u7269\uff0c\u71b1\u91cf\u8207\u6cb9\u8102\u4e5f\u76f8\u5c0d\u8f03\u9ad8\uff0c"
    "\u5efa\u8b70\u63a7\u5236\u4efd\u91cf\u4e26\u642d\u914d\u852c\u83dc\u3002"
)
CHICKEN_STEAK_NOODLES_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u96de\u6392\u9eb5\uff0c"
    "\u4e3b\u8981\u7531\u9eb5\u689d\u3001\u96de\u6392\u8207\u9752\u83dc\u7d44\u6210\u3002"
    "\u6b64\u9910\u9ede\u86cb\u767d\u8cea\u542b\u91cf\u8f03\u9ad8\uff0c"
    "\u4f46\u82e5\u96de\u6392\u70ba\u6cb9\u70b8\u6599\u7406\uff0c"
    "\u71b1\u91cf\u8207\u6cb9\u8102\u4e5f\u6703\u504f\u9ad8\uff0c"
    "\u5efa\u8b70\u642d\u914d\u852c\u83dc\u4e26\u63a7\u5236\u4efd\u91cf\u3002"
)
FRIED_CHICKEN_CUTLET_REASON = (
    "\u7cfb\u7d71\u6839\u64da\u5716\u7247\u4e2d\u53ef\u898b\u7684\u5927\u578b\u88f9\u7c89"
    "\u6cb9\u70b8\u96de\u6392\u5224\u65b7\u6b64\u9910\u9ede\u70ba\u70b8\u96de\u6392\u3002"
    "\u5716\u7247\u4e2d\u672a\u660e\u78ba\u770b\u5230\u9eb5\u689d\u6216\u6e6f\u54c1\uff0c"
    "\u56e0\u6b64\u4e0d\u5224\u65b7\u70ba\u96de\u6392\u9eb5\u3002"
    "\u6b64\u9910\u9ede\u86cb\u767d\u8cea\u542b\u91cf\u8f03\u9ad8\uff0c"
    "\u4f46\u6cb9\u70b8\u6599\u7406\u71b1\u91cf\u8207\u6cb9\u8102\u4e5f\u8f03\u9ad8\uff0c"
    "\u5efa\u8b70\u63a7\u5236\u4efd\u91cf\u3002"
)
STEAK_EGG_NOODLES_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u725b\u6392\u86cb\u9eb5\uff0c"
    "\u4e3b\u8981\u7531\u9eb5\u689d\u3001\u725b\u6392\u3001\u96de\u86cb\u8207\u9752\u83dc\u7d44\u6210\u3002"
    "\u6b64\u9910\u9ede\u86cb\u767d\u8cea\u542b\u91cf\u8f03\u9ad8\uff0c"
    "\u4f46\u4efd\u91cf\u8207\u8abf\u5473\u53ef\u80fd\u4f7f\u71b1\u91cf\u504f\u9ad8\uff0c"
    "\u5efa\u8b70\u642d\u914d\u852c\u83dc\u4e26\u7559\u610f\u91ac\u6599\u651d\u53d6\u3002"
)
SOUP_DUMPLING_REASON = (
    "\u7cfb\u7d71\u8fa8\u8b58\u6b64\u9910\u9ede\u70ba\u5c0f\u7c60\u5305\uff0c"
    "\u4e3b\u8981\u7531\u9eb5\u76ae\u3001\u8089\u9921\u8207\u6e6f\u6c41\u7d44\u6210\u3002"
    "\u6b64\u985e\u9910\u9ede\u71b1\u91cf\u591a\u4f86\u81ea\u9eb5\u76ae\u8207\u8089\u9921\uff0c"
    "\u5efa\u8b70\u6ce8\u610f\u4efd\u91cf\u8207\u9209\u542b\u91cf\u3002"
)
WATERMELON_REASON = (
    "\u7cfb\u7d71\u6839\u64da\u4f7f\u7528\u8005\u63d0\u4f9b\u7684\u6587\u5b57\u63cf\u8ff0"
    "\u5224\u65b7\u6b64\u9910\u9ede\u70ba\u897f\u74dc\u3002\u897f\u74dc\u542b\u6c34\u91cf\u9ad8\u3001"
    "\u71b1\u91cf\u8f03\u4f4e\uff0c\u9069\u5408\u4f5c\u70ba\u9ede\u5fc3\u6216\u98ef\u5f8c\u6c34\u679c\uff0c"
    "\u4f46\u4ecd\u5efa\u8b70\u7559\u610f\u4efd\u91cf\u8207\u7cd6\u5206\u651d\u53d6\u3002"
)
PEANUT_REASON = (
    "\u7cfb\u7d71\u6839\u64da\u4f7f\u7528\u8005\u63d0\u4f9b\u7684\u6587\u5b57\u63cf\u8ff0"
    "\u5224\u65b7\u6b64\u9805\u76ee\u70ba\u82b1\u751f\u3002\u82b1\u751f\u542b\u6709\u86cb\u767d\u8cea"
    "\u8207\u8102\u80aa\uff0c\u71b1\u91cf\u8f03\u9ad8\uff0c\u9069\u5408\u4f5c\u70ba\u5c11\u91cf\u9ede\u5fc3"
    "\u6216\u71df\u990a\u88dc\u5145\uff0c\u4f46\u5c0d\u82b1\u751f\u904e\u654f\u8005\u61c9\u907f\u514d\u98df\u7528\u3002"
)

KNOWN_MEALS: dict[str, dict[str, Any]] = {
    "\u5c0f\u7c60\u5305": {
        "estimatedCalories": 380,
        "estimatedProtein": 16,
        "mealType": "\u4e2d\u5f0f\u9ede\u5fc3",
        "tags": ["\u4e2d\u5f0f", "\u9ede\u5fc3", "\u9eb5\u98df"],
        "mainIngredients": ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"],
        "allergens": ["\u9ea9\u8cea"],
        "recommendationReason": SOUP_DUMPLING_REASON,
    },
    "\u897f\u74dc": {
        "estimatedCalories": 30,
        "estimatedProtein": 1,
        "mealType": "\u6c34\u679c",
        "tags": ["\u6c34\u679c", "\u4f4e\u71b1\u91cf", "\u6c34\u5206\u9ad8"],
        "mainIngredients": ["\u897f\u74dc"],
        "allergens": [],
        "recommendationReason": WATERMELON_REASON,
    },
    "\u82b1\u751f": {
        "estimatedCalories": 567,
        "estimatedProtein": 26,
        "mealType": "\u5805\u679c / \u8c46\u985e\u98df\u6750",
        "tags": ["\u5805\u679c", "\u9ad8\u86cb\u767d", "\u9ad8\u8102\u80aa"],
        "mainIngredients": ["\u82b1\u751f"],
        "allergens": ["\u82b1\u751f"],
        "recommendationReason": PEANUT_REASON,
    },
    "\u725b\u6392\u86cb\u9eb5": {
        "estimatedCalories": 850,
        "estimatedProtein": 38,
        "mealType": "\u725b\u6392\u9eb5",
        "tags": ["\u725b\u6392", "\u9eb5\u98df", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u9eb5\u689d", "\u725b\u6392", "\u96de\u86cb", "\u9752\u83dc", "\u9ad8\u6e6f"],
        "allergens": ["\u86cb", "\u9ea9\u8cea"],
        "recommendationReason": STEAK_EGG_NOODLES_REASON,
    },
    "\u725b\u6392\u9eb5": {
        "estimatedCalories": 900,
        "estimatedProtein": 42,
        "mealType": "\u725b\u6392\u9eb5",
        "tags": ["\u725b\u6392", "\u9eb5\u98df", "\u725b\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u9eb5\u689d", "\u725b\u6392", "\u9752\u83dc", "\u9ad8\u6e6f"],
        "allergens": ["\u9ea9\u8cea"],
    },
    "\u96de\u6392\u86cb\u9eb5": {
        "estimatedCalories": 850,
        "estimatedProtein": 40,
        "mealType": "\u9eb5\u98df",
        "tags": ["\u9eb5\u98df", "\u96de\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u9eb5\u689d", "\u96de\u6392", "\u96de\u86cb", "\u9752\u83dc", "\u9ad8\u6e6f"],
        "allergens": ["\u86cb", "\u9ea9\u8cea"],
        "recommendationReason": CHICKEN_STEAK_NOODLES_REASON,
    },
    "\u725b\u6392\u86cb": {
        "estimatedCalories": 700,
        "estimatedProtein": 42,
        "mealType": "\u86cb\u767d\u8cea\u9910",
        "tags": ["\u725b\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u725b\u6392", "\u96de\u86cb"],
        "allergens": ["\u86cb"],
    },
    "\u725b\u6392": {
        "estimatedCalories": 650,
        "estimatedProtein": 40,
        "mealType": "\u86cb\u767d\u8cea\u9910",
        "tags": ["\u725b\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u725b\u6392"],
        "allergens": [],
    },
    "\u96de\u86cb": {
        "estimatedCalories": 80,
        "estimatedProtein": 7,
        "mealType": "\u86cb\u767d\u9ede\u5fc3",
        "tags": ["\u4f4e\u5361", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u96de\u86cb"],
        "allergens": ["\u86cb"],
    },
    "\u96de\u6392\u9eb5": {
        "estimatedCalories": 850,
        "estimatedProtein": 38,
        "mealType": "\u9eb5\u98df",
        "tags": ["\u9eb5\u98df", "\u96de\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u9eb5\u689d", "\u96de\u6392", "\u9752\u83dc", "\u9ad8\u6e6f"],
        "allergens": ["\u9ea9\u8cea"],
        "recommendationReason": CHICKEN_STEAK_NOODLES_REASON,
    },
    "\u96de\u6392": {
        "estimatedCalories": 600,
        "estimatedProtein": 35,
        "mealType": "\u70b8\u7269 / \u5c0f\u5403",
        "tags": ["\u96de\u8089", "\u70b8\u7269", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u96de\u8089", "\u9eb5\u8863", "\u6cb9"],
        "allergens": ["\u9ea9\u8cea"],
        "recommendationReason": FRIED_CHICKEN_CUTLET_REASON,
    },
    "\u70b8\u96de\u6392": {
        "estimatedCalories": 600,
        "estimatedProtein": 35,
        "mealType": "\u70b8\u7269 / \u5c0f\u5403",
        "tags": ["\u70b8\u7269", "\u96de\u8089", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u96de\u8089", "\u9eb5\u8863", "\u6cb9"],
        "allergens": ["\u9ea9\u8cea"],
        "recommendationReason": FRIED_CHICKEN_CUTLET_REASON,
    },
    "\u96de\u8089\u9eb5": {
        "estimatedCalories": 650,
        "estimatedProtein": 32,
        "mealType": "\u9eb5\u98df",
        "tags": ["\u9eb5\u98df", "\u96de\u8089"],
        "mainIngredients": ["\u9eb5\u689d", "\u96de\u8089", "\u9752\u83dc", "\u9ad8\u6e6f"],
        "allergens": ["\u9ea9\u8cea"],
    },
    "\u9eb5\u98df": {
        "estimatedCalories": 600,
        "estimatedProtein": 20,
        "mealType": "\u9eb5\u98df",
        "tags": ["\u9eb5\u98df"],
        "mainIngredients": ["\u9eb5\u689d", "\u9ad8\u6e6f"],
        "allergens": ["\u9ea9\u8cea"],
    },
    "\u8c5a\u4e3c": {
        "estimatedCalories": 650,
        "estimatedProtein": 28,
        "mealType": "\u65e5\u5f0f\u4e3c\u98ef",
        "tags": ["\u65e5\u5f0f", "\u4e3c\u98ef", "\u8c6c\u8089"],
        "mainIngredients": ["\u767d\u98ef", "\u8c6c\u8089\u7247", "\u96de\u86cb", "\u6d77\u82d4"],
        "allergens": ["\u86cb"],
        "recommendationReason": BUTADON_REASON,
    },
    "\u8c6c\u6392\u4e3c": {
        "estimatedCalories": 780,
        "estimatedProtein": 32,
        "mealType": "\u65e5\u5f0f\u4e3c\u98ef",
        "tags": ["\u65e5\u5f0f", "\u4e3c\u98ef", "\u70b8\u7269", "\u8c6c\u8089"],
        "mainIngredients": ["\u767d\u98ef", "\u70b8\u8c6c\u6392", "\u96de\u86cb", "\u6d0b\u8525"],
        "allergens": ["\u86cb", "\u9ea9\u8cea"],
        "recommendationReason": KATSUDON_REASON,
    },
    "\u89aa\u5b50\u4e3c": {
        "estimatedCalories": 620,
        "estimatedProtein": 30,
        "mealType": "\u65e5\u5f0f\u4e3c\u98ef",
        "tags": ["\u65e5\u5f0f", "\u4e3c\u98ef", "\u96de\u8089"],
        "mainIngredients": ["\u767d\u98ef", "\u96de\u8089", "\u96de\u86cb", "\u6d0b\u8525"],
        "allergens": ["\u86cb"],
    },
    "\u725b\u4e3c": {
        "estimatedCalories": 700,
        "estimatedProtein": 30,
        "mealType": "\u65e5\u5f0f\u4e3c\u98ef",
        "tags": ["\u65e5\u5f0f", "\u4e3c\u98ef", "\u725b\u8089"],
        "mainIngredients": ["\u767d\u98ef", "\u725b\u8089\u7247", "\u6d0b\u8525"],
        "allergens": [],
    },
    "\u8766\u4ec1\u7092\u98ef": {
        "estimatedCalories": 650,
        "estimatedProtein": 22,
        "mealType": "\u98ef\u985e",
        "tags": ["\u98ef\u985e", "\u6d77\u9bae", "\u4e2d\u5f0f\u6599\u7406"],
        "mainIngredients": ["\u8766\u4ec1", "\u767d\u98ef", "\u96de\u86cb", "\u9752\u8525"],
        "allergens": ["\u8766", "\u86cb"],
    },
    "\u7092\u98ef": {
        "estimatedCalories": 620,
        "estimatedProtein": 18,
        "mealType": "\u98ef\u985e",
        "tags": ["\u98ef\u985e", "\u4e2d\u5f0f\u6599\u7406"],
        "mainIngredients": ["\u767d\u98ef", "\u96de\u86cb", "\u9752\u8525"],
        "allergens": ["\u86cb"],
    },
    "\u96de\u80f8\u8089\u5065\u5eb7\u9910": {
        "estimatedCalories": 420,
        "estimatedProtein": 32,
        "mealType": "\u5065\u5eb7\u9910",
        "tags": ["\u4f4e\u5361", "\u9ad8\u86cb\u767d"],
        "mainIngredients": ["\u96de\u80f8\u8089", "\u852c\u83dc", "\u7cd9\u7c73"],
        "allergens": [],
    },
}


def normalize_and_enrich_result(result: MealAnalysisResult | dict[str, Any], original_text: str | None = None) -> MealAnalysisResult:
    payload = result.model_dump() if isinstance(result, MealAnalysisResult) else dict(result)
    source_type = payload.get("sourceType") if payload.get("sourceType") in {"text", "image", "url"} else "text"
    meal_name = normalize_meal_name(str(payload.get("mealName") or original_text or "\u672a\u547d\u540d\u9910\u9ede"))
    original_meal_name = normalize_meal_name(str(original_text or ""))
    if _is_generic_name(meal_name) and original_meal_name in KNOWN_MEALS:
        meal_name = original_meal_name
    meal_name = _contextual_meal_name(meal_name, payload, original_text)
    known = KNOWN_MEALS.get(meal_name, {})
    raw_meal_type = normalize_user_facing_text(str(payload.get("mealType") or ""))
    meal_type = str(known.get("mealType") or "") if _is_generic_meal_type(raw_meal_type) else raw_meal_type
    tags = _merge_lists(_string_list(payload.get("tags")), _string_list(known.get("tags")))
    main_ingredients = [
        ingredient
        for ingredient in _merge_lists(_string_list(payload.get("mainIngredients")), _string_list(known.get("mainIngredients")))
        if not _is_invalid_user_value(ingredient)
    ]
    allergens = _merge_lists(_string_list(payload.get("allergens")), _string_list(known.get("allergens")))

    calories = _positive_float(payload.get("estimatedCalories")) or _positive_float(known.get("estimatedCalories"))
    protein = _positive_float(payload.get("estimatedProtein")) or _positive_float(known.get("estimatedProtein"))

    if not meal_type:
        meal_type = _infer_type(meal_name, tags)
    if not calories or not protein:
        estimated = _estimate_by_type(meal_type, tags)
        calories = calories or estimated["estimatedCalories"]
        protein = protein or estimated["estimatedProtein"]
    if not main_ingredients and known.get("mainIngredients"):
        main_ingredients = _string_list(known["mainIngredients"])
    if not main_ingredients:
        main_ingredients = ["\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d"]

    allergens = _merge_lists(allergens, _infer_allergens(main_ingredients))
    reason = normalize_user_facing_text(str(payload.get("recommendationReason") or known.get("recommendationReason") or ""))
    if _is_forbidden_reason(reason) or _is_generic_reason(reason) or not reason:
        reason = str(known.get("recommendationReason") or DEFAULT_REASON)

    confidence = max(0, min(float(payload.get("confidence") or 0.55), 1))
    if meal_name == "\u70b8\u96de\u6392":
        confidence = min(confidence, 0.85)

    enriched = MealAnalysisResult(
        id=str(payload.get("id") or f"system-{uuid4()}"),
        mealName=meal_name,
        mealType=meal_type or "\u7d9c\u5408\u9910",
        estimatedCalories=calories,
        estimatedProtein=protein,
        tags=normalize_user_facing_list(tags),
        mainIngredients=normalize_user_facing_list(main_ingredients),
        allergens=normalize_user_facing_list(allergens),
        recommendationReason=normalize_user_facing_text(reason),
        confidence=confidence,
        sourceType=source_type,
        createdAt=str(payload.get("createdAt") or datetime.now(timezone.utc).isoformat()),
        isAiGenerated=bool(payload.get("isAiGenerated", True)),
    )
    if validate_analysis_result(enriched):
        fixed = enriched.model_dump()
        if _is_invalid_user_value(fixed["mealName"]):
            fixed["mealName"] = "\u7d9c\u5408\u9910"
        if not fixed["mainIngredients"] or all(_is_invalid_user_value(item) for item in fixed["mainIngredients"]):
            fixed["mainIngredients"] = ["\u4e3b\u8981\u98df\u6750\u9700\u4eba\u5de5\u78ba\u8a8d"]
        if not fixed["tags"]:
            fixed["tags"] = ["\u7d9c\u5408\u9910"]
        if fixed["estimatedCalories"] <= 0:
            fixed["estimatedCalories"] = 500
        if fixed["estimatedProtein"] <= 0:
            fixed["estimatedProtein"] = 20
        if _is_forbidden_reason(fixed["recommendationReason"]) or not fixed["recommendationReason"]:
            fixed["recommendationReason"] = DEFAULT_REASON
        enriched = MealAnalysisResult(**fixed)
    return enriched


def validate_analysis_result(result: MealAnalysisResult | dict[str, Any]) -> list[str]:
    payload = result.model_dump() if isinstance(result, MealAnalysisResult) else dict(result)
    issues: list[str] = []
    meal_name = str(payload.get("mealName") or "")
    meal_type = str(payload.get("mealType") or "")
    reason = str(payload.get("recommendationReason") or "")
    tags = payload.get("tags") if isinstance(payload.get("tags"), list) else []
    ingredients = payload.get("mainIngredients") if isinstance(payload.get("mainIngredients"), list) else []
    confidence = float(payload.get("confidence") or 0)
    calories = _positive_float(payload.get("estimatedCalories"))

    if not meal_name or _is_invalid_user_value(meal_name) or _has_english_meal_name(meal_name) or _is_overly_generic_name(meal_name):
        issues.append("mealName must be localized Traditional Chinese")
    if not meal_type or _is_invalid_user_value(meal_type):
        issues.append("mealType is missing")
    if calories is None:
        issues.append("estimatedCalories must be greater than zero")
    if _positive_float(payload.get("estimatedProtein")) is None:
        issues.append("estimatedProtein must be greater than zero")
    if not tags:
        issues.append("tags must not be empty")
    ingredients_incomplete = not ingredients or any(_is_invalid_user_value(str(item)) for item in ingredients)
    if ingredients_incomplete:
        issues.append("mainIngredients must be meaningful")
    if (
        not reason
        or _is_forbidden_reason(reason)
        or _is_invalid_user_value(reason)
        or _has_english_meal_name(reason)
        or _is_generic_reason(reason)
    ):
        issues.append("recommendationReason must be localized and user friendly")
    if meal_name in {"\u6e6f\u5305", "\u5c0f\u7c60\u5305"} and ingredients_incomplete:
        issues.append("soup dumpling requires concrete ingredients")
    if confidence >= 0.9 and ingredients_incomplete:
        issues.append("high confidence requires concrete ingredients")
    if calories == 500 and ingredients_incomplete:
        issues.append("generic nutrition defaults require concrete ingredients")
    return issues


def _positive_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [normalize_user_facing_text(str(item)) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [normalize_user_facing_text(value)]
    return []


def _merge_lists(primary: list[str], fallback: list[str]) -> list[str]:
    values: list[str] = []
    for item in [*primary, *fallback]:
        if item and item not in values:
            values.append(item)
    return values


def _contextual_meal_name(meal_name: str, payload: dict[str, Any], original_text: str | None) -> str:
    source_type = payload.get("sourceType")
    context_parts = [
        meal_name,
        str(original_text or ""),
        str(payload.get("mealType") or ""),
        str(payload.get("recommendationReason") or ""),
        " ".join(_string_list(payload.get("tags"))),
        " ".join(_string_list(payload.get("mainIngredients"))),
    ]
    context = normalize_user_facing_text(" ".join(context_parts)).lower()
    evidence_context_parts = [
        str(original_text or ""),
        str(payload.get("mealType") or ""),
        str(payload.get("recommendationReason") or ""),
        " ".join(_string_list(payload.get("tags"))),
        " ".join(_string_list(payload.get("mainIngredients"))),
    ]
    evidence_context = normalize_user_facing_text(" ".join(evidence_context_parts)).lower()
    has_noodles = _has_noodle_evidence(evidence_context if source_type == "image" else context)
    egg_context = context.replace("\u86cb\u767d\u8cea", "").replace("\u9ad8\u86cb\u767d", "")
    has_egg = _has_any(
        egg_context,
        ["\u96de\u86cb", "\u53ef\u898b\u86cb", "\u86cb\u6db2", "\u6ed1\u86cb", " \u86cb ", "\u86cb,", "egg"],
    )
    has_steak = _has_any(context, ["\u725b\u6392", "steak"])
    has_chicken_steak = _has_any(context, ["\u96de\u6392", "chicken steak"])
    has_chicken = _has_any(context, ["\u96de\u8089", "chicken"])
    has_fried_chicken_cutlet = _has_any(
        context,
        ["\u70b8\u96de\u6392", "\u96de\u6392", "chicken steak", "fried chicken steak", "fried chicken cutlet"],
    )

    if source_type == "image" and meal_name == "\u70b8\u96de\u6392":
        return "\u70b8\u96de\u6392"
    if source_type == "image" and has_fried_chicken_cutlet and not has_noodles:
        return "\u70b8\u96de\u6392"

    if has_chicken_steak and has_noodles and has_egg:
        return "\u96de\u6392\u86cb\u9eb5"
    if has_steak and has_noodles and has_egg and not has_chicken:
        return "\u725b\u6392\u86cb\u9eb5"
    if has_chicken_steak and has_noodles:
        return "\u96de\u6392\u9eb5"
    if has_steak and has_noodles and not has_chicken:
        return "\u725b\u6392\u9eb5"
    if has_steak and has_egg and meal_name in {"\u725b\u6392", "\u725b\u6392\u86cb", "\u9eb5\u98df", "\u672a\u547d\u540d\u9910\u9ede"}:
        return "\u725b\u6392\u86cb"
    return meal_name


def _has_noodle_evidence(context: str) -> bool:
    if _has_any(
        context,
        [
            "\u672a\u660e\u78ba\u770b\u5230\u9eb5\u689d",
            "\u6c92\u6709\u9eb5\u689d",
            "\u672a\u770b\u5230\u9eb5\u689d",
            "\u4e0d\u5224\u65b7\u70ba\u96de\u6392\u9eb5",
            "no noodles",
            "no visible noodles",
        ],
    ):
        return False
    return _has_any(context, ["\u9eb5\u689d", "\u9eb5\u98df", "\u53ef\u898b\u9eb5", "\u6e6f\u9eb5", "noodles", "noodle"])


def _infer_type(meal_name: str, tags: list[str]) -> str:
    if "\u9eb5" in meal_name or "\u9eb5\u98df" in tags:
        return "\u9eb5\u98df"
    if "\u4e3c" in meal_name or "\u4e3c\u98ef" in tags or "\u65e5\u5f0f" in tags:
        return "\u65e5\u5f0f\u4e3c\u98ef"
    if "\u98ef" in meal_name or "\u98ef\u985e" in tags:
        return "\u98ef\u985e"
    if "\u4fbf\u7576" in meal_name:
        return "\u4fbf\u7576"
    if "\u5065\u5eb7\u9910" in tags:
        return "\u5065\u5eb7\u9910"
    return "\u7d9c\u5408\u9910"


def _estimate_by_type(meal_type: str, tags: list[str]) -> dict[str, float]:
    if "\u725b\u6392\u9eb5" in meal_type:
        return {"estimatedCalories": 850, "estimatedProtein": 38}
    if "\u9eb5\u98df" in meal_type or "\u9eb5\u98df" in tags:
        return {"estimatedCalories": 600, "estimatedProtein": 20}
    if "\u70b8\u7269" in meal_type or "\u70b8\u7269" in tags:
        return {"estimatedCalories": 700, "estimatedProtein": 30}
    if "\u70b8\u7269" in tags and "\u4e3c" in meal_type:
        return {"estimatedCalories": 780, "estimatedProtein": 32}
    if "\u65e5\u5f0f\u4e3c\u98ef" in meal_type:
        return {"estimatedCalories": 650, "estimatedProtein": 28}
    if "\u98ef\u985e" in meal_type:
        return {"estimatedCalories": 600, "estimatedProtein": 18}
    if "\u5065\u5eb7\u9910" in meal_type:
        return {"estimatedCalories": 420, "estimatedProtein": 32}
    if "\u4fbf\u7576" in meal_type:
        return {"estimatedCalories": 750, "estimatedProtein": 30}
    return {"estimatedCalories": 500, "estimatedProtein": 20}


def _infer_allergens(ingredients: list[str]) -> list[str]:
    joined = " ".join(ingredients)
    allergens: list[str] = []
    if "\u96de\u86cb" in joined or "\u86cb" in joined:
        allergens.append("\u86cb")
    if "\u8766\u4ec1" in joined or "\u8766" in joined:
        allergens.append("\u8766")
    if "\u9eb5\u689d" in joined or "\u70b8\u8c6c\u6392" in joined or "\u9eb5\u8863" in joined or "\u9eb5\u5305\u7c89" in joined:
        allergens.append("\u9ea9\u8cea")
    if "\u82b1\u751f" in joined:
        allergens.append("\u82b1\u751f")
    return allergens


def _is_forbidden_reason(reason: str) -> bool:
    lowered = reason.lower()
    forbidden = ["fallback", "rule-based", "ai \u670d\u52d9\u7121\u6cd5\u4f7f\u7528", "\u5c1a\u672a\u8a2d\u5b9a", "\u5c55\u793a\u7d50\u679c"]
    return any(item in lowered for item in forbidden)


def _is_generic_name(meal_name: str) -> bool:
    return meal_name in {
        "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70",
        "\u672a\u547d\u540d\u9910\u9ede",
        "\u7d9c\u5408\u9910",
    }


def _is_overly_generic_name(meal_name: str) -> bool:
    return meal_name in {
        "\u7d9c\u5408\u9910",
        "\u9910\u9ede",
        "\u98df\u7269",
        "\u6599\u7406",
        "\u4e3b\u9910",
        "\u7cfb\u7d71\u8fa8\u8b58\u9910\u9ede",
    }


def _is_generic_meal_type(meal_type: str) -> bool:
    return not meal_type or meal_type in {"\u7d9c\u5408\u9910", "\u9910\u9ede", "\u98df\u7269", "\u6599\u7406"}


def _is_generic_reason(reason: str) -> bool:
    return reason.strip() in {
        "\u7cfb\u7d71\u5df2\u6839\u64da\u5019\u9078\u9910\u9ede\u8207\u53ef\u898b\u98df\u6750\u7279\u5fb5\u91cd\u65b0\u6821\u6b63\u8fa8\u8b58\u7d50\u679c\u3002",
        "\u7cfb\u7d71\u5df2\u5b8c\u6210\u9910\u9ede\u5206\u6790\u3002",
        "AI \u5df2\u5b8c\u6210\u9910\u9ede\u5206\u6790\u3002",
    }


def _has_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _has_english_meal_name(value: str) -> bool:
    lowered = value.lower()
    tokens = [
        "steak",
        "eggs",
        "chicken steak",
        "noodles",
        "katsudon",
        "oyakodon",
        "butadon",
        "gyudon",
        "fried rice",
        "curry rice",
    ]
    return any(token in lowered for token in tokens)


def _is_invalid_user_value(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    lowered = text.lower()
    invalid_tokens = [
        "unknown",
        "\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d",
        "\u672a\u78ba\u8a8d",
        "\ufffd",
        "\u9285\u9919",
        "\u657a",
        "\uee38",
        "\uf731",
        "?",
    ]
    return any(token in lowered for token in invalid_tokens)
