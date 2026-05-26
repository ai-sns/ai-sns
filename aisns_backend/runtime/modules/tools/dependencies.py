# -*- coding: utf-8 -*-
"""
Tools module - FastAPI dependencies
"""
from .service import ToolsService
from runtime.shared import debug_info


def get_tools_service() -> ToolsService:
    """Get tools service instance

    Service manages its own database sessions internally.
    """
    return ToolsService()
