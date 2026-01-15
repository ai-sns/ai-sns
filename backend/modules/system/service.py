# -*- coding: utf-8 -*-
"""
System module - Service layer
"""
import logging
from typing import Dict, Any

from db.DBFactory import query_SystemCfg, update_SystemCfg
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class SystemService:
    """Service for managing system configuration"""

    @staticmethod
    def get_system_config() -> Dict[str, Any]:
        """Get system configuration"""
        config = query_SystemCfg()
        settings = get_settings()

        return {
            "theme": getattr(config, 'theme', 'dark'),
            "language": getattr(config, 'language', 'zh'),
            "minirunontray": getattr(config, 'minirunontray', True),
            "tools": {
                "page_size": settings.tools.page_size
            }
        }

    @staticmethod
    def update_system_config(**kwargs) -> None:
        """Update system configuration"""
        update_SystemCfg(**kwargs)
