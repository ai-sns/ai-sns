# -*- coding: utf-8 -*-
"""
KM module - Service layer
"""
import logging
from typing import List, Dict, Any
from pathlib import Path

from db.DBFactory import (
    query_KMCfg_All,
    add_KMCfg,
    update_KMCfg,
    delete_KMCfg
)

logger = logging.getLogger(__name__)


class KMService:
    """Service for managing knowledge bases"""

    @staticmethod
    def get_all_knowledge_bases() -> List[Dict[str, Any]]:
        """Get all knowledge bases"""
        kbs = query_KMCfg_All()
        result = []
        for kb in kbs:
            result.append({
                "id": kb.id,
                "name": getattr(kb, 'name', ''),
                "description": getattr(kb, 'description', ''),
                "km_type": getattr(kb, 'km_type', 'vector'),
                "path": getattr(kb, 'path', '')
            })
        return result

    @staticmethod
    def create_knowledge_base(**kwargs) -> int:
        """Create a new knowledge base"""
        kb_id = add_KMCfg(**kwargs)
        return kb_id

    @staticmethod
    def update_knowledge_base(kb_id: int, **kwargs) -> None:
        """Update knowledge base configuration"""
        update_KMCfg(kb_id, **kwargs)

    @staticmethod
    def delete_knowledge_base(kb_id: int) -> None:
        """Delete a knowledge base"""
        delete_KMCfg(kb_id)

    @staticmethod
    def save_uploaded_file(kb_id: int, filename: str, content: bytes) -> Path:
        """
        Save uploaded file to knowledge base directory

        Args:
            kb_id: Knowledge base ID
            filename: File name
            content: File content

        Returns:
            Path to saved file
        """
        upload_dir = Path(f"km/uploads/{kb_id}")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path
