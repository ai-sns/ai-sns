# -*- coding: utf-8 -*-
"""
KM module - Dependencies
"""
from .service import KMService


def get_km_service() -> KMService:
    """Get KM service instance"""
    return KMService()
