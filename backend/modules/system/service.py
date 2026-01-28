# -*- coding: utf-8 -*-
"""
System module - Service layer
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from db.DBFactory import query_SystemCfg, update_SystemCfg
from backend.config.settings import get_settings
from backend.database.repositories import WebMngRepository
from backend.database.models.system import WebMng

logger = logging.getLogger(__name__)


class SystemService:
    """Service for managing system configuration"""

    def __init__(self):
        self.web_mng_repo = WebMngRepository()

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

    def get_web_mng(self) -> List[Dict[str, Any]]:
        """Get all web management items"""
        items = self.web_mng_repo.get_all_ordered(is_delete=False)
        return [
            {
                "id": item.id,
                "web_id": item.web_id,
                "name": item.name,
                "title": item.title,
                "type": item.type,
                "description": item.description,
                "filename": item.filename,
                "url": item.url,
                "position": item.position,
                "creator": item.creator,
                "is_delete": item.is_delete,
                "create_time": item.create_time.isoformat() if item.create_time else None
            }
            for item in items
        ]

    def create_web_mng(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new web management item"""
        import random
        import string

        # Generate web_id if not provided
        if 'web_id' not in data:
            data['web_id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

        # Set defaults
        data.setdefault('position', 999)
        data.setdefault('creator', 'User')
        data.setdefault('is_delete', False)
        data.setdefault('create_time', datetime.now())

        item = self.web_mng_repo.create(**data)

        return {
            "id": item.id,
            "web_id": item.web_id,
            "name": item.name,
            "type": item.type,
            "url": item.url
        }

    def update_web_mng(self, item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update web management item"""
        # Remove fields that shouldn't be updated
        data.pop('id', None)
        data.pop('web_id', None)
        data.pop('create_time', None)

        self.web_mng_repo.update(item_id, **data)
        item = self.web_mng_repo.get_by_id(item_id)

        return {
            "id": item.id,
            "web_id": item.web_id,
            "name": item.name,
            "title": item.title,
            "type": item.type,
            "description": item.description,
            "filename": item.filename,
            "url": item.url,
            "position": item.position
        }

    def delete_web_mng(self, item_id: int) -> None:
        """Delete web management item (soft delete)"""
        self.web_mng_repo.update(item_id, is_delete=True)

    def reorder_web_mng(self, items: List[Dict[str, Any]]) -> None:
        """Reorder web management items"""
        for item in items:
            item_id = item.get('id')
            position = item.get('position')
            if item_id is not None and position is not None:
                self.web_mng_repo.update(item_id, position=position)
