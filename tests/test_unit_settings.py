"""
Unit tests for runtime/config/settings.py and runtime/shared/utils.py.

No running backend needed.
"""
import pytest

pytestmark = pytest.mark.unit


class TestSettings:
    """Verify settings module loads correctly."""

    def test_settings_importable(self):
        """get_settings is importable and returns a settings object."""
        from runtime.config.settings import get_settings
        settings = get_settings()
        assert settings is not None

    def test_settings_has_app_name(self):
        """Settings must have app_name."""
        from runtime.config.settings import get_settings
        settings = get_settings()
        assert hasattr(settings, 'app_name')
        assert settings.app_name

    def test_settings_has_database_config(self):
        """Settings must have database configuration."""
        from runtime.config.settings import get_settings
        settings = get_settings()
        assert hasattr(settings, 'database')
        assert settings.database is not None
        assert hasattr(settings.database, 'full_path')

    def test_settings_has_server_config(self):
        """Settings must have server host/port."""
        from runtime.config.settings import get_settings
        settings = get_settings()
        assert hasattr(settings, 'server')
        assert settings.server.host
        assert settings.server.port > 0

    def test_settings_has_ai_config(self):
        """Settings must have AI/LLM config."""
        from runtime.config.settings import get_settings
        settings = get_settings()
        assert hasattr(settings, 'ai')


class TestUtils:
    """Verify shared utility functions."""

    def test_generate_uuid(self):
        """generate_uuid returns unique 36-char strings."""
        from runtime.shared.utils import generate_uuid
        u1 = generate_uuid()
        u2 = generate_uuid()
        assert len(u1) == 36
        assert u1 != u2

    def test_generate_short_id(self):
        """generate_short_id returns string of requested length."""
        from runtime.shared.utils import generate_short_id
        sid = generate_short_id(12)
        assert len(sid) == 12

    def test_hash_string_deterministic(self):
        """hash_string is deterministic."""
        from runtime.shared.utils import hash_string
        h1 = hash_string("hello")
        h2 = hash_string("hello")
        assert h1 == h2
        assert len(h1) == 64  # SHA-256

    def test_safe_json_roundtrip(self):
        """safe_json_dumps/loads roundtrips correctly."""
        from runtime.shared.utils import safe_json_dumps, safe_json_loads
        data = {"key": "value", "num": 42}
        s = safe_json_dumps(data)
        assert isinstance(s, str)
        parsed = safe_json_loads(s)
        assert parsed == data

    def test_safe_json_loads_invalid(self):
        """safe_json_loads on invalid input returns fallback."""
        from runtime.shared.utils import safe_json_loads
        result = safe_json_loads("not json {{{", default={})
        assert result == {}

    def test_sanitize_filename(self):
        """sanitize_filename strips dangerous characters."""
        from runtime.shared.utils import sanitize_filename
        safe = sanitize_filename("test<>:\"/\\|?*file.txt")
        for ch in '<>:"/\\|?*':
            assert ch not in safe

    def test_mask_sensitive_data(self):
        """mask_sensitive_data masks middle characters."""
        from runtime.shared.utils import mask_sensitive_data
        masked = mask_sensitive_data("sk-abcdef1234567890", 4)
        assert masked.startswith("sk-a")
        assert "*" in masked

    def test_validate_email(self):
        """validate_email basic checks."""
        from runtime.shared.utils import validate_email
        assert validate_email("user@example.com") is True
        assert validate_email("not-an-email") is False
