import io
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_get_returns_200(client):
    """GET / should return the upload form."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Resume Screener" in resp.data


def test_index_post_missing_fields_returns_400(client):
    """POST / with no file or job_url should give a 400 and error message."""
    resp = client.post(
        "/",
        data={},  # no resume, no job_url
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert b"Missing fields" in resp.data
