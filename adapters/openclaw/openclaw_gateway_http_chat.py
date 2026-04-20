import argparse
import json
import os
from typing import Iterable, Optional

try:
    import requests
except ModuleNotFoundError as e:
    raise SystemExit(
        "Missing dependency 'requests'. Install it in the Python environment you're using:\n"
        "  python -m pip install requests\n"
        "Or, if you're using a venv:\n"
        "  <venv>\\Scripts\\python.exe -m pip install requests"
    ) from e


def _iter_sse_data_lines(resp: requests.Response) -> Iterable[str]:
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        if raw.startswith("data: "):
            yield raw[len("data: ") :].strip()


def chat_once(
    *,
    base_url: str,
    token: str,
    agent_id: str,
    message: str,
    stream: bool,
    session_key: Optional[str] = None,
    timeout_seconds: int = 600,
) -> str:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_key:
        headers["X-OpenClaw-Session-Key"] = session_key

    body = {
        "model": f"openclaw:{agent_id}",
        "stream": stream,
        "messages": [{"role": "user", "content": message}],
    }

    s = requests.Session()
    s.trust_env = False

    if not stream:
        r = s.post(url, headers=headers, json=body, timeout=timeout_seconds, allow_redirects=False)
        if 300 <= r.status_code < 400:
            location = r.headers.get("Location")
            raise RuntimeError(
                f"Unexpected redirect ({r.status_code}) to {location!r}. "
                "Refusing to follow redirects; check --base-url (use the gateway root like http://127.0.0.1:18789)."
            )
        if r.status_code == 405:
            allow = r.headers.get("Allow")
            raise RuntimeError(
                f"HTTP 405 Method Not Allowed from {r.url}. "
                f"method={getattr(r.request, 'method', None)!r} allow={allow!r}. "
                "This often happens if a redirect/proxy turned your POST into a GET."
            )
        r.raise_for_status()
        data = r.json()
        return str(data["choices"][0]["message"]["content"])

    full: list[str] = []
    with s.post(
        url,
        headers=headers,
        json=body,
        stream=True,
        timeout=timeout_seconds,
        allow_redirects=False,
    ) as r:
        if 300 <= r.status_code < 400:
            location = r.headers.get("Location")
            raise RuntimeError(
                f"Unexpected redirect ({r.status_code}) to {location!r}. "
                "Refusing to follow redirects; check --base-url (use the gateway root like http://127.0.0.1:18789)."
            )
        if r.status_code == 405:
            allow = r.headers.get("Allow")
            raise RuntimeError(
                f"HTTP 405 Method Not Allowed from {r.url}. "
                f"method={getattr(r.request, 'method', None)!r} allow={allow!r}. "
                "This often happens if a redirect/proxy turned your POST into a GET."
            )
        r.raise_for_status()
        for data_str in _iter_sse_data_lines(r):
            if data_str == "[DONE]":
                break
            chunk = json.loads(data_str)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content")
            if isinstance(content, str) and content:
                print(content, end="", flush=True)
                full.append(content)
        print()

    return "".join(full)


def _resolve_token(cli_token: Optional[str]) -> str:
    token = cli_token or os.environ.get("OPENCLAW_GATEWAY_TOKEN") or os.environ.get("CLAWDBOT_GATEWAY_TOKEN")
    if not token:
        raise SystemExit(
            "Missing gateway token. Provide --token or set OPENCLAW_GATEWAY_TOKEN."
        )
    return token


def main() -> None:
    p = argparse.ArgumentParser(description="OpenClaw Gateway HTTP chat client (/v1/chat/completions)")
    p.add_argument("--base-url", default="http://127.0.0.1:18789")
    p.add_argument("--token", default=None)
    p.add_argument("--agent-id", default="main")
    p.add_argument("--session-key", default=None)
    p.add_argument("--no-stream", action="store_true")
    p.add_argument("message", nargs="?", default="hello")
    args = p.parse_args()

    token = _resolve_token(args.token)
    text = chat_once(
        base_url=args.base_url,
        token=token,
        agent_id=args.agent_id,
        message=args.message,
        stream=not args.no_stream,
        session_key=args.session_key,
    )

    if args.no_stream:
        print(text)


if __name__ == "__main__":
    main()
