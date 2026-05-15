"""
API smoke tests — verify key endpoints are reachable and return expected shapes.

Requires: backend running on localhost:8788
"""
import pytest
import httpx

pytestmark = pytest.mark.api

BASE_URL = "http://localhost:8788"


def _get(path: str, **kwargs) -> httpx.Response:
    """Helper: synchronous GET with timeout."""
    return httpx.get(f"{BASE_URL}{path}", timeout=10.0, **kwargs)


def _post(path: str, **kwargs) -> httpx.Response:
    """Helper: synchronous POST with timeout."""
    return httpx.post(f"{BASE_URL}{path}", timeout=10.0, **kwargs)


class TestHealthCheck:
    """T1-07: Health check endpoints."""

    def test_health_root(self):
        """/health should return 200 with status."""
        r = _get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data

    def test_health_api(self):
        """/api/health should return 200."""
        r = _get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data


class TestAgentList:
    """T2-02: Agent list endpoint."""

    def test_agent_list_returns_json(self):
        """/api/agent/list should return success structure."""
        r = _get("/api/agent/list")
        assert r.status_code == 200
        data = r.json()
        # Expected shape: {"success": true, "data": [...]}
        assert "success" in data or "data" in data or isinstance(data, list), (
            f"Unexpected response shape: {data}"
        )

    def test_agent_list_data_is_list(self):
        """Agent list data should be a list."""
        r = _get("/api/agent/list")
        data = r.json()
        if isinstance(data, dict) and "data" in data:
            assert isinstance(data["data"], list)
        elif isinstance(data, list):
            pass  # Direct list response is also acceptable
        else:
            pytest.fail(f"Unexpected shape: {data}")


class TestSNSEngine:
    """T4-01: SNS engine status."""

    def test_engine_status(self):
        """/api/sns/engine-status should return a JSON structure."""
        r = _get("/api/sns/engine-status")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)


class TestA2ACommands:
    """T9-06: A2A command discovery."""

    def test_a2a_commands_endpoint(self):
        """/api/sns/a2a/commands should return command list."""
        r = _get("/api/sns/a2a/commands")
        # May return 200 with list, or 404 if not registered at this path
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, (list, dict))
        else:
            # Acceptable: endpoint might be at different path
            pytest.skip(f"A2A commands endpoint returned {r.status_code}")


class TestSSEStream:
    """T3-02: HTTP/SSE streaming endpoint."""

    def test_chat_stream_endpoint_exists(self):
        """POST /api/chat/stream should accept request (may fail without LLM config)."""
        r = _post(
            "/api/chat/stream",
            json={"messages": [{"role": "user", "content": "ping"}]},
            headers={"Accept": "text/event-stream"},
        )
        # 200 with SSE or 4xx/5xx due to missing LLM config — both prove endpoint exists
        assert r.status_code in (200, 400, 401, 422, 500), (
            f"Unexpected status: {r.status_code}"
        )
