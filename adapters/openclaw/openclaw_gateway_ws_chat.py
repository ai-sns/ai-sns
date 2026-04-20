import argparse
import asyncio
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Optional

import websockets

PROTOCOL_VERSION = 3


def _extract_text_from_chat_message(message: Any) -> str:
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            parts.append(part["text"])
    return "".join(parts)


@dataclass
class GatewayHello:
    conn_id: Optional[str]
    server_version: Optional[str]


class GatewayWsClient:
    def __init__(
        self,
        *,
        url: str,
        token: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "gateway-client",
        client_mode: str = "ui",
        client_display_name: str = "python-client",
    ):
        self.url = url
        self.token = token
        self.password = password
        self.client_id = client_id
        self.client_mode = client_mode
        self.client_display_name = client_display_name

        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._reader_task: Optional[asyncio.Task[None]] = None
        self._pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def __aenter__(self):
        self._ws = await websockets.connect(self.url, max_size=25 * 1024 * 1024)
        self._reader_task = asyncio.create_task(self._reader())
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._reader_task:
            self._reader_task.cancel()
        if self._ws:
            await self._ws.close()

    async def _reader(self) -> None:
        assert self._ws is not None
        async for raw in self._ws:
            obj = json.loads(raw)
            frame_type = obj.get("type")

            if frame_type == "res" and isinstance(obj.get("id"), str):
                fut = self._pending.pop(obj["id"], None)
                if fut and not fut.done():
                    fut.set_result(obj)
                continue

            if frame_type == "event":
                await self._event_queue.put(obj)
                continue

    async def request(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        assert self._ws is not None
        req_id = str(uuid.uuid4())
        frame = {
            "type": "req",
            "id": req_id,
            "method": method,
            "params": params or {},
        }
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[req_id] = fut
        await self._ws.send(json.dumps(frame))
        res = await fut
        if not res.get("ok", False):
            err = res.get("error") or {}
            msg = err.get("message") or "unknown error"
            raise RuntimeError(f"{method} failed: {msg}")
        payload = res.get("payload")
        return payload if isinstance(payload, dict) else {}

    async def next_event(self) -> dict[str, Any]:
        return await self._event_queue.get()

    async def connect(self) -> GatewayHello:
        # The gateway sends connect.challenge immediately on open; we don't need it
        # when using shared-secret auth (token/password), but we drain a little to
        # keep the queue clean.
        await self._drain_initial_challenge()

        auth: Optional[dict[str, Any]] = None
        if self.token or self.password:
            auth = {}
            if self.token:
                auth["token"] = self.token
            if self.password:
                auth["password"] = self.password

        params: dict[str, Any] = {
            "minProtocol": PROTOCOL_VERSION,
            "maxProtocol": PROTOCOL_VERSION,
            "client": {
                "id": self.client_id,
                "displayName": self.client_display_name,
                "version": "py",
                "platform": os.name,
                "mode": self.client_mode,
                "instanceId": str(uuid.uuid4()),
            },
            "caps": ["tool-events"],
            "role": "operator",
            "scopes": ["operator.admin"],
        }
        if auth:
            params["auth"] = auth

        hello = await self.request("connect", params)

        conn_id = None
        server_version = None
        if isinstance(hello, dict):
            server = hello.get("server")
            if isinstance(server, dict):
                if isinstance(server.get("connId"), str):
                    conn_id = server["connId"]
                if isinstance(server.get("version"), str):
                    server_version = server["version"]

        return GatewayHello(conn_id=conn_id, server_version=server_version)

    async def _drain_initial_challenge(self) -> None:
        # Try to consume the initial connect.challenge quickly if it's already there.
        # Don't block; if nothing is ready, just continue.
        await asyncio.sleep(0)
        while True:
            try:
                evt = self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            if evt.get("type") == "event" and evt.get("event") == "connect.challenge":
                continue
            # Put back anything else.
            await self._event_queue.put(evt)
            return


def _resolve_token(cli_token: Optional[str]) -> str:
    token = cli_token or os.environ.get("OPENCLAW_GATEWAY_TOKEN") or os.environ.get("CLAWDBOT_GATEWAY_TOKEN")
    if not token:
        raise SystemExit("Missing gateway token. Provide --token or set OPENCLAW_GATEWAY_TOKEN.")
    return token


def _compute_session_key(agent_id: str, session_key: Optional[str]) -> str:
    if session_key:
        return session_key
    # Works with the gateway session key parser. This matches the common main session.
    return f"agent:{agent_id}:main"


async def chat_stream(
    *,
    url: str,
    token: str,
    agent_id: str,
    session_key: str,
    message: str,
    thinking: Optional[str],
    deliver: bool,
    timeout_ms: Optional[int],
) -> str:
    run_id = str(uuid.uuid4())

    async with GatewayWsClient(url=url, token=token) as client:
        params: dict[str, Any] = {
            "sessionKey": session_key,
            "message": message,
            "deliver": deliver,
            "idempotencyKey": run_id,
        }
        if thinking:
            params["thinking"] = thinking
        if timeout_ms is not None:
            params["timeoutMs"] = timeout_ms

        # chat.send responds immediately with { runId, status: "started" }
        await client.request("chat.send", params)

        last_text = ""
        while True:
            evt = await client.next_event()
            if evt.get("event") != "chat":
                continue
            payload = evt.get("payload")
            if not isinstance(payload, dict):
                continue
            if payload.get("runId") != run_id:
                continue

            state = payload.get("state")
            text = _extract_text_from_chat_message(payload.get("message"))

            if state == "delta":
                # The gateway emits the full accumulated assistant text so far.
                if text.startswith(last_text):
                    print(text[len(last_text) :], end="", flush=True)
                else:
                    # Fallback: print whole line if the accumulation reset.
                    print(text, end="", flush=True)
                last_text = text
                continue

            if state == "final":
                if text.startswith(last_text):
                    print(text[len(last_text) :], end="", flush=True)
                elif text and text != last_text:
                    print(text, end="", flush=True)
                print()
                return text

            if state == "error":
                raise RuntimeError(str(payload.get("errorMessage") or "chat error"))

            if state == "aborted":
                raise RuntimeError("chat aborted")


def main() -> None:
    p = argparse.ArgumentParser(description="OpenClaw Gateway WebSocket chat client (connect + chat.send)")
    p.add_argument("--url", default="ws://127.0.0.1:18789")
    p.add_argument("--token", default=None)
    p.add_argument("--agent-id", default="main")
    p.add_argument("--session-key", default=None)
    p.add_argument("--thinking", default=None)
    p.add_argument("--deliver", action="store_true")
    p.add_argument("--timeout-ms", type=int, default=None)
    p.add_argument("message", nargs="?", default="hello")
    args = p.parse_args()

    token = _resolve_token(args.token)
    session_key = _compute_session_key(args.agent_id, args.session_key)

    asyncio.run(
        chat_stream(
            url=args.url,
            token=token,
            agent_id=args.agent_id,
            session_key=session_key,
            message=args.message,
            thinking=args.thinking,
            deliver=args.deliver,
            timeout_ms=args.timeout_ms,
        )
    )
    # chat_stream already prints streaming output.


if __name__ == "__main__":
    main()
