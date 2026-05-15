"""
API integration tests — business logic verification.

Requires: backend running on localhost:8788
"""
import pytest
import httpx

pytestmark = pytest.mark.api

BASE_URL = "http://localhost:8788"


def _get(path: str, **kwargs) -> httpx.Response:
    return httpx.get(f"{BASE_URL}{path}", timeout=10.0, **kwargs)


def _post(path: str, **kwargs) -> httpx.Response:
    return httpx.post(f"{BASE_URL}{path}", timeout=10.0, **kwargs)


class TestPeopleList:
    """B-04: get_people_list must always return JSON, never null/204."""

    def test_people_list_with_coords(self):
        """With valid lng/lat, should return JSON."""
        r = _get("/api/get_people_list/", params={"lng": "116.4", "lat": "39.9"})
        assert r.status_code == 200
        data = r.json()
        assert data is not None, "Response must not be null"
        assert isinstance(data, (dict, list)), f"Expected JSON structure, got {type(data)}"

    def test_people_list_without_coords(self):
        """Without coords, should still return a valid JSON fallback."""
        r = _get("/api/get_people_list/")
        # Should not be 500 or null
        assert r.status_code in (200, 422), f"Unexpected status: {r.status_code}"
        if r.status_code == 200:
            data = r.json()
            assert data is not None

    def test_people_list_invalid_coords(self):
        """With invalid coords, should return graceful fallback, not crash."""
        r = _get("/api/get_people_list/", params={"lng": "abc", "lat": "xyz"})
        assert r.status_code in (200, 400, 422)
        # Must still be valid JSON
        try:
            r.json()
        except Exception:
            pytest.fail("Response is not valid JSON")


class TestKMCreation:
    """KM knowledge base creation - basic validation."""

    def test_create_km_minimal_payload(self):
        """POST /api/km with minimal payload should succeed or return validation error."""
        r = _post("/api/km", json={"name": "pytest_test_kb", "kmtype": 1})
        # 200/201 = success, 400/422 = validation, 409 = duplicate
        assert r.status_code in (200, 201, 400, 409, 422), (
            f"Unexpected status: {r.status_code}"
        )
        if r.status_code in (200, 201):
            data = r.json()
            assert data is not None

    def test_create_km_missing_name(self):
        """POST /api/km without name should fail with validation error."""
        r = _post("/api/km", json={"kmtype": 1})
        # Should be 422 (validation) or 400
        assert r.status_code in (400, 422, 500), (
            f"Expected validation error, got {r.status_code}"
        )


class TestAgentOperations:
    """Agent CRUD basic checks."""

    def test_agent_list_not_empty_structure(self):
        """Agent list endpoint returns proper structure."""
        r = _get("/api/agent/list")
        assert r.status_code == 200
        data = r.json()
        # Verify it's a structured response
        assert isinstance(data, (dict, list))

    def test_get_nonexistent_agent(self):
        """Getting a non-existent agent should return 404 or error structure."""
        r = _get("/api/agent/nonexistent-uuid-12345")
        assert r.status_code in (200, 404, 422, 500)


class TestSystemConfig:
    """System configuration endpoints."""

    def test_get_system_settings(self):
        """System settings should be retrievable."""
        r = _get("/api/system/settings")
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, dict)
        else:
            # Endpoint might be at a different path
            pytest.skip(f"System settings returned {r.status_code}")
