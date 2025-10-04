import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    A Pytest fixture providing a test client for the FastAPI app.
    """
    return TestClient(app)


def test_health_endpoint(client):
    """
    Test the /health endpoint to ensure the service is running correctly.
    """
    response = client.get("/health")
    assert response.status_code == 200, "Health endpoint failed"
    assert response.json() == {"status": "ok"}, "Health endpoint response mismatch"


def test_unauthorized_timetable_access(client):
    """
    Ensure accessing /timetable without a valid API key results in a 401 Unauthorized error.
    """
    response = client.get("/timetable")  # No API key provided
    assert response.status_code == 401, "Unauthorized timetable access did not return 401"


def test_invalid_api_key(client):
    """
    Check that providing an invalid API key results in a 401 Unauthorized error.
    """
    invalid_headers = {"X-API-Key": "invalid-key"}
    response = client.get("/timetable", headers=invalid_headers)
    assert response.status_code == 401, "Invalid API key access did not return 401"