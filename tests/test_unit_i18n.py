"""
Unit tests for runtime/i18n.py — verifies B-08 (lang directory path bug).

These tests do NOT require a running backend.
"""
import os
import json
import tempfile
import pytest
from pathlib import Path


pytestmark = pytest.mark.unit

BACKEND_ROOT = Path(__file__).resolve().parent.parent / "aisns_backend"
I18N_FILE = BACKEND_ROOT / "runtime" / "i18n.py"
LANG_DIR = BACKEND_ROOT / "runtime" / "lang"


class TestI18nPathBug:
    """B-08: Verify the _lang_dir path construction in i18n.py."""

    def test_lang_directory_exists(self):
        """The actual lang directory must exist at runtime/lang/."""
        assert LANG_DIR.exists(), f"Expected lang dir at {LANG_DIR}"
        assert LANG_DIR.is_dir()

    def test_lang_files_present(self):
        """At least en.json and zh.json should be present."""
        en_file = LANG_DIR / "en.json"
        zh_file = LANG_DIR / "zh.json"
        assert en_file.exists(), "en.json missing"
        assert zh_file.exists(), "zh.json missing"

    def test_lang_dir_path_is_correct(self):
        """
        B-08 core check: _lang_dir in i18n.py should resolve to runtime/lang/,
        NOT runtime/runtime/lang/.
        """
        from runtime import i18n
        actual_dir = Path(i18n._lang_dir).resolve()
        expected_dir = LANG_DIR.resolve()

        # This is the B-08 bug detection:
        # If _lang_dir == ...runtime/runtime/lang, this assertion fails
        wrong_dir = (BACKEND_ROOT / "runtime" / "runtime" / "lang").resolve()
        assert actual_dir != wrong_dir, (
            f"B-08 BUG CONFIRMED: _lang_dir points to {actual_dir} "
            f"(double 'runtime' in path)"
        )

        # Positive check
        assert actual_dir == expected_dir, (
            f"_lang_dir mismatch: got {actual_dir}, expected {expected_dir}"
        )

    def test_lang_dir_path_exists_on_disk(self):
        """The _lang_dir value should point to an existing directory."""
        from runtime import i18n
        assert os.path.isdir(i18n._lang_dir), (
            f"_lang_dir does not exist on disk: {i18n._lang_dir}"
        )


class TestI18nTranslation:
    """Verify lt() function works correctly when path is fixed."""

    def test_lt_returns_fallback_for_missing_key(self):
        """lt() with unknown key returns fallback."""
        from runtime.i18n import lt
        result = lt("nonexistent.key.path", "my_fallback")
        assert result == "my_fallback"

    def test_lt_loads_english_key(self):
        """lt() can resolve a known English key."""
        from runtime.i18n import lt, _load_lang, reload_lang
        from runtime.globals import global_env

        # Force English
        global_env["lang"] = "en"
        reload_lang()

        # Try loading — if B-08 is present, this returns fallback
        en_data = _load_lang("en")
        if en_data:
            # Use a key we know exists
            result = lt("home.config.title", "FALLBACK")
            assert result == "Configuration", (
                f"Expected 'Configuration', got '{result}' — "
                "lang file may not be loading (B-08?)"
            )
        else:
            pytest.skip("en.json could not be loaded (B-08 bug active)")

    def test_lt_loads_chinese_key(self):
        """lt() can resolve a known Chinese key."""
        from runtime.i18n import lt, _load_lang, reload_lang
        from runtime.globals import global_env

        global_env["lang"] = "zh"
        reload_lang()

        zh_data = _load_lang("zh")
        if zh_data:
            # Verify any key resolves (not just fallback)
            result = lt("home.config.title", "FALLBACK")
            assert result != "FALLBACK", (
                f"Got fallback for zh key — translation not loaded (B-08?)"
            )
        else:
            pytest.skip("zh.json could not be loaded (B-08 bug active)")

    def test_reload_lang_clears_cache(self):
        """reload_lang() should clear the internal cache."""
        from runtime.i18n import _lang_cache, reload_lang, _load_lang

        _load_lang("en")
        assert "en" in _lang_cache
        reload_lang()
        assert len(_lang_cache) == 0


class TestI18nEnJsonStructure:
    """Validate the structure of en.json."""

    def test_en_json_is_valid(self):
        """en.json must be valid JSON with at least one top-level key."""
        with open(LANG_DIR / "en.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_en_json_has_expected_sections(self):
        """en.json should have agent section based on known usage."""
        with open(LANG_DIR / "en.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "agent" in data, "Missing 'agent' section in en.json"
