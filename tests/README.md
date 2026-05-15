# AI-SNS Automated Test Suite

## Overview

This test suite implements the automated testing plan from the v3.1 audit report.
Tests are organized into layers that can run independently.

## Test Layers

| Layer | Directory/File | Requires Backend | Description |
|-------|---------------|-----------------|-------------|
| Unit | `test_unit_*.py` | No | Pure logic tests (i18n, write_queue, utils, settings) |
| API Smoke | `test_api_smoke.py` | Yes | Health check, basic endpoint reachability |
| API Integration | `test_api_integration.py` | Yes | Business logic: Agent, KM, SNS, people_list |
| Concurrency | `test_concurrency.py` | Yes | T12-04 concurrent KM creation, DB lock stress |
| WebSocket | `test_websocket.py` | Yes | WS connect, ping/pong, message flow |

## Running

```bash
# All unit tests (no backend needed)
python -m pytest tests/ -m unit -v

# All API tests (backend must be running on localhost:8788)
python -m pytest tests/ -m api -v

# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --tb=short
```

## Test Environment

| Item | Value |
|------|-------|
| Python | `venv\Scripts\python.exe` |
| Backend | `http://localhost:8788` |
| A2A | `http://localhost:8789` |
| DB | `aisns_backend/db/db.sqlite` |

## Markers

- `@pytest.mark.unit` — No external dependencies
- `@pytest.mark.api` — Requires running backend
- `@pytest.mark.slow` — Long-running stress/concurrency tests

## Audit Report Coverage

| Bug/Risk | Test | Status |
|----------|------|--------|
| B-04 | `test_api_integration::test_people_list_always_returns_json` | ✓ |
| B-08 | `test_unit_i18n::test_lang_dir_path_is_correct` | ✓ |
| B-08 | `test_unit_i18n::test_lt_loads_translation` | ✓ |
| R-02 | `test_unit_write_queue::test_write_queue_serializes` | ✓ |
| T12-04 | `test_concurrency::test_concurrent_km_creation` | ✓ |
| T1-07 | `test_api_smoke::test_health_check` | ✓ |
| T2-02 | `test_api_smoke::test_agent_list` | ✓ |
| T4-01 | `test_api_smoke::test_sns_engine_status` | ✓ |
| T9-06 | `test_api_smoke::test_a2a_commands` | ✓ |
| WS | `test_websocket::test_ws_connect` | ✓ |
