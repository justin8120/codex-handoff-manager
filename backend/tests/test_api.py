from fastapi.testclient import TestClient

from app.main import app
from app.models import MealAnalysisResult
from app.services.ai_provider import normalize_meal_name
from app.services.nutrition_enricher import (
    calibrate_confidence,
    infer_recommendation_labels,
    load_recommendation_categories,
    normalize_and_enrich_result,
    validate_analysis_result,
)
from app.services.openai_meal_analyzer import classify_text_hint
from app.services.web_food_verifier import rerank_food_candidates
from app.storage import meals_store


client = TestClient(app)


def meal_fixture(
    name: str,
    tags: list[str] | None = None,
    ingredients: list[str] | None = None,
    allergens: list[str] | None = None,
    reason: str = "\u6e2c\u8a66\u7528\u9910\u9ede\u3002",
) -> MealAnalysisResult:
    return MealAnalysisResult(
        id=f"test-{name}",
        mealName=name,
        mealType="\u6e2c\u8a66\u9910",
        estimatedCalories=500,
        estimatedProtein=25,
        tags=tags or ["\u5065\u5eb7\u9910"],
        mainIngredients=ingredients or ["\u767d\u98ef", "\u852c\u83dc"],
        allergens=allergens or [],
        recommendationReason=reason,
        confidence=0.7,
        sourceType="text",
        createdAt="2026-06-12T00:00:00+00:00",
        isAiGenerated=False,
        recommendedGoals=["\u5747\u8861\u98f2\u98df"],
    )


def test_normalize_meal_name_maps_romanized_names():
    assert normalize_meal_name("Katsudon") == "\u8c6c\u6392\u4e3c"
    assert normalize_meal_name("Oyakodon") == "\u89aa\u5b50\u4e3c"
    assert normalize_meal_name("Butadon") == "\u8c5a\u4e3c"
    assert normalize_meal_name("\u8c5a\u4e95") == "\u8c5a\u4e3c"
    assert normalize_meal_name("Gyudon") == "\u725b\u4e3c"
    assert normalize_meal_name("Tendon") == "\u5929\u4e3c"
    assert normalize_meal_name("Curry Rice") == "\u5496\u54e9\u98ef"
    assert normalize_meal_name("Fried Rice") == "\u7092\u98ef"


def test_classify_text_hint_treats_single_peanut_as_weak_hint():
    hint = classify_text_hint("\u82b1\u751f")

    assert hint["weakHint"] == "\u82b1\u751f"
    assert hint["explicitMealName"] is None
    assert hint["isExplicitOverride"] is False


def test_classify_text_hint_detects_explicit_override():
    hint = classify_text_hint("\u9019\u662f\u82b1\u751f")

    assert hint["explicitMealName"] == "\u82b1\u751f"
    assert hint["weakHint"] is None
    assert hint["isExplicitOverride"] is True


def test_validate_analysis_result_flags_english_meal_name():
    issues = validate_analysis_result(
        {
            "mealName": "Steak and Eggs",
            "mealType": "\u86cb\u767d\u8cea\u9910",
            "estimatedCalories": 700,
            "estimatedProtein": 42,
            "tags": ["\u725b\u8089"],
            "mainIngredients": ["\u725b\u6392", "\u96de\u86cb"],
            "allergens": ["\u86cb"],
            "recommendationReason": "Steak and Eggs detected from image.",
        },
    )

    assert any("mealName" in issue for issue in issues)


def test_validate_analysis_result_flags_invalid_ingredients():
    issues = validate_analysis_result(
        {
            "mealName": "\u7d9c\u5408\u9910",
            "mealType": "\u7d9c\u5408\u9910",
            "estimatedCalories": 500,
            "estimatedProtein": 20,
            "tags": ["\u7d9c\u5408\u9910"],
            "mainIngredients": ["unknown"],
            "allergens": [],
            "recommendationReason": "\u7cfb\u7d71\u5df2\u5b8c\u6210\u9910\u9ede\u5206\u6790\u3002",
        },
    )

    assert any("mainIngredients" in issue for issue in issues)


def test_validate_analysis_result_rejects_pending_ingredient_placeholder():
    issues = validate_analysis_result(
        {
            "mealName": "\u7591\u4f3c\u9910\u9ede",
            "mealType": "\u5f85\u78ba\u8a8d",
            "estimatedCalories": 500,
            "estimatedProtein": 20,
            "tags": ["\u5f85\u78ba\u8a8d"],
            "mainIngredients": ["\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d"],
            "allergens": [],
            "recommendationReason": "\u7cfb\u7d71\u7121\u6cd5\u5f9e\u5716\u7247\u4e2d\u7a69\u5b9a\u8fa8\u8b58\u5177\u9ad4\u9910\u9ede\u3002",
        },
    )

    assert any("mainIngredients" in issue for issue in issues)


def test_validate_analysis_result_rejects_soup_dumpling_with_incomplete_ingredients():
    issues = validate_analysis_result(
        {
            "mealName": "\u6e6f\u5305",
            "mealType": "\u4e2d\u5f0f\u9ede\u5fc3",
            "estimatedCalories": 500,
            "estimatedProtein": 20,
            "tags": ["\u4e2d\u5f0f"],
            "mainIngredients": ["\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d"],
            "allergens": [],
            "recommendationReason": "\u7cfb\u7d71\u5df2\u6839\u64da\u5019\u9078\u9910\u9ede\u8207\u53ef\u898b\u98df\u6750\u7279\u5fb5\u91cd\u65b0\u6821\u6b63\u8fa8\u8b58\u7d50\u679c\u3002",
            "confidence": 0.95,
        },
    )

    assert any("soup dumpling" in issue or "mainIngredients" in issue for issue in issues)


def test_validate_analysis_result_rejects_high_confidence_with_incomplete_ingredients():
    issues = validate_analysis_result(
        {
            "mealName": "\u7591\u4f3c\u9910\u9ede",
            "mealType": "\u5f85\u78ba\u8a8d",
            "estimatedCalories": 500,
            "estimatedProtein": 20,
            "tags": ["\u5f85\u78ba\u8a8d"],
            "mainIngredients": ["unknown"],
            "allergens": [],
            "recommendationReason": "\u7cfb\u7d71\u7121\u6cd5\u5f9e\u5716\u7247\u4e2d\u7a69\u5b9a\u8fa8\u8b58\u5177\u9ad4\u9910\u9ede\u3002",
            "confidence": 0.95,
        },
    )

    assert any("high confidence" in issue for issue in issues)


