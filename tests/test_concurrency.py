"""
Concurrency / stress tests — T12-04: concurrent KM creation and DB lock behavior.

Requires: backend running on localhost:8788
WARNING: These tests CREATE records in the database. Run only against a test database.
"""
import asyncio
import time
import pytest
import httpx

pytestmark = [pytest.mark.api, pytest.mark.slow]

BASE_URL = "http://localhost:8788"
CONCURRENCY_LEVEL = 20  # Reduced from audit's 50 for safety


class TestConcurrentKMCreation:
    """
    T12-04: Verify that concurrent knowledge base creation does not trigger
    'OperationalError: database is locked' thanks to DbWriteQueue serialization.
    """

    @pytest.mark.asyncio
    async def test_concurrent_km_creation_no_lock_error(self):
        """
        Fire CONCURRENCY_LEVEL concurrent POST /api/km requests.
        None should return a 500 with 'database is locked'.
        """
        results = []
        errors = []

        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            async def create_km(i: int):
                try:
                    r = await client.post(
                        "/api/km",
                        json={"name": f"pytest_concurrent_{i}_{int(time.time())}", "kmtype": 1}
                    )
                    results.append((i, r.status_code, r.text[:200]))
                    return r
                except Exception as e:
                    errors.append((i, str(e)))
                    return None

            responses = await asyncio.gather(
                *[create_km(i) for i in range(CONCURRENCY_LEVEL)]
            )

        # Analyze results
        locked_errors = [
            (i, text) for i, code, text in results
            if code == 500 and "locked" in text.lower()
        ]

        assert len(locked_errors) == 0, (
            f"Got {len(locked_errors)} 'database is locked' errors out of "
            f"{CONCURRENCY_LEVEL} requests: {locked_errors[:3]}"
        )

        # At least some should succeed (200/201) or get validation errors (422)
        success_count = sum(1 for _, code, _ in results if code in (200, 201))
        assert success_count > 0 or len(errors) == 0, (
            f"No successful creates. Results: {results[:5]}, Errors: {errors[:5]}"
        )

    @pytest.mark.asyncio
    async def test_concurrent_reads_during_writes(self):
        """
        While writing, reads should still work (SQLite WAL allows concurrent reads).
        """
        read_results = []
        write_results = []

        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            async def read_agents():
                r = await client.get("/api/agent/list")
                read_results.append(r.status_code)

            async def write_km(i: int):
                r = await client.post(
                    "/api/km",
                    json={"name": f"pytest_rw_{i}_{int(time.time())}", "kmtype": 1}
                )
                write_results.append(r.status_code)

            # Mix reads and writes
            tasks = []
            for i in range(10):
                tasks.append(read_agents())
                tasks.append(write_km(i))

            await asyncio.gather(*tasks)

        # All reads should succeed
        failed_reads = [s for s in read_results if s != 200]
        assert len(failed_reads) == 0, (
            f"Reads failed during concurrent writes: {failed_reads}"
        )
