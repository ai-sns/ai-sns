# -*- coding: utf-8 -*-
"""
Map module - Dependencies
"""
from .service import MapService
from .websocket import ConnectionManager, manager
from runtime.shared import debug_info


def get_map_service() -> MapService:
    """Get map service instance"""
    return MapService()


def get_connection_manager() -> ConnectionManager:
    """Get WebSocket connection manager instance"""
    return manager
