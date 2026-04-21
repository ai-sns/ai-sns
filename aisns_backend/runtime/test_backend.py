# -*- coding: utf-8 -*-
"""
Backend Components Test

Simple tests to verify backend components are working correctly.
Run with: python -m pytest runtime/test_backend.py -v
Or simply: python runtime/test_backend.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_settings():
    """Test settings configuration"""
    print("Testing settings...")
    from runtime.config.settings import get_settings

    settings = get_settings()

    assert settings is not None
    assert settings.app_name == "AI-SNS API Server"
    assert settings.app_version == "1.0.0"

    # Test AI config
    assert settings.ai is not None
    assert settings.ai.api_base
    assert settings.ai.model

    # Test database config
    assert settings.database is not None
    assert settings.database.full_path

    # Test server config
    assert settings.server is not None
    assert settings.server.host
    assert settings.server.port > 0

    print("✓ Settings test passed")


def test_database_config():
    """Test database configuration"""
    print("Testing database configuration...")
    from db.database import (
        SQLALCHEMY_DATABASE_URL,
        SessionLocal,
        get_db_session
    )

    assert SQLALCHEMY_DATABASE_URL
    assert "sqlite" in SQLALCHEMY_DATABASE_URL
    assert SessionLocal is not None

    # Test session creation
    session = get_db_session()
    assert session is not None
    session.close()

    print("✓ Database configuration test passed")


def test_websocket_manager():
    """Test WebSocket manager"""
    print("Testing WebSocket manager...")
    from runtime.shared.websocket_manager import ConnectionManager, manager

    assert manager is not None
    assert isinstance(manager, ConnectionManager)
    assert manager.get_client_count() == 0
    assert manager.get_connected_clients() == []

    print("✓ WebSocket manager test passed")


def test_utils():
    """Test utility functions"""
    print("Testing utility functions...")
    from runtime.shared.utils import (
        generate_uuid,
        generate_short_id,
        hash_string,
        safe_json_loads,
        safe_json_dumps,
        truncate_string,
        sanitize_filename,
        mask_sensitive_data,
        validate_email
    )

    # Test UUID generation
    uuid1 = generate_uuid()
    uuid2 = generate_uuid()
    assert uuid1 != uuid2
    assert len(uuid1) == 36

    # Test short ID
    short_id = generate_short_id(8)
    assert len(short_id) == 8

    # Test hashing
    hash1 = hash_string("test")
    hash2 = hash_string("test")
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256

    # Test JSON functions
    data = {"key": "value"}
    json_str = safe_json_dumps(data)
    assert json_str == '{"key": "value"}'
    parsed = safe_json_loads(json_str)
    assert parsed == data

    # Test string truncation
    text = "Hello, World!"
    truncated = truncate_string(text, 8)
    assert len(truncated) <= 8

    # Test filename sanitization
    filename = sanitize_filename("test<>:file.txt")
    assert "<" not in filename
    assert ">" not in filename

    # Test sensitive data masking
    masked = mask_sensitive_data("sk-1234567890abcdef", 4)
    assert masked.startswith("sk-1")
    assert "*" in masked

    # Test email validation
    assert validate_email("test@example.com")
    assert not validate_email("invalid-email")

    print("✓ Utility functions test passed")


def test_dependencies():
    """Test FastAPI dependencies"""
    print("Testing dependencies...")
    from runtime.core.dependencies import (
        get_settings,
        pagination_params
    )

    # These are async functions, so we just check they exist
    assert get_settings is not None
    assert pagination_params is not None

    print("✓ Dependencies test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("Running Backend Component Tests")
    print("=" * 50 + "\n")

    try:
        test_settings()
        test_database_config()
        test_websocket_manager()
        test_utils()
        test_dependencies()

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50 + "\n")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
