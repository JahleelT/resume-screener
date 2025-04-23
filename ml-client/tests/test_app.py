import pytest
from app import app, collection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_analyze_missing_fields(client):
    """POST /analyze without resume_path or job_url returns a 400 and JSON error."""
    resp = client.post("/analyze", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "Missing resume_path or job_url"


def test_history_returns_list(monkeypatch, client):
    """GET /history should return a JSON list (even if empty)."""
    # Monkey-patch the DB call to avoid needing a real Mongo instance
    monkeypatch.setattr(collection, "find", lambda *args, **kwargs: [])
    resp = client.get("/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