def test_validate_analysis_result_rejects_generic_recommendation_reason():
    issues = validate_analysis_result(
        {
            "mealName": "\u6e6f\u5305",
            "mealType": "\u4e2d\u5f0f\u9ede\u5fc3",
            "estimatedCalories": 380,
            "estimatedProtein": 16,
            "tags": ["\u4e2d\u5f0f", "\u9ede\u5fc3"],
            "mainIngredients": ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"],
            "allergens": ["\u9ea9\u8cea"],
            "recommendationReason": "\u7cfb\u7d71\u5df2\u6839\u64da\u5019\u9078\u9910\u9ede\u8207\u53ef\u898b\u98df\u6750\u7279\u5fb5\u91cd\u65b0\u6821\u6b63\u8fa8\u8b58\u7d50\u679c\u3002",
            "confidence": 0.8,
        },
    )

    assert any("recommendationReason" in issue for issue in issues)


def test_enrichment_normalizes_steak_and_eggs():
    result = normalize_and_enrich_result(
        {
            "id": "test-steak-eggs",
            "mealName": "Steak and Eggs",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.mealName == "\u725b\u6392\u86cb"
    assert result.estimatedCalories > 0
    assert result.estimatedProtein > 0
    assert result.mainIngredients
    assert "\u86cb" in result.allergens


def test_enrichment_fills_soup_dumpling_ingredients():
    result = normalize_and_enrich_result(
        {
            "id": "test-soup-dumpling",
            "mealName": "\u6e6f\u5305",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.estimatedCalories == 380
    assert result.estimatedProtein == 16
    assert result.mainIngredients == ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"]
    assert "\u9ea9\u8cea" in result.allergens


def test_enrichment_fills_butadon_nutrition_when_values_are_zero():
    result = normalize_and_enrich_result(
        {
            "id": "test-butadon",
            "mealName": "\u8c5a\u4e3c",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.mealName == "\u8c5a\u4e3c"
    assert result.estimatedCalories > 0
    assert result.estimatedProtein > 0
    assert result.mainIngredients
    assert "\u86cb" in result.allergens


def test_enrichment_fills_katsudon_nutrition_ingredients_and_allergens():
    result = normalize_and_enrich_result(
        {
            "id": "test-katsudon",
            "mealName": "Katsudon",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.mealName == "\u8c6c\u6392\u4e3c"
    assert result.estimatedCalories > 0
    assert result.estimatedProtein > 0
    assert result.mainIngredients
    assert "\u86cb" in result.allergens or "\u9ea9\u8cea" in result.allergens


def test_enrichment_normalizes_chicken_steak_with_noodles():
    result = normalize_and_enrich_result(
        {
            "id": "test-chicken-noodles",
            "mealName": "Chicken steak with noodles",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.mealName == "\u70b8\u96de\u6392"
    assert result.estimatedCalories > 0
    assert result.estimatedProtein > 0
    assert result.mainIngredients
    assert "\u9ea9\u8cea" in result.allergens


def test_enrichment_caps_fried_chicken_cutlet_confidence_and_warns_about_oil():
    result = normalize_and_enrich_result(
        {
            "id": "test-fried-chicken",
            "mealName": "\u70b8\u96de\u6392",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 1.0,
            "sourceType": "image",
            "createdAt": "2026-06-12T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.mealName == "\u70b8\u96de\u6392"
    assert result.confidence <= 0.85
    assert result.estimatedCalories == 600
    assert result.estimatedProtein == 35
    assert result.mainIngredients == ["\u96de\u8089", "\u9eb5\u8863", "\u6cb9"]
    assert "\u6cb9\u8102" in result.recommendationReason
    assert "\u5065\u5eb7\u7dad\u6301" not in result.recommendedGoals
    assert "\u5747\u8861\u98f2\u98df" not in result.recommendedGoals
    assert "\u6e1b\u8102" not in result.recommendedGoals
    assert "\u589e\u808c" in result.recommendedGoals or "\u9ad8\u86cb\u767d\u88dc\u5145" in result.recommendedGoals
    assert "\u5076\u723e\u4eab\u7528" in result.recommendedGoals or "\u6cb9\u70b8\u63d0\u9192" in result.recommendedGoals


def test_enrichment_assigns_treat_goals_for_cinnamon_swirl():
    result = normalize_and_enrich_result(
        {
            "id": "test-cinnamon",
            "mealName": "\u8089\u6842\u6372",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.55,
            "sourceType": "url",
            "createdAt": "2026-06-12T00:00:00+00:00",
            "isAiGenerated": True,
        },
        original_text="cinnamon-swirl",
    )

    assert "\u751c\u9ede" in result.tags or "\u70d8\u7119" in result.tags
    assert "\u6e1b\u8102" not in result.recommendedGoals
    assert "\u5065\u5eb7\u7dad\u6301" not in result.recommendedGoals
    assert "\u5747\u8861\u98f2\u98df" not in result.recommendedGoals
    assert "\u5076\u723e\u4eab\u7528" in result.recommendedGoals
    assert "\u9ad8\u7cd6\u63d0\u9192" in result.recommendedGoals


def test_confidence_calibration_caps_incomplete_ingredients():
    confidence = calibrate_confidence(
        {
            "mealName": "\u70e4\u96de\u80f8\u8089\u98ef",
            "mealType": "\u98ef\u985e",
            "estimatedCalories": 600,
            "estimatedProtein": 18,
            "tags": ["\u9ad8\u86cb\u767d"],
            "mainIngredients": ["\u4e3b\u8981\u98df\u6750\u9700\u4eba\u5de5\u78ba\u8a8d"],
            "recommendationReason": "\u521d\u6b65\u4f30\u7b97\u7d50\u679c\u3002",
            "confidence": 0.8,
            "sourceType": "url",
        },
        source_type="url",
    )

    assert confidence <= 0.45


def test_confidence_calibration_caps_fallback_results():
    confidence = calibrate_confidence(
        {
            "id": "system-test",
            "mealName": "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70",
            "mealType": "\u5065\u5eb7\u9910",
            "estimatedCalories": 420,
            "estimatedProtein": 32,
            "tags": ["\u4f4e\u5361", "\u9ad8\u86cb\u767d"],
            "mainIngredients": ["\u96de\u80f8\u8089", "\u852c\u83dc", "\u7cd9\u7c73"],
            "recommendationReason": "\u7cfb\u7d71\u5df2\u6839\u64da\u8f38\u5165\u5167\u5bb9\u63d0\u4f9b\u9910\u9ede\u5065\u5eb7\u5efa\u8b70\u3002",
            "confidence": 0.9,
            "sourceType": "text",
        },
        source_type="text",
        used_fallback=True,
    )

    assert confidence <= 0.55


def test_enrichment_uses_visual_context_for_steak_egg_noodles():
    result = normalize_and_enrich_result(
        {
            "id": "test-steak-egg-noodles",
            "mealName": "Steak and Eggs",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.7,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
        original_text="visible steak, noodles, egg, greens and soup",
    )

    assert result.mealName == "\u725b\u6392\u86cb\u9eb5"
    assert result.estimatedCalories > 0
    assert result.estimatedProtein > 0
    assert "\u9eb5\u689d" in result.mainIngredients
    assert "\u9ea9\u8cea" in result.allergens


def test_enrichment_uses_original_text_when_result_name_is_generic():
    result = normalize_and_enrich_result(
        {
            "id": "test-generic",
            "mealName": "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70",
            "mealType": "",
            "estimatedCalories": 0,
            "estimatedProtein": 0,
            "tags": [],
            "mainIngredients": [],
            "allergens": [],
            "recommendationReason": "",
            "confidence": 0.4,
            "sourceType": "text",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
        original_text="Chicken steak with noodles",
    )

    assert result.mealName == "\u96de\u6392\u9eb5"
    assert result.estimatedCalories == 850
    assert result.estimatedProtein == 38


def test_health_reports_backend_status(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["aiProvider"] == "mock"
    assert payload["aiConfigured"] is True
    assert payload["fallbackEnabled"] is True


def test_get_meals_returns_seed_dataset():
    response = client.get("/api/meals")

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "\u96de\u80f8\u8089\u4fbf\u7576" in names
    assert "\u8336\u8449\u86cb" in names
    assert "\u6d77\u9bae\u7ca5" in names


def test_recommend_excludes_seafood():
    response = client.post(
        "/api/recommend",
        json={
            "healthGoal": "\u5747\u8861\u98f2\u98df",
            "tags": [],
            "excludedIngredients": ["\u6d77\u9bae"],
            "keyword": None,
        },
    )

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "\u6d77\u9bae\u7ca5" not in names
    assert "\u9bad\u9b5a\u6c99\u62c9" not in names
    assert "\u8c46\u8150\u852c\u83dc\u7897" in names


def test_mock_provider_identifies_shrimp_fried_rice(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post("/api/analyze/text", json={"description": "\u8766\u4ec1\u7092\u98ef"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u8766\u4ec1\u7092\u98ef"
    assert payload["mealType"] == "\u98ef\u985e"
    assert payload["estimatedCalories"] == 650
    assert payload["estimatedProtein"] == 22
    assert payload["tags"] == ["\u98ef\u985e", "\u6d77\u9bae", "\u4e2d\u5f0f\u6599\u7406"]
    assert payload["mainIngredients"] == [
        "\u8766\u4ec1",
        "\u767d\u98ef",
        "\u96de\u86cb",
        "\u9752\u8525",
    ]
    assert payload["allergens"] == ["\u8766", "\u86cb"]
    assert payload["confidence"] <= 0.55
    assert "fallback" not in payload["recommendationReason"]
    assert "AI \u670d\u52d9\u7121\u6cd5\u4f7f\u7528" not in payload["recommendationReason"]


def test_mock_provider_identifies_generic_fried_rice(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post("/api/analyze/text", json={"description": "\u852c\u83dc\u7092\u98ef"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u7092\u98ef"
    assert payload["mealType"] == "\u98ef\u985e"
    assert payload["estimatedCalories"] == 620
    assert payload["estimatedProtein"] == 18
    assert payload["tags"] == ["\u98ef\u985e", "\u4e2d\u5f0f\u6599\u7406"]
    assert payload["mainIngredients"] == ["\u767d\u98ef", "\u96de\u86cb", "\u9752\u8525"]
    assert payload["allergens"] == ["\u86cb"]
    assert payload["confidence"] <= 0.55


def test_mock_provider_normalizes_ton_i_text_hint_to_butadon(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post("/api/analyze/text", json={"description": "\u7bc4\u4f8b\u7167\u7247\uff1a\u8c5a\u4e95"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u8c5a\u4e3c"
    assert payload["mealType"] == "\u65e5\u5f0f\u4e3c\u98ef"
    assert payload["estimatedCalories"] == 650
    assert payload["estimatedProtein"] == 28
    assert payload["tags"] == ["\u65e5\u5f0f", "\u4e3c\u98ef", "\u8c6c\u8089"]
    assert payload["mainIngredients"] == ["\u767d\u98ef", "\u8c6c\u8089\u7247", "\u96de\u86cb", "\u6d77\u82d4"]
    assert payload["allergens"] == ["\u86cb"]
    assert payload["confidence"] <= 0.55


def test_analyze_image_with_text_hint_ton_i_normalizes_to_butadon(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        files={"file": ("\u8c5a\u4e95.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u8c5a\u4e3c"
    assert payload["sourceType"] == "image"
    assert "\u89aa\u5b50\u4e3c" in payload["recommendationReason"]


def test_analyze_image_with_xiaolongbao_hint_uses_text_before_uncertain_fallback(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"description": "\u5c0f\u7c60\u5305"},
        files={"file": ("images.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u5c0f\u7c60\u5305"
    assert payload["estimatedCalories"] == 380
    assert payload["estimatedProtein"] == 16
    assert payload["mealType"] == "\u4e2d\u5f0f\u9ede\u5fc3"
    assert payload["tags"] == ["\u4e2d\u5f0f", "\u9ede\u5fc3", "\u9eb5\u98df"]
    assert payload["mainIngredients"] == ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"]
    assert payload["allergens"] == ["\u9ea9\u8cea"]
    assert "\u5c0f\u7c60\u5305" in payload["recommendationReason"]
    assert "\u9eb5\u76ae" in payload["recommendationReason"]


def test_analyze_image_accepts_text_hint_field(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"text": "\u5c0f\u7c60\u5305"},
        files={"file": ("images.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["mealName"] == "\u5c0f\u7c60\u5305"


def test_image_result_keeps_soup_dumpling_when_text_hint_is_weak_peanut(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u53ef\u898b\u9eb5\u76ae\u3001\u8089\u9921\u3001\u6e6f\u6c41\u8207\u84b8\u7c60",
            "candidates": [
                {
                    "name": "\u5c0f\u7c60\u5305",
                    "confidence": 0.82,
                    "evidence": ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41", "\u84b8\u7c60"],
                },
                {
                    "name": "\u82b1\u751f",
                    "confidence": 0.2,
                    "evidence": ["\u4f7f\u7528\u8005\u6587\u5b57\u63d0\u793a"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        data={"text": "\u82b1\u751f"},
        files={"file": ("\u6e6f\u5305.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] != "\u82b1\u751f"
    assert payload["mealName"] in {"\u5c0f\u7c60\u5305", "\u6e6f\u5305"}
    assert payload["mainIngredients"] == ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"]
    assert "\u9ea9\u8cea" in payload["allergens"]
    assert "\u672a\u8986\u84cb\u5716\u7247\u8fa8\u8b58\u7d50\u679c" in payload["recommendationReason"]


def test_explicit_peanut_hint_can_override_uncertain_image(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"text": "\u9019\u662f\u82b1\u751f"},
        files={"file": ("unclear.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u82b1\u751f"
    assert payload["mainIngredients"] == ["\u82b1\u751f"]
    assert "\u82b1\u751f" in payload["allergens"]


def test_peanut_allergy_hint_does_not_rename_soup_dumpling(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u53ef\u898b\u9eb5\u76ae\u3001\u8089\u9921\u3001\u6e6f\u6c41\u8207\u84b8\u7c60",
            "candidates": [
                {
                    "name": "\u6e6f\u5305",
                    "confidence": 0.8,
                    "evidence": ["\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41", "\u84b8\u7c60"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        data={"text": "\u82b1\u751f\u904e\u654f"},
        files={"file": ("\u6e6f\u5305.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] != "\u82b1\u751f"
    assert payload["mealName"] in {"\u5c0f\u7c60\u5305", "\u6e6f\u5305"}
    assert "\u9ea9\u8cea" in payload["allergens"]
    assert "\u82b1\u751f" in payload["allergens"]
    assert "\u82b1\u751f\u9650\u5236" in payload["recommendationReason"]


def test_analyze_image_with_english_soup_dumplings_hint_uses_xiaolongbao(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"description": "soup dumplings"},
        files={"file": ("images.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["mealName"] == "\u5c0f\u7c60\u5305"


def test_analyze_image_with_peanut_hint_uses_peanut(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"text": "\u82b1\u751f"},
        files={"file": ("\u82b1\u751f\u71df\u990a\u6210\u5206.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u82b1\u751f"
    assert payload["mealName"] != "\u7591\u4f3c\u9910\u9ede"
    assert payload["mealType"] == "\u5805\u679c / \u8c46\u985e\u98df\u6750"
    assert payload["estimatedCalories"] == 567
    assert payload["estimatedProtein"] == 26
    assert payload["mainIngredients"] == ["\u82b1\u751f"]
    assert "\u82b1\u751f" in payload["allergens"]
    assert payload["confidence"] <= 0.55


def test_analyze_image_with_watermelon_hint_uses_watermelon(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        data={"description": "watermelon"},
        files={"file": ("images.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u897f\u74dc"
    assert payload["estimatedCalories"] == 30
    assert payload["mainIngredients"] == ["\u897f\u74dc"]


def test_single_ingredient_result_passes_validation():
    result = normalize_and_enrich_result(
        {
            "id": "test-peanut",
            "mealName": "\u82b1\u751f",
            "mealType": "\u5805\u679c / \u8c46\u985e\u98df\u6750",
            "estimatedCalories": 567,
            "estimatedProtein": 26,
            "tags": ["\u5805\u679c", "\u9ad8\u86cb\u767d", "\u9ad8\u8102\u80aa"],
            "mainIngredients": ["\u82b1\u751f"],
            "allergens": ["\u82b1\u751f"],
            "recommendationReason": (
                "\u7cfb\u7d71\u6839\u64da\u4f7f\u7528\u8005\u63d0\u4f9b\u7684\u6587\u5b57\u63cf\u8ff0"
                "\u5224\u65b7\u6b64\u9805\u76ee\u70ba\u82b1\u751f\u3002"
            ),
            "confidence": 0.9,
            "sourceType": "image",
            "createdAt": "2026-06-06T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert validate_analysis_result(result) == []


def test_rerank_prefers_butadon_when_pork_slices_are_visible(monkeypatch):
    monkeypatch.setenv("WEB_VERIFY_MAX_CANDIDATES", "5")
    candidates = [
        {
            "name": "\u8c5a\u4e3c",
            "confidence": 0.72,
            "evidence": [
                "\u53ef\u898b\u8c6c\u8089\u7247",
                "\u767d\u98ef",
                "\u86cb\u6db2\u6216\u6ed1\u86cb",
                "\u6d77\u82d4\u7d72",
            ],
        },
        {
            "name": "\u89aa\u5b50\u4e3c",
            "confidence": 0.58,
            "evidence": ["\u53ef\u898b\u86cb", "\u767d\u98ef", "\u65e5\u5f0f\u4e3c\u98ef\u5916\u89c0"],
        },
    ]

    result = rerank_food_candidates(
        candidates,
        "\u53ef\u898b\u5927\u7247\u8c6c\u8089\u7247\u8986\u84cb\u767d\u98ef\uff0c\u672a\u898b\u660e\u78ba\u96de\u8089\u584a",
    )

    assert result["verifiedName"] == "\u8c5a\u4e3c"
    assert result["confidence"] >= 0.65
    assert result["rejectedCandidates"][0]["name"] == "\u89aa\u5b50\u4e3c"
    assert "\u8c5a\u4e3c" in result["reason"]


def test_rerank_does_not_prefer_katsudon_without_cutlet_evidence(monkeypatch):
    monkeypatch.setenv("WEB_VERIFY_MAX_CANDIDATES", "5")
    candidates = [
        {
            "name": "Katsudon",
            "confidence": 0.78,
            "evidence": ["egg", "rice", "nori"],
        },
        {
            "name": "Butadon",
            "confidence": 0.66,
            "evidence": ["pork slices", "rice", "egg"],
        },
        {
            "name": "Oyakodon",
            "confidence": 0.62,
            "evidence": ["egg", "rice"],
        },
    ]

    result = rerank_food_candidates(
        candidates,
        "large pork slices over rice with egg and nori, no visible fried pork cutlet or breading",
    )

    assert result["verifiedName"] == "\u8c5a\u4e3c"
    assert result["verifiedName"] != "\u8c6c\u6392\u4e3c"
    assert all(candidate["name"] != "Katsudon" for candidate in result["rejectedCandidates"])


def test_analyze_image_does_not_500_when_web_verification_fails(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u53ef\u898b\u8c6c\u8089\u7247\u8207\u767d\u98ef",
            "candidates": [
                {
                    "name": "\u8c5a\u4e3c",
                    "confidence": 0.7,
                    "evidence": ["\u53ef\u898b\u8c6c\u8089\u7247", "\u767d\u98ef"],
                },
                {
                    "name": "\u89aa\u5b50\u4e3c",
                    "confidence": 0.62,
                    "evidence": ["\u53ef\u898b\u86cb\u8207\u767d\u98ef"],
                },
            ],
        }

    def fail_verification(candidates, visual_description):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)
    monkeypatch.setattr(openai_meal_analyzer.web_food_verifier, "verify_food_candidates", fail_verification)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["mealName"] == "\u8c5a\u4e3c"


def test_unrecognized_image_fallback_uses_low_confidence_without_pending_placeholder(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u7591\u4f3c\u9910\u9ede"
    assert payload["confidence"] <= 0.4
    assert "\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d" not in payload["mainIngredients"]


def test_analyze_image_rejects_soup_dumpling_guess_without_visual_evidence(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u5716\u7247\u4e2d\u9910\u9ede\u7279\u5fb5\u4e0d\u660e\u986f",
            "candidates": [
                {
                    "name": "\u6e6f\u5305",
                    "confidence": 0.95,
                    "evidence": ["\u9910\u9ede\u5916\u89c0\u4e0d\u660e\u78ba"],
                },
            ],
        }

    def fail_retry(*args, **kwargs):
        raise RuntimeError("retry unavailable")

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)
    monkeypatch.setattr(openai_meal_analyzer, "_retry_image_correction", fail_retry)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u7591\u4f3c\u9910\u9ede"
    assert payload["confidence"] <= 0.4
    assert "\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d" not in payload["mainIngredients"]


def test_analyze_image_katsudon_result_is_enriched(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u53ef\u898b\u70b8\u8c6c\u6392\u3001\u9eb5\u8863\u3001\u96de\u86cb\u8207\u767d\u98ef",
            "candidates": [
                {
                    "name": "Katsudon",
                    "confidence": 0.84,
                    "evidence": ["fried pork cutlet", "breading", "egg", "rice"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("katsudon.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u8c6c\u6392\u4e3c"
    assert payload["estimatedCalories"] > 0
    assert payload["estimatedProtein"] > 0
    assert payload["mainIngredients"]
    assert "\u86cb" in payload["allergens"] or "\u9ea9\u8cea" in payload["allergens"]


def test_analyze_image_english_meal_name_is_translated_and_enriched(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "Chicken steak with noodles, greens and soup",
            "candidates": [
                {
                    "name": "Chicken steak with noodles",
                    "confidence": 0.82,
                    "evidence": ["chicken steak", "noodles", "greens"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u96de\u6392\u9eb5"
    assert payload["estimatedCalories"] > 0
    assert payload["estimatedProtein"] > 0
    assert payload["mainIngredients"]
    assert "\u9ea9\u8cea" in payload["allergens"]


def test_analyze_image_chicken_steak_without_noodle_evidence_returns_fried_cutlet(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u5716\u7247\u4e2d\u53ef\u898b\u5927\u578b\u88f9\u7c89\u6cb9\u70b8\u96de\u6392",
            "candidates": [
                {
                    "name": "Chicken steak",
                    "confidence": 0.82,
                    "evidence": ["fried chicken cutlet", "breading", "golden crust"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("fried-chicken.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u70b8\u96de\u6392"
    assert payload["mealType"] == "\u70b8\u7269 / \u5c0f\u5403"
    assert payload["estimatedCalories"] == 600
    assert payload["estimatedProtein"] == 35
    assert payload["mainIngredients"] == ["\u96de\u8089", "\u9eb5\u8863", "\u6cb9"]
    assert "\u9eb5\u689d" not in payload["mainIngredients"]
    assert "\u9ad8\u6e6f" not in payload["mainIngredients"]
    assert "\u9752\u83dc" not in payload["mainIngredients"]
    assert "\u4e0d\u5224\u65b7\u70ba\u96de\u6392\u9eb5" in payload["recommendationReason"]


def test_analyze_image_chicken_steak_with_noodles_name_without_evidence_is_corrected(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "\u5716\u7247\u4e2d\u53ea\u770b\u5230\u88f9\u7c89\u6cb9\u70b8\u96de\u6392",
            "candidates": [
                {
                    "name": "Chicken steak with noodles",
                    "confidence": 0.84,
                    "evidence": ["fried chicken cutlet", "breading", "crispy crust"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("fried-chicken.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u70b8\u96de\u6392"
    assert "\u9eb5\u689d" not in payload["mainIngredients"]
    assert "\u9ad8\u6e6f" not in payload["mainIngredients"]


def test_analyze_image_keeps_chicken_steak_noodles_when_noodle_evidence_exists(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "fried chicken steak with visible noodles and soup",
            "candidates": [
                {
                    "name": "Chicken steak with noodles",
                    "confidence": 0.84,
                    "evidence": ["fried chicken cutlet", "noodles", "soup"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("chicken-noodles.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u96de\u6392\u9eb5"
    assert "\u9eb5\u689d" in payload["mainIngredients"]


def test_analyze_image_steak_and_eggs_uses_evidence_for_chinese_noodle_result(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("WEB_VERIFY_ENABLED", "false")

    def fake_candidate_completion(provider_name, text, image_url):
        return {
            "visualDescription": "Steak, egg, noodles, greens and soup are visible",
            "candidates": [
                {
                    "name": "Steak and Eggs",
                    "confidence": 0.82,
                    "evidence": ["steak", "egg", "noodles", "greens"],
                },
            ],
        }

    monkeypatch.setattr(openai_meal_analyzer, "_call_image_candidate_completion", fake_candidate_completion)

    response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u725b\u6392\u86cb\u9eb5"
    assert "Steak" not in payload["mealName"]
    assert "Eggs" not in payload["mealName"]
    assert payload["estimatedCalories"] > 0
    assert payload["estimatedProtein"] > 0
    assert payload["mainIngredients"]
    assert "\u9ea9\u8cea" in payload["allergens"]


def test_analyze_endpoints_never_return_zero_nutrition(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    async def fake_fetch_url_summary(url):
        return "Chicken steak with noodles menu page"

    monkeypatch.setattr(openai_meal_analyzer, "fetch_url_summary", fake_fetch_url_summary)

    text_response = client.post("/api/analyze/text", json={"description": "Chicken steak with noodles"})
    image_response = client.post(
        "/api/analyze/image",
        files={"file": ("Chicken steak with noodles.jpg", b"fake-image", "image/jpeg")},
    )
    url_response = client.post("/api/analyze/url", json={"url": "https://example.com/menu"})

    for response in [text_response, image_response, url_response]:
        assert response.status_code == 200
        payload = response.json()
        assert payload["estimatedCalories"] > 0
        assert payload["estimatedProtein"] > 0
        assert payload["mainIngredients"]


def test_analyze_url_keeps_url_source_type_and_caps_incomplete_result(monkeypatch):
    from app.services import openai_meal_analyzer

    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    async def fake_fetch_url_summary(url):
        return "Title: menu\nPage text: \u70e4\u96de\u80f8\u8089\u98ef"

    def fake_chat_completion(provider_name, text, source_type, image_url):
        return normalize_and_enrich_result(
            {
                "id": "fake-url",
                "mealName": "\u70e4\u96de\u80f8\u8089\u98ef",
                "mealType": "\u98ef\u985e",
                "estimatedCalories": 600,
                "estimatedProtein": 18,
                "tags": ["\u9ad8\u86cb\u767d"],
                "mainIngredients": ["\u4e3b\u8981\u98df\u6750\u9700\u4eba\u5de5\u78ba\u8a8d"],
                "allergens": [],
                "recommendationReason": "\u6587\u5b57\u63cf\u8ff0\u300c\u5c0f\u7c60\u5305\u300d\u50c5\u4f5c\u70ba\u8f14\u52a9\u63d0\u793a\u3002",
                "confidence": 0.8,
                "sourceType": "image",
                "createdAt": "2026-06-12T00:00:00+00:00",
                "isAiGenerated": True,
            },
            original_text="menu",
        )

    monkeypatch.setattr(openai_meal_analyzer, "fetch_url_summary", fake_fetch_url_summary)
    monkeypatch.setattr(openai_meal_analyzer, "_call_chat_completion", fake_chat_completion)

    response = client.post("/api/analyze/url", json={"url": "https://example.com/menu"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceType"] == "url"
    assert payload["confidence"] <= 0.45
    assert "\u5c0f\u7c60\u5305" not in payload["recommendationReason"]
    assert "\u7121\u6cd5\u5b8c\u6574\u89e3\u6790" in payload["recommendationReason"]


def test_analyze_url_fetch_failure_uses_low_confidence(monkeypatch):
    from app.services import openai_meal_analyzer
    import httpx

    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    async def fail_fetch_url_summary(url):
        raise httpx.HTTPError("network unavailable")

    monkeypatch.setattr(openai_meal_analyzer, "fetch_url_summary", fail_fetch_url_summary)

    response = client.post("/api/analyze/url", json={"url": "https://example.com/menu"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceType"] == "url"
    assert payload["confidence"] <= 0.35
    assert payload["mealName"] != "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70"
    assert "\u96de\u80f8\u8089" not in payload["mainIngredients"]


def test_analyze_url_uses_mcdonalds_cinnamon_swirl_slug(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/url",
        json={"url": "https://www.mcdonalds.com/tw/zh-tw/product/cinnamon-swirl.html"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u8089\u6842\u6372"
    assert payload["sourceType"] == "url"
    assert payload["mealName"] != "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70"
    assert "\u96de\u80f8\u8089" not in payload["mainIngredients"]
    assert "\u7cd9\u7c73" not in payload["mainIngredients"]
    assert "\u725b\u8089" not in payload["mainIngredients"]
    assert "\u751c\u9ede" in payload["tags"] or "\u70d8\u7119" in payload["tags"]
    assert payload["confidence"] <= 0.75
    assert "\u6e1b\u8102" not in payload["recommendedGoals"]
    assert "\u5065\u5eb7\u7dad\u6301" not in payload["recommendedGoals"]
    assert "\u5747\u8861\u98f2\u98df" not in payload["recommendedGoals"]
    assert "\u5076\u723e\u4eab\u7528" in payload["recommendedGoals"] or "\u9ad8\u7cd6\u63d0\u9192" in payload["recommendedGoals"]


def test_recommendation_categories_are_data_driven():
    categories = load_recommendation_categories()

    assert any(category["label"] == "\u5076\u723e\u4eab\u7528" for category in categories)
    labels = infer_recommendation_labels(
        "\u81ea\u8a02\u751c\u9ede",
        "\u751c\u9ede",
        ["\u751c\u9ede", "\u9ad8\u7cd6"],
        350,
        5,
    )
    assert "\u5076\u723e\u4eab\u7528" in labels
    assert "\u9ad8\u7cd6\u63d0\u9192" in labels


def test_analyze_source_types_remain_distinct(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    text_response = client.post("/api/analyze/text", json={"description": "\u8336\u8449\u86cb"})
    image_response = client.post(
        "/api/analyze/image",
        files={"file": ("meal.jpg", b"fake-image", "image/jpeg")},
    )

    assert text_response.status_code == 200
    assert image_response.status_code == 200
    assert text_response.json()["sourceType"] == "text"
    assert image_response.json()["sourceType"] == "image"


def test_mock_provider_applies_bento_chicken_beef_and_peanut_rules(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/text",
        json={
            "description": (
                "\u96de\u80f8\u4fbf\u7576 \u725b\u8089 "
                "\u4e0d\u8981\u725b\u8089 \u82b1\u751f\u904e\u654f"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "\u96de\u80f8\u8089\u5065\u5eb7\u9910"
    assert payload["mealType"] == "\u4fbf\u7576"
    assert "\u4fbf\u7576" in payload["tags"]
    assert "\u9ad8\u86cb\u767d" in payload["tags"]
    assert "\u96de\u80f8\u8089" in payload["mainIngredients"]
    assert "\u725b\u8089" not in payload["mainIngredients"]
    assert "\u82b1\u751f" in payload["allergens"]
    assert "\u5df2\u6839\u64da\u9700\u6c42\u6392\u9664\u725b\u8089" in payload["recommendationReason"]


def test_fallback_response_is_ascii_escaped_json(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post("/api/analyze/text", json={"description": "\u6e1b\u8102"})

    assert response.status_code == 200
    assert b"\\u9910" in response.content
    assert b"\xe9\xa4\x90" not in response.content
    assert response.json()["mealName"] == "\u9910\u9ede\u5065\u5eb7\u5efa\u8b70"


def test_analyze_text_requires_key_when_fallback_disabled(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/api/analyze/text", json={"description": "\u8336\u8449\u86cb"})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI analysis service is not configured. Please set OPENAI_API_KEY."


def test_analyze_text_rejects_empty_description():
    response = client.post("/api/analyze/text", json={"description": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "\u6587\u5b57\u63cf\u8ff0\u4e0d\u53ef\u70ba\u7a7a\u3002"


def test_analyze_url_rejects_empty_url():
    response = client.post("/api/analyze/url", json={"url": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "\u9910\u9ede\u9023\u7d50\u4e0d\u53ef\u70ba\u7a7a\u3002"


def test_recommend_accepts_unknown_custom_tags_and_avoid_ingredients():
    response = client.post(
        "/api/recommend",
        json={
            "healthGoal": "\u5747\u8861\u98f2\u98df",
            "tags": ["\u5c11\u6cb9", "\u4f4e\u9209"],
            "excludedIngredients": ["\u4e0d\u5403\u8fa3", "\u7121\u9ea9\u8cea"],
            "keyword": None,
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_recommend_excludes_pork_synonyms(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u8c5a\u4e3c", tags=["\u65e5\u5f0f", "\u4e3c\u98ef", "\u8c6c\u8089"], ingredients=["\u767d\u98ef", "\u8c6c\u8089\u7247"]),
            meal_fixture("\u8c6c\u6392\u4e3c", ingredients=["\u767d\u98ef", "\u70b8\u8c6c\u6392"]),
            meal_fixture("\u8336\u8449\u86cb", ingredients=["\u96de\u86cb", "\u8336\u8449"]),
        ],
    )

    response = client.post(
        "/api/recommend",
        json={
            "healthGoal": "\u5747\u8861\u98f2\u98df",
            "tags": [],
            "excludedIngredients": ["\u8c6c\u8089"],
            "keyword": None,
        },
    )

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "\u8c5a\u4e3c" not in names
    assert "\u8c6c\u6392\u4e3c" not in names
    assert "\u8336\u8449\u86cb" in names


def test_recommend_excludes_beef_seafood_and_peanut_synonyms(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u725b\u4e3c", tags=["\u725b\u8089"], ingredients=["\u725b\u8089\u7247", "\u767d\u98ef"]),
            meal_fixture("\u725b\u6392", ingredients=["\u725b\u6392"]),
            meal_fixture("\u8766\u4ec1\u7092\u98ef", tags=["\u6d77\u9bae"], ingredients=["\u8766\u4ec1", "\u767d\u98ef"]),
            meal_fixture("\u82b1\u751f\u91ac\u5410\u53f8", ingredients=["\u82b1\u751f\u91ac", "\u5410\u53f8"]),
            meal_fixture("\u852c\u98df\u4fbf\u7576", ingredients=["\u8c46\u88fd\u54c1", "\u852c\u83dc"]),
        ],
    )

    beef_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u725b\u8089"], "keyword": None},
    )
    seafood_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u6d77\u9bae"], "keyword": None},
    )
    peanut_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u82b1\u751f"], "keyword": None},
    )

    beef_names = [meal["mealName"] for meal in beef_response.json()]
    seafood_names = [meal["mealName"] for meal in seafood_response.json()]
    peanut_names = [meal["mealName"] for meal in peanut_response.json()]
    assert "\u725b\u4e3c" not in beef_names
    assert "\u725b\u6392" not in beef_names
    assert "\u8766\u4ec1\u7092\u98ef" not in seafood_names
    assert "\u82b1\u751f\u91ac\u5410\u53f8" not in peanut_names


def test_recommend_excludes_land_meat_category(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u8c5a\u4e3c", tags=["\u8c6c\u8089"], ingredients=["\u767d\u98ef", "\u8c6c\u8089\u7247"]),
            meal_fixture("\u8c6c\u6392\u4e3c", tags=["\u65e5\u5f0f"], ingredients=["\u767d\u98ef", "\u70b8\u8c6c\u6392"]),
            meal_fixture("\u96de\u80f8\u8089\u4fbf\u7576", tags=["\u9ad8\u86cb\u767d"], ingredients=["\u96de\u80f8\u8089", "\u852c\u83dc"]),
            meal_fixture("\u70b8\u96de\u6392", tags=["\u70b8\u7269"], ingredients=["\u96de\u8089", "\u9eb5\u8863"]),
            meal_fixture("\u725b\u4e3c", tags=["\u725b\u8089"], ingredients=["\u725b\u8089\u7247", "\u767d\u98ef"]),
            meal_fixture("\u725b\u6392", ingredients=["\u725b\u6392"]),
            meal_fixture("\u852c\u98df\u4fbf\u7576", tags=["\u7d20\u98df"], ingredients=["\u8c46\u8150", "\u852c\u83dc"]),
        ],
    )

    response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u8089\u985e"], "keyword": None},
    )

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "\u8c5a\u4e3c" not in names
    assert "\u8c6c\u6392\u4e3c" not in names
    assert "\u96de\u80f8\u8089\u4fbf\u7576" not in names
    assert "\u70b8\u96de\u6392" not in names
    assert "\u725b\u4e3c" not in names
    assert "\u725b\u6392" not in names
    assert "\u852c\u98df\u4fbf\u7576" in names


def test_recommend_vegetarian_tag_excludes_meat_and_seafood(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u8c5a\u4e3c", tags=["\u7d20\u98df"], ingredients=["\u767d\u98ef", "\u8c6c\u8089\u7247"]),
            meal_fixture("\u96de\u80f8\u8089\u4fbf\u7576", tags=["\u7d20\u98df"], ingredients=["\u96de\u80f8\u8089", "\u852c\u83dc"]),
            meal_fixture("\u8766\u4ec1\u7092\u98ef", tags=["\u7d20\u98df"], ingredients=["\u8766\u4ec1", "\u767d\u98ef"]),
            meal_fixture("\u852c\u98df\u4fbf\u7576", tags=["\u7d20\u98df"], ingredients=["\u8c46\u8150", "\u852c\u83dc"]),
        ],
    )

    response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": ["\u7d20\u98df"], "excludedIngredients": [], "keyword": None},
    )

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "\u8c5a\u4e3c" not in names
    assert "\u96de\u80f8\u8089\u4fbf\u7576" not in names
    assert "\u8766\u4ec1\u7092\u98ef" not in names
    assert names == ["\u852c\u98df\u4fbf\u7576"]


def test_normalize_avoid_term_removes_user_condition_words():
    assert meals_store.normalize_avoid_term("\u4e0d\u5403\u8c6c\u8089") == "\u8c6c\u8089"
    assert meals_store.normalize_avoid_term("\u82b1\u751f\u904e\u654f") == "\u82b1\u751f"
    assert meals_store.normalize_avoid_term("\u7121\u9ea9\u8cea") == "\u9ea9\u8cea"
    assert meals_store.normalize_avoid_term("\u4e0d\u80fd\u5403\u9999\u83dc") == "\u9999\u83dc"
    assert meals_store.normalize_avoid_term("\u5c0d\u6d77\u9bae\u904e\u654f") == "\u6d77\u9bae"


def test_recommend_excludes_custom_constraints_without_mapping(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u9999\u83dc\u62cc\u9eb5", ingredients=["\u9eb5\u689d", "\u9999\u83dc"]),
            meal_fixture("\u829d\u9ebb\u6dbc\u9eb5", ingredients=["\u9eb5\u689d", "\u829d\u9ebb\u91ac"]),
            meal_fixture("\u8334\u9999\u70e4\u852c\u83dc", ingredients=["\u8334\u9999", "\u852c\u83dc"]),
            meal_fixture("\u6e05\u7092\u852c\u83dc", ingredients=["\u852c\u83dc"]),
        ],
    )

    cilantro_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u9999\u83dc"], "keyword": None},
    )
    sesame_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u829d\u9ebb"], "keyword": None},
    )
    fennel_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u8334\u9999"], "keyword": None},
    )

    assert "\u9999\u83dc\u62cc\u9eb5" not in [meal["mealName"] for meal in cilantro_response.json()]
    assert "\u829d\u9ebb\u6dbc\u9eb5" not in [meal["mealName"] for meal in sesame_response.json()]
    assert "\u8334\u9999\u70e4\u852c\u83dc" not in [meal["mealName"] for meal in fennel_response.json()]


def test_recommend_excludes_normalized_spicy_and_gluten_constraints(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture("\u9ebb\u8fa3\u8c46\u8150", tags=["\u8f9b\u8fa3"], ingredients=["\u8c46\u8150", "\u8fa3\u6912"]),
            meal_fixture("\u70b8\u96de\u6392", ingredients=["\u96de\u8089", "\u9eb5\u8863"]),
            meal_fixture("\u6e05\u84b8\u8c46\u8150", ingredients=["\u8c46\u8150"]),
        ],
    )

    spicy_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u4e0d\u5403\u8fa3"], "keyword": None},
    )
    gluten_response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": ["\u7121\u9ea9\u8cea"], "keyword": None},
    )

    assert "\u9ebb\u8fa3\u8c46\u8150" not in [meal["mealName"] for meal in spicy_response.json()]
    assert "\u70b8\u96de\u6392" not in [meal["mealName"] for meal in gluten_response.json()]


def test_ingredient_matches_exclusion_checks_full_food_text():
    food_text = "\u8c5a\u4e3c \u65e5\u5f0f \u4e3c\u98ef \u8c6c\u8089 \u767d\u98ef \u8c6c\u8089\u7247"

    assert meals_store.ingredient_matches_exclusion(food_text, ["\u8c6c\u8089"])
    assert meals_store.ingredient_matches_exclusion(food_text, ["\u8089\u985e"])


def test_meals_dataset_has_expanded_complete_records():
    meals = meals_store.load_meals()
    ids = [meal.id for meal in meals]

    assert len(meals) >= 100
    assert len(ids) == len(set(ids))
    assert all(meal.mealName.strip() for meal in meals)
    assert all(meal.tags for meal in meals)
    assert all(meal.mainIngredients for meal in meals)
    assert all(meal.recommendationReason.strip() for meal in meals)
    assert all("\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d" not in meal.mainIngredients for meal in meals)
    assert all("\u4e3b\u8981\u98df\u6750\u9700\u4eba\u5de5\u78ba\u8a8d" not in meal.mainIngredients for meal in meals)


def test_dataset_soup_dumpling_is_complete():
    soup_dumplings = [meal for meal in meals_store.load_meals() if meal.mealName in {"\u6e6f\u5305", "\u5c0f\u7c60\u5305"}]

    assert soup_dumplings
    for meal in soup_dumplings:
        assert {"\u9eb5\u76ae", "\u8c6c\u8089\u9921", "\u6e6f\u6c41"}.intersection(meal.mainIngredients)
        assert meals_store.is_complete_meal(meal)


def test_recommend_filters_incomplete_meals(monkeypatch):
    monkeypatch.setattr(
        meals_store,
        "load_meals",
        lambda: [
            meal_fixture(
                "\u6e6f\u5305",
                tags=["\u4e2d\u5f0f"],
                ingredients=["\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d"],
                reason="\u7cfb\u7d71\u5df2\u6839\u64da\u5019\u9078\u9910\u9ede\u8207\u53ef\u898b\u98df\u6750\u7279\u5fb5\u91cd\u65b0\u6821\u6b63\u8fa8\u8b58\u7d50\u679c\u3002",
            ),
            meal_fixture("\u852c\u98df\u4fbf\u7576", tags=["\u5065\u5eb7\u9910"], ingredients=["\u8c46\u8150", "\u852c\u83dc"]),
        ],
    )

    response = client.post(
        "/api/recommend",
        json={"healthGoal": "\u5747\u8861\u98f2\u98df", "tags": [], "excludedIngredients": [], "keyword": None},
    )

    names = [meal["mealName"] for meal in response.json()]
    assert "\u6e6f\u5305" not in names
    assert "\u852c\u98df\u4fbf\u7576" in names


def test_dataset_recommendation_exclusions_and_keyword_search():
    pork_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": ["\u8c6c\u8089"], "keyword": None},
    )
    beef_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": ["\u725b\u8089"], "keyword": None},
    )
    seafood_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": ["\u6d77\u9bae"], "keyword": None},
    )
    cilantro_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": ["\u9999\u83dc"], "keyword": None},
    )
    spicy_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": ["\u4e0d\u5403\u8fa3"], "keyword": None},
    )
    low_calorie_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": [], "keyword": "\u4f4e\u5361"},
    )
    dessert_response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": [], "excludedIngredients": [], "keyword": "\u751c\u9ede"},
    )

    pork_names = [meal["mealName"] for meal in pork_response.json()]
    beef_names = [meal["mealName"] for meal in beef_response.json()]
    seafood_names = [meal["mealName"] for meal in seafood_response.json()]
    cilantro_names = [meal["mealName"] for meal in cilantro_response.json()]
    spicy_names = [meal["mealName"] for meal in spicy_response.json()]
    low_calorie_names = [meal["mealName"] for meal in low_calorie_response.json()]
    dessert_names = [meal["mealName"] for meal in dessert_response.json()]

    assert "\u8c5a\u4e3c" not in pork_names
    assert "\u6e6f\u5305" not in pork_names
    assert "\u725b\u4e3c" not in beef_names
    assert "\u725b\u8089\u9eb5" not in beef_names
    assert "\u8766\u4ec1\u7092\u98ef" not in seafood_names
    assert "\u9bae\u9b5a\u5065\u5eb7\u9910" not in seafood_names
    assert "\u9999\u83dc\u725b\u8089\u6e6f" not in cilantro_names
    assert "\u9ebb\u8fa3\u8c46\u8150" not in spicy_names
    assert any(name in low_calorie_names for name in ["\u4f4e\u5361\u6c99\u62c9", "\u8212\u80a5\u96de\u80f8\u9910"])
    assert any(name in dessert_names for name in ["\u8089\u6842\u6372", "\u86cb\u7cd5", "OREO \u51b0\u70ab\u98a8"])


def test_vegetarian_recommendation_excludes_dataset_meat_and_seafood():
    response = client.post(
        "/api/recommend",
        json={"healthGoal": "", "tags": ["\u7d20\u98df"], "excludedIngredients": [], "keyword": None},
    )

    names = [meal["mealName"] for meal in response.json()]
    assert "\u81ed\u8c46\u8150" in names
    assert "\u8c5a\u4e3c" not in names
    assert "\u8766\u4ec1\u7092\u98ef" not in names


def test_incomplete_image_analysis_confidence_is_capped():
    result = normalize_and_enrich_result(
        {
            "id": "test-incomplete",
            "mealName": "\u7591\u4f3c\u9910\u9ede",
            "mealType": "\u5f85\u78ba\u8a8d",
            "estimatedCalories": 500,
            "estimatedProtein": 20,
            "tags": ["\u5f85\u78ba\u8a8d"],
            "mainIngredients": ["\u4e3b\u8981\u98df\u6750\u5f85\u78ba\u8a8d"],
            "allergens": [],
            "recommendationReason": "\u7cfb\u7d71\u7121\u6cd5\u5f9e\u5716\u7247\u4e2d\u7a69\u5b9a\u8fa8\u8b58\u5177\u9ad4\u9910\u9ede\uff0c\u5efa\u8b70\u88dc\u5145\u6587\u5b57\u63cf\u8ff0\u3002",
            "confidence": 0.95,
            "sourceType": "image",
            "createdAt": "2026-06-13T00:00:00+00:00",
            "isAiGenerated": True,
        },
    )

    assert result.confidence <= 0.4
