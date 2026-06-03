from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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
    assert "雞胸肉便當" in names
    assert "茶葉蛋" in names
    assert "海鮮粥" in names


def test_recommend_excludes_seafood():
    response = client.post(
        "/api/recommend",
        json={
            "healthGoal": "均衡飲食",
            "tags": [],
            "excludedIngredients": ["海鮮"],
            "keyword": None,
        },
    )

    assert response.status_code == 200
    names = [meal["mealName"] for meal in response.json()]
    assert "海鮮粥" not in names
    assert "鮭魚沙拉" not in names
    assert "豆腐蔬菜碗" in names


def test_analyze_text_uses_mock_provider_without_calling_ai(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post(
        "/api/analyze/text",
        json={
            "description": (
                "\u6e1b\u8102 \u9ad8\u86cb\u767d "
                "\u4e0d\u8981\u725b\u8089 \u82b1\u751f\u904e\u654f"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mealName"] == "AI fallback \u9910\u9ede\u5065\u5eb7\u5efa\u8b70"
    assert payload["mealType"] == "\u5065\u5eb7\u9910"
    assert payload["tags"] == ["\u4f4e\u5361", "\u9ad8\u86cb\u767d"]
    assert payload["mainIngredients"] == ["\u96de\u80f8\u8089", "\u852c\u83dc", "\u7cd9\u7c73"]
    assert "\u725b\u8089" not in payload["mainIngredients"]
    assert payload["allergens"] == ["\u82b1\u751f"]
    assert (
        payload["recommendationReason"]
        == "\u76ee\u524d\u4f7f\u7528 rule-based fallback\uff1bAI "
        "\u670d\u52d9\u7121\u6cd5\u4f7f\u7528\u6216\u5c1a\u672a\u8a2d\u5b9a\uff0c"
        "\u56e0\u6b64\u7cfb\u7d71\u6539\u7528\u898f\u5247\u5f0f\u5206\u6790"
        "\u63d0\u4f9b\u5c55\u793a\u7d50\u679c\u3002"
    )
    assert payload["isAiGenerated"] is True


def test_fallback_response_is_ascii_escaped_json(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")

    response = client.post("/api/analyze/text", json={"description": "\u6e1b\u8102"})

    assert response.status_code == 200
    assert b"\\u9910" in response.content
    assert b"\xe9\xa4\x90" not in response.content
    assert response.json()["mealName"] == "AI fallback \u9910\u9ede\u5065\u5eb7\u5efa\u8b70"


def test_analyze_text_requires_key_when_fallback_disabled(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/api/analyze/text", json={"description": "茶葉蛋"})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI analysis service is not configured. Please set OPENAI_API_KEY."
