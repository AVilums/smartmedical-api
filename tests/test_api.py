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


def test_rate_limiting(client):
    """
    Test that the rate-limiting mechanism works as intended.
    """
    # Set a mock API key and headers
    rate_limit_headers = {"X-API-Key": "test-key"}

    # First request should pass
    response_1 = client.get("/timetable", headers=rate_limit_headers)
    assert response_1.status_code in (200, 501), "First request failed or unexpected status"

    # Second request should be rate-limited
    response_2 = client.get("/timetable", headers=rate_limit_headers)
    assert response_2.status_code == 429, "Second request was not rate limited"


def test_timetable_response_format(client):
    """
    If the /timetable endpoint is implemented, check the response format.
    """
    valid_headers = {"X-API-Key": "test-key"}
    response = client.get("/timetable", headers=valid_headers)

    # If the endpoint is implemented, check the response JSON
    if response.status_code == 200:
        json_data = response.json()
        assert "source" in json_data, "Response does not include 'source'"
        assert isinstance(json_data.get("slots"), list), "'slots' should be a list"
    else:
        # If not implemented, ensure it returns 501
        assert response.status_code == 501, "Unexpected status for unimplemented endpoint"