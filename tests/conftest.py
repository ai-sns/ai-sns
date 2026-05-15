"""
Shared fixtures and configuration for the AI-SNS test suite.
"""
import sys
import os
from pathlib import Path

import pytest

# Ensure aisns_backend is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent / "aisns_backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Base URL for API tests
API_BASE_URL = os.environ.get("AISNS_TEST_URL", "http://localhost:8788")
A2A_BASE_URL = os.environ.get("AISNS_A2A_URL", "http://localhost:8789")


@pytest.fixture
def api_base_url():
    """Return the backend API base URL."""
    return API_BASE_URL


@pytest.fixture
def a2a_base_url():
    """Return the A2A service base URL."""
    return A2A_BASE_URL


@pytest.fixture
def async_client():
    """Create an httpx async client for API testing."""
    import httpx
    return httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0)


@pytest.fixture
def sync_client():
    """Create an httpx sync client for API testing."""
    import httpx
    return httpx.Client(base_url=API_BASE_URL, timeout=10.0)
