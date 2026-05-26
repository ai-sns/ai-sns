# -*- coding: utf-8 -*-
"""
KM module - Dependencies
"""
from .service import KMService
from runtime.shared import debug_info


def get_km_service() -> KMService:
    """Get KM service instance"""
    return KMService()
