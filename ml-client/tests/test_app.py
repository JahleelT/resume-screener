import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_process_missing_id(client):
    """POST /process without 'id' returns a 400 and JSON error."""
    resp = client.post("/process", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "missing id"
