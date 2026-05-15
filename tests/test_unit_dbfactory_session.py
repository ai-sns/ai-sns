"""B-05 regression tests for DBFactory._session_scope.

Verifies that sessions are always released, even when the wrapped body
raises an exception. Also verifies the contract for a sampling of
representative query functions.
"""
from __future__ import annotations

import os
import sys
from unittest import mock

import pytest

# Ensure aisns_backend is importable.
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "aisns_backend"),
)


def test_session_scope_closes_on_success():
    """The session yielded by _session_scope must be closed after normal exit."""
    from db import DBFactory

    closed = []
    real_session = DBFactory.Session()

    with mock.patch.object(DBFactory, "Session", return_value=real_session):
        original_close = real_session.close

        def _tracking_close(*args, **kwargs):
            closed.append(True)
            return original_close(*args, **kwargs)

        real_session.close = _tracking_close

        with DBFactory._session_scope() as session:
            assert session is real_session

    assert closed, "session.close() must be called after normal exit"


def test_session_scope_closes_on_exception():
    """The session must be closed even when the body raises."""
    from db import DBFactory

    closed = []
    real_session = DBFactory.Session()

    with mock.patch.object(DBFactory, "Session", return_value=real_session):
        original_close = real_session.close

        def _tracking_close(*args, **kwargs):
            closed.append(True)
            return original_close(*args, **kwargs)

        real_session.close = _tracking_close

        with pytest.raises(RuntimeError, match="boom"):
            with DBFactory._session_scope() as session:
                assert session is real_session
                raise RuntimeError("boom")

    assert closed, "session.close() must be called on exception path"


def test_query_functions_do_not_leak_on_exception():
    """When a query raises inside a refactored function, no session leak occurs.

    We patch session.query to raise and confirm that the unsafe code path
    (e.g. query_AIChatMessages) now propagates the exception while still
    releasing the session.
    """
    from db import DBFactory

    real_session = DBFactory.Session()
    closed = []
    original_close = real_session.close

    def _tracking_close(*args, **kwargs):
        closed.append(True)
        return original_close(*args, **kwargs)

    real_session.close = _tracking_close

    def _raising_query(*args, **kwargs):
        raise RuntimeError("simulated db failure")

    real_session.query = _raising_query  # type: ignore[assignment]

    with mock.patch.object(DBFactory, "Session", return_value=real_session):
        with pytest.raises(RuntimeError, match="simulated db failure"):
            DBFactory.query_AIChatMessages(id=1)

    assert closed, (
        "query_AIChatMessages must release its session even when query() raises"
    )


def test_query_AIChatMessages_returns_none_for_missing_row():
    """Sanity: refactored function still returns None for non-existent row."""
    from db import DBFactory

    record = DBFactory.query_AIChatMessages(id=-999999)
    assert record is None
