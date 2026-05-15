"""
WebSocket connectivity tests — verify basic WS handshake and message flow.

Requires: backend running on localhost:8788
"""
import asyncio
import json
import pytest

pytestmark = pytest.mark.api

WS_URL = "ws://localhost:8788/ws"


class TestWebSocketConnect:
    """Basic WebSocket connectivity."""

    @pytest.mark.asyncio
    async def test_ws_connect_and_disconnect(self):
        """Should be able to establish and close a WebSocket connection."""
        import websockets

        try:
            async with websockets.connect(WS_URL, open_timeout=5) as ws:
                # Connection established if we reach here
                await ws.close()
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

    @pytest.mark.asyncio
    async def test_ws_ping_pong(self):
        """Server should respond to WebSocket ping."""
        import websockets

        try:
            async with websockets.connect(WS_URL, open_timeout=5) as ws:
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout=5.0)
                # If we get here, ping/pong works
                await ws.close()
        except asyncio.TimeoutError:
            pytest.fail("WebSocket ping/pong timed out")
        except Exception as e:
            pytest.fail(f"WebSocket ping failed: {e}")

    @pytest.mark.asyncio
    async def test_ws_send_json_message(self):
        """Send a JSON message to the WebSocket; server should not crash."""
        import websockets

        try:
            async with websockets.connect(WS_URL, open_timeout=5) as ws:
                # Send a test message
                msg = json.dumps({"type": "ping", "data": {}})
                await ws.send(msg)

                # Try to receive any response within 3 seconds
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    # If we get a response, verify it's valid JSON
                    data = json.loads(response)
                    assert isinstance(data, dict)
                except asyncio.TimeoutError:
                    # No response is also acceptable (server may not echo pings)
                    pass

                await ws.close()
        except Exception as e:
            pytest.fail(f"WebSocket message test failed: {e}")

    @pytest.mark.asyncio
    async def test_ws_multiple_connections(self):
        """Multiple simultaneous WS connections should work."""
        import websockets

        connections = []
        try:
            for _ in range(3):
                ws = await websockets.connect(WS_URL, open_timeout=5)
                connections.append(ws)

            # All connections established
            assert len(connections) == 3

            # Close all
            for ws in connections:
                await ws.close()
                await asyncio.sleep(0.1)
        except Exception as e:
            # Cleanup
            for ws in connections:
                try:
                    await ws.close()
                except Exception:
                    pass
            pytest.fail(f"Multiple WS connections failed: {e}")
