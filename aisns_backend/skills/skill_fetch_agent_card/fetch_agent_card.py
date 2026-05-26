"""Fetch an A2A agent card from a given endpoint URL.

Input (stdin JSON):
    url  - The A2A endpoint URL.

Output (stdout JSON):
    ok     - True if a card was fetched successfully.
    card   - The raw agent card JSON text (full body, no truncation).
    source - "direct", "well_known_card" (A2A 0.3+ /.well-known/agent-card.json),
             or "well_known_legacy" (legacy /.well-known/agent.json).
    error  - Error description when all attempts fail.
"""

import json
import sys
from urllib.parse import urlparse

try:
    import urllib.request
    import ssl
except ImportError:
    pass

TIMEOUT_SECONDS = 10


def _try_get(url: str) -> str:
    """GET a URL and return the FULL response body if it looks like JSON.

    NOTE: We deliberately do NOT truncate the body. Agent cards are consumed
    by downstream JSON parsers; any truncation produces invalid JSON and
    causes the caller to silently fall back to other sources (e.g. PEP).
    """
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, method="GET", headers={
        "Accept": "application/json",
        "User-Agent": "AI-SNS-Skill/1.0",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS, context=ctx) as resp:
        body = resp.read().decode("utf-8", errors="replace").strip()
        if body and (body.startswith("{") or body.startswith("[")):
            return body
    return ""


def main():
    raw = sys.stdin.read() or "{}"
    try:
        params = json.loads(raw)
    except Exception:
        params = {}

    url = (params.get("url") or "").strip()
    if not url:
        print(json.dumps({"ok": False, "card": "", "source": "", "error": "url parameter is required"}, ensure_ascii=False))
        return

    # Attempt 1: direct GET on the endpoint URL
    try:
        card = _try_get(url)
        if card:
            print(json.dumps({"ok": True, "card": card, "source": "direct", "error": ""}, ensure_ascii=False))
            return
    except Exception as e1:
        pass  # fall through to well-known

    # Attempt 2: fallback to A2A 0.3+ standard path /.well-known/agent-card.json
    try:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        well_known_card = f"{origin}/.well-known/agent-card.json"
        card = _try_get(well_known_card)
        if card:
            print(json.dumps({"ok": True, "card": card, "source": "well_known_card", "error": ""}, ensure_ascii=False))
            return
    except Exception as e2:
        pass

    # Attempt 3: legacy fallback /.well-known/agent.json (pre-0.3 A2A)
    try:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        well_known_legacy = f"{origin}/.well-known/agent.json"
        card = _try_get(well_known_legacy)
        if card:
            print(json.dumps({"ok": True, "card": card, "source": "well_known_legacy", "error": ""}, ensure_ascii=False))
            return
    except Exception as e3:
        pass

    print(json.dumps({
        "ok": False,
        "card": "",
        "source": "",
        "error": f"All fetch attempts failed (direct, /.well-known/agent-card.json, /.well-known/agent.json) for: {url}"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
