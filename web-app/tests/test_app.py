import io
import pytest
from app import app
from unittest.mock import patch, MagicMock
from bson import ObjectId


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


def test_signup_get(client):
    """
    Test that GET /signup returns signup page.
    """

    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b'<form' in resp.data
    assert b'username' in resp.data


def test_login_get(client):
    """
    Test that GET /login returns login page.
    """

    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'<form' in resp.data
    assert b'password' in resp.data


@patch("app.collection.find_one")
def test_job_pending(mock_find_one, client):
    """
    Test that GET /job/<job_id> returns pending JSON if not complete yet.
    """

    # mock data
    mock_id = ObjectId()
    mock_find_one.return_value = {"_id": mock_id, "status": "pending", "user_id": None}

    resp = client.get(f"/job/{str(mock_id)}")
    assert resp.status_code == 200
    assert b"pending" in resp.data


@patch("app.collection.find_one")
def test_job_complete(mock_find_one, client):
    """
    Test that GET /job/<job_id> shows results page when complete.
    """

    # mock data
    mock_id = ObjectId()
    mock_find_one.return_value = {"_id": mock_id, "status": "complete", "user_id": None, "results": "Test"}

    resp = client.get(f"/job/{str(mock_id)}")
    assert resp.status_code == 200
    assert b"result" in resp.data.lower()


@patch("app.check_password_hash", return_value=True)
@patch("app.mongo")
def test_login_successful(mock_check_password_hash, mock_mongo, client):
    """
    Test for a successful login.
    """

    # create mock user
    mock_user = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "fakehashedpassword",
    }

    mock_mongo.__getitem__.return_value["users"].find_one.return_value = mock_user

    with app.app_context():

        resp = client.post("/login", data={"username": "testuser", "password": "correctpassword"})
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/")


@patch("app.check_password_hash", return_value=False)
@patch("app.mongo")
def test_login_wrong_password(mock_check_password_hash, mock_mongo, client):
    """
    Tests if login failed due to a wrong password.
    """

    # create mock user
    mock_user = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "fakehashedpassword",
    }
    mock_mongo.__getitem__.return_value["users"].find_one.return_value = mock_user

    resp = client.post("/login", data={"username": "testuser", "password": "wrongpassword"})
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


@patch("app.fitz.open")
@patch("app.collection.insert_one")
@patch("app.collection.find_one")
def test_index_post_success(mock_find_one, mock_insert_one, mock_fitz_open, client):
    """
    Test POST / with valid data (PDF and URL).
    """

    # mock data
    mock_id = ObjectId()
    mock_insert_one.return_value.inserted_id = mock_id
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Fake resume text"
    mock_doc = [mock_page]
    mock_fitz_open.return_value = mock_doc

    # mock upload
    data = {
        "resume": (io.BytesIO(b"fake content pretending to be PDF"), "resume.pdf"),
        "job_url": "http://example.com/job-posting"
    }

    resp = client.post("/", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"check();" in resp.data 

    # stimulate polling
    mock_find_one.return_value = {
        "_id": mock_id,
        "status": "pending"
    }

    status_resp = client.get(f"/status/{str(mock_id)}")
    assert status_resp.status_code == 200
    assert b"pending" in status_resp.data

    # stimulate job completion
    mock_find_one.return_value = {
        "_id": mock_id,
        "status": "complete",
        "results": "Fake Screening Results"
    }

    status_resp = client.get(f"/status/{str(mock_id)}")
    assert status_resp.status_code == 200
    assert b"complete" in status_resp.data


def test_logout(client):
    """
    Test that the user can log out.
    """

    resp = client.get("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/login")


def test_post_missing_pdf(client):
    """
    Test POST / with no resume file should give 404.
    """

    # mock data
    data = {
        "job_url": "http://example.com/job-posting"
    }

    resp = client.post("/", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert b"Missing fields" in resp.data


@patch("app.mongo")
def test_signup_success(mock_mongo, client):
    """
    Test that POST signup creates a user.
    """

    resp = client.post("/signup", data={"username": "newuser", "password": "newpass"})
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
