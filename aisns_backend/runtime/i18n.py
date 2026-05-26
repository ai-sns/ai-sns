"""
Internationalization (i18n) module.

Usage:
    from runtime.i18n import lt
    lt("home.main.greeting", "Welcome")
    # Returns the translated string for the current language,
    # or the fallback if key is not found.

Language files are stored in runtime/lang/{lang}.json
"""
import os
import json
import logging
from runtime.globals import global_env
from runtime.shared import debug_info

logger = logging.getLogger(__name__)

_lang_cache = {}  # {"en": {...}, "zh": {...}}
_lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang")


def _get_lang_code() -> str:
    """Get current language code from global_env."""
    lang = global_env.get("lang", "en")
    # Backward compatible: old code used 0/1 for en/zh
    if lang == 0 or lang == "0":
        return "en"
    if lang == 1 or lang == "1":
        return "zh"
    return str(lang) if lang else "en"


def _load_lang(lang_code: str) -> dict:
    """Load language file and cache it."""
    if lang_code in _lang_cache:
        return _lang_cache[lang_code]

    file_path = os.path.join(_lang_dir, f"{lang_code}.json")
    data = {}
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    except Exception as e:
        logger.warning("Failed to load language file %s: %s", file_path, e)

    _lang_cache[lang_code] = data
    return data


def _resolve_key(data: dict, key: str):
    """Resolve a dotted key like 'home.main.greeting' from a nested dict."""
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current if isinstance(current, str) else None


def reload_lang():
    """Clear cache and reload language files."""
    _lang_cache.clear()


def lt(key: str, fallback: str = "") -> str:
    """
    Translate a key to the current language.

    Args:
        key: Dotted key path, e.g. "home.main.greeting"
        fallback: Default text if key is not found

    Returns:
        Translated string, or fallback
    """
    lang_code = _get_lang_code()
    lang_data = _load_lang(lang_code)
    result = _resolve_key(lang_data, key)
    if result is not None:
        return result

    # If not found in current language, try English as ultimate fallback
    if lang_code != "en":
        en_data = _load_lang("en")
        result = _resolve_key(en_data, key)
        if result is not None:
            return result

    return fallback
