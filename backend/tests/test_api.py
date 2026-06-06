from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_provider import normalize_meal_name
from app.services.web_food_verifier import rerank_food_candidates


client = TestClient(app)


def test_normalize_meal_name_maps_romanized_names():
    assert normalize_meal_name("Katsudon") == "\u8c6c\u6392\u4e3c"
    assert normalize_meal_name("Oyakodon") == "\u89aa\u5b50\u4e3c"
    assert normalize_meal_name("Butadon") == "\u8c5a\u4e3c"
    assert normalize_meal_name("\u8c5a\u4e95") == "\u8c5a\u4e3c"
    assert normalize_meal_name("Gyudon") == "\u725b\u4e3c"
    assert normalize_meal_name("Tendon") == "\u5929\u4e3c"
    assert normalize_meal_name("Curry Rice") == "\u5496\u54e9\u98ef"
    assert normalize_meal_name("Fried Rice") == "\u7092\u98ef"


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
    assert payload["confidence"] == 0.75
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
    assert payload["confidence"] == 0.7


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
    assert payload["confidence"] == 0.75


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
