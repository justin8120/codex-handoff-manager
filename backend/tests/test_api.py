from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_reports_backend_status(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["aiConfigured"] is False


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


def test_analyze_text_requires_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post("/api/analyze/text", json={"description": "茶葉蛋"})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI analysis service is not configured. Please set OPENAI_API_KEY."
