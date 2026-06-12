import json
from pathlib import Path
from threading import Lock

from app.models import MealAnalysisResult


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MEALS_FILE = DATA_DIR / "meals.json"

_lock = Lock()


def _ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEALS_FILE.exists():
        MEALS_FILE.write_text("[]", encoding="utf-8")


def load_meals() -> list[MealAnalysisResult]:
    _ensure_data_file()
    with _lock:
        raw = json.loads(MEALS_FILE.read_text(encoding="utf-8"))
    return [MealAnalysisResult.model_validate(item) for item in raw]


def save_meals(meals: list[MealAnalysisResult]) -> None:
    _ensure_data_file()
    payload = [meal.model_dump() for meal in meals]
    with _lock:
        MEALS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def add_meal(meal: MealAnalysisResult) -> MealAnalysisResult:
    meals = load_meals()
    meals.insert(0, meal)
    save_meals(meals)
    return meal


def recommend_meals(
    health_goal: str,
    tags: list[str],
    excluded_ingredients: list[str],
    keyword: str | None,
) -> list[MealAnalysisResult]:
    normalized_keyword = (keyword or "").strip().lower()
    normalized_excluded = [item.lower() for item in excluded_ingredients]

    results: list[MealAnalysisResult] = []
    for meal in load_meals():
        searchable_text = " ".join(
            [
                meal.mealName,
                meal.mealType,
                meal.recommendationReason,
                *meal.tags,
                *meal.mainIngredients,
                *meal.allergens,
            ],
        ).lower()
        matches_goal = _matches_health_goal(meal, health_goal)
        matches_tags = all(tag in meal.tags for tag in tags)
        avoids_excluded = all(
            excluded not in [allergen.lower() for allergen in meal.allergens]
            and excluded not in [ingredient.lower() for ingredient in meal.mainIngredients]
            for excluded in normalized_excluded
        )
        matches_keyword = not normalized_keyword or normalized_keyword in searchable_text

        if matches_goal and matches_tags and avoids_excluded and matches_keyword:
            results.append(meal)

    return results


def _matches_health_goal(meal: MealAnalysisResult, health_goal: str) -> bool:
    if not health_goal:
        return True
    profile = " ".join([meal.mealName, meal.mealType, *meal.tags])
    is_risky = any(token in profile for token in ["甜點", "高糖", "炸物", "油炸", "高脂肪"])
    if health_goal == "減脂":
        return not is_risky and (
            meal.estimatedCalories <= 500 or "低卡" in meal.tags or "低脂" in meal.tags
        )
    if health_goal == "增肌":
        return meal.estimatedProtein >= 25 or "高蛋白" in meal.tags
    if health_goal == "均衡飲食":
        return not is_risky and ("健康餐" in meal.tags or meal.estimatedProtein >= 15)
    if health_goal == "健康維持":
        return not is_risky and (
            "健康餐" in meal.tags or "低脂" in meal.tags or meal.estimatedCalories <= 550
        )
    return True
