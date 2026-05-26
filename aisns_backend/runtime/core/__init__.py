"""
Core package - Essential application components
"""
from .dependencies import get_current_user, get_db_session
from runtime.shared import debug_info

__all__ = ["get_current_user", "get_db_session"]
