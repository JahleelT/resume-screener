from unittest.mock import patch
from app import do_work
import pytest
from app import app
from bson import ObjectId


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_process_missing_id(client):
    """
    POST /process without 'id' returns a 400 and JSON error.
    """
    resp = client.post("/process", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "missing id"


def test_job_not_found():
    """
    POST /process when the job isn't found, nothing should be done.
    """

    mock_job_id = ObjectId()

    with patch("app.collection.find_one", return_value=None):
        do_work(mock_job_id)


def test_fetch_job_description_fails():
    """
    POST /process when fetching the job description fails, ensure proper error handling and output.
    """

    mock_job_id = ObjectId()
    mock_job = {
        "_id": mock_job_id,
        "resume_text": "Sample resume text",
        "job_url": "https://fakeurl.com"
    }

    with patch("app.collection.find_one", return_value=mock_job):
        with patch("app.collection.update_one") as mock_update:
            with patch("app.fetch_job_description", side_effect=Exception("Fetch failed")):
                with patch("app.call_openai") as mock_call_openai:

                    # call_openai should still be called with a placeholder job desc
                    do_work(mock_job_id)
                    assert mock_call_openai.called
                    assert mock_update.called


def test_process_valid_job(client):
    """
    POST /process with a valid job ID should return 202 and begin processing.
    """

    # create mock data
    mock_job_id = ObjectId()
    mock_job = {
        "_id": mock_job_id,
        "resume_text": "Sample resume content",
        "job_url": "https://example.com/job"
    }

    # process starts successfully
    with patch("app.collection.find_one", return_value=mock_job):
        resp = client.post("/process", json={"id": str(mock_job["_id"])})
        assert resp.status_code == 202
        data = resp.get_json()
        assert data["status"] == "started"


def test_job_status_update():
    """
    Ensure the status of the job is updated correctly during processing.
    """

    # create mock data
    mock_job_id = ObjectId()
    mock_job = {
        "_id": mock_job_id,
        "resume_text": "Sample resume content",
        "job_url": "https://example.com/job"
    }

    # checks that the job goes from started to processing to complete
    with patch("app.collection.find_one", return_value=mock_job):
        with patch("app.collection.update_one") as mock_update:
            with patch("app.fetch_job_description", return_value="Job description content"):
                with patch("app.call_openai", return_value={"summary": "Summary", "suggestions": "Suggestions", "job_focus": "Focus"}):

                    do_work(mock_job_id)

                    # processing
                    mock_update.assert_any_call(
                        {"_id": mock_job_id},
                        {"$set": {"status": "processing"}}
                    )

                    # complete
                    mock_update.assert_any_call(
                        {"_id": mock_job_id},
                        {"$set": {"status": "complete", "summary": "Summary", "suggestions": "Suggestions", "job_focus": "Focus"}}
                    )


def test_invalid_json(client):
    """
    POST /process with invalid JSON should return 400.
    """

    # empty field should be invalid JSON
    resp = client.post("/process", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "missing id"


def test_mongodb_operations():
    """
    Tests that the MongoDB operations are done correctly (find and replace)
    """

    # create mock data
    mock_job_id = ObjectId()
    mock_job = {
        "_id": mock_job_id,
        "resume_text": "Sample resume content",
        "job_url": "https://example.com/job"
    }

    with patch("app.collection.find_one", return_value=mock_job) as mock_find, \
         patch("app.collection.update_one") as mock_update:
        
        do_work(mock_job_id)

        # find_one called
        mock_find.assert_called_once_with({"_id": mock_job_id})

        # update_one called twice (processing and completed)
        assert mock_update.call_count == 2