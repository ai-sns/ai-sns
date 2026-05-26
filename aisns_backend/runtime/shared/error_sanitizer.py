# -*- coding: utf-8 -*-
"""Helpers for safe user-facing error messages."""
import re
from typing import Any


_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\bsk-svcac[A-Za-z0-9_\-\*]{12,}\b"),
)


def _mask_secret(match: re.Match) -> str:
    value = match.group(0)
    if len(value) <= 12:
        return "[redacted]"
    return f"{value[:6]}...{value[-4:]}"


def sanitize_user_error(error: Any, max_length: int = 420) -> str:
    """Return a compact, secret-safe message suitable for UI display."""
    text = str(error or "").strip()
    if not text:
        return "Unknown error"

    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(_mask_secret, text)

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_length:
        text = text[:max_length].rstrip() + "..."
    return text
