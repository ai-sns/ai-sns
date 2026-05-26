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


# OpenAI reasoning model families. These models reject the legacy
# `max_tokens` parameter (require `max_completion_tokens`), only accept the
# default temperature (1), and ignore sampling params like top_p /
# frequency_penalty / presence_penalty.
_OPENAI_REASONING_PREFIXES = ("o1", "o3", "o4", "gpt-5")


def is_openai_reasoning_model(model_name: str) -> bool:
    """Return True if the model belongs to an OpenAI reasoning family.

    Detection is by name prefix (`o1`, `o3`, `o4`, `gpt-5`). Only meaningful
    when paired with `provider == 'openai'` (i.e. api.openai.com). Custom /
    OpenAI-compatible gateways should keep using `max_tokens` because most
    third-party providers (DeepSeek, Qwen, etc.) still expect it even for
    their own reasoning models.
    """
    m = str(model_name or "").strip().lower()
    if not m:
        return False
    for p in _OPENAI_REASONING_PREFIXES:
        if m == p or m.startswith(p + "-") or m.startswith(p + "."):
            return True
    return False
