import re
from urllib.parse import urlparse


def normalize_openai_base_url(api_endpoint: str) -> str:
    raw = str(api_endpoint or "").strip()
    if not raw:
        return ""

    try:
        parsed = urlparse(raw)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return raw.rstrip("/")
    except Exception:
        return raw.rstrip("/")

    base = raw
    base = re.sub(r"/chat/completions/?$", "", base, flags=re.IGNORECASE)
    base = base.rstrip("/")
    return base


def normalize_anthropic_base_url(api_endpoint: str) -> str:
    raw = str(api_endpoint or "").strip()
    if not raw:
        return ""

    try:
        parsed = urlparse(raw)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return raw.rstrip("/")
    except Exception:
        return raw.rstrip("/")

    base = raw
    base = re.sub(r"/v1/messages/?$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"/messages/?$", "", base, flags=re.IGNORECASE)
    base = base.rstrip("/")
    return base


def normalize_provider(provider: str) -> str:
    p = str(provider or "").strip().lower()
    return p or "openai"
