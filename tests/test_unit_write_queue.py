"""
Unit tests for db/write_queue.py — verifies DbWriteQueue serialization.

These tests use a temporary SQLite database, no running backend needed.
"""
import asyncio
import threading
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit


class TestDbWriteQueueLogic:
    """Test the write queue serialization mechanism."""

    def test_write_queue_class_exists(self):
        """DbWriteQueue class is importable."""
        from db.write_queue import DbWriteQueue
        assert DbWriteQueue is not None

    def test_write_op_dataclass(self):
        """_WriteOp dataclass works."""
        from db.write_queue import _WriteOp
        import concurrent.futures

        op = _WriteOp(func=lambda s: "result", description="test")
        assert op.func is not None
        assert op.description == "test"
        assert isinstance(op.future, concurrent.futures.Future)

    def test_db_write_function_exists(self):
        """db_write convenience function is importable."""
        from db.write_queue import db_write, db_write_async
        assert callable(db_write)
        assert callable(db_write_async)

    def test_write_queue_singleton_pattern(self):
        """DbWriteQueue uses singleton pattern."""
        from db.write_queue import DbWriteQueue
        # Verify class-level singleton attributes exist
        assert hasattr(DbWriteQueue, '_instance')
        assert hasattr(DbWriteQueue, '_lock')
        assert isinstance(DbWriteQueue._lock, type(threading.Lock()))

    def test_write_queue_submit_write_serializes(self):
        """
        Verify that submit_write processes operations sequentially.
        We mock the Session to avoid needing a real database.
        """
        from db.write_queue import DbWriteQueue

        # Create a fresh instance (bypassing singleton for isolation)
        wq = DbWriteQueue.__new__(DbWriteQueue)
        import queue as q
        import concurrent.futures

        wq._queue = q.Queue()
        wq._session = None
        wq._started = False
        wq._shutting_down = False

        # Track execution order
        execution_order = []
        mock_session = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.close = MagicMock()

        def mock_get_session():
            return mock_session

        wq._get_session = mock_get_session

        # Start worker manually
        wq._worker = threading.Thread(target=wq._worker_loop, daemon=True)
        wq._worker.start()
        wq._started = True

        # Submit operations
        def op1(session):
            execution_order.append(1)
            time.sleep(0.05)
            return "r1"

        def op2(session):
            execution_order.append(2)
            return "r2"

        r1 = wq.submit_write(op1, description="op1")
        r2 = wq.submit_write(op2, description="op2")

        assert r1 == "r1"
        assert r2 == "r2"
        assert execution_order == [1, 2], "Operations must execute in order"

        # Shutdown
        wq.shutdown(wait=True, timeout=5.0)

    def test_write_queue_handles_exception_in_op(self):
        """If a write op raises, the queue continues processing next ops."""
        from db.write_queue import DbWriteQueue
        import queue as q

        wq = DbWriteQueue.__new__(DbWriteQueue)
        wq._queue = q.Queue()
        wq._session = None
        wq._started = False
        wq._shutting_down = False

        mock_session = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.close = MagicMock()

        def mock_get_session():
            return mock_session

        wq._get_session = mock_get_session
        wq._worker = threading.Thread(target=wq._worker_loop, daemon=True)
        wq._worker.start()
        wq._started = True

        # First op raises
        def bad_op(session):
            raise ValueError("intentional error")

        def good_op(session):
            return "ok"

        with pytest.raises(ValueError):
            wq.submit_write(bad_op, description="bad_op")

        # Queue should still work
        result = wq.submit_write(good_op, description="good_op")
        assert result == "ok"

        wq.shutdown(wait=True, timeout=5.0)


class TestDbWriteQueueAsync:
    """Test the async submit path."""

    @pytest.mark.asyncio
    async def test_submit_write_async(self):
        """submit_write_async should work from async context."""
        from db.write_queue import DbWriteQueue
        import queue as q

        wq = DbWriteQueue.__new__(DbWriteQueue)
        wq._queue = q.Queue()
        wq._session = None
        wq._started = False
        wq._shutting_down = False

        mock_session = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.close = MagicMock()

        def mock_get_session():
            return mock_session

        wq._get_session = mock_get_session
        wq._worker = threading.Thread(target=wq._worker_loop, daemon=True)
        wq._worker.start()
        wq._started = True

        result = await wq.submit_write_async(
            lambda s: "async_result", description="async_test"
        )
        assert result == "async_result"

        wq.shutdown(wait=True, timeout=5.0)
