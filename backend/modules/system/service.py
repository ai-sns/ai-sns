# -*- coding: utf-8 -*-
"""
System module - Service layer
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

import os
from pathlib import Path

import httpx
from PIL import Image

from db.DBFactory import query_SystemCfg, update_SystemCfg
from backend.config.settings import get_settings
from backend.database.repositories import WebMngRepository, SystemInitRepository, AiChatCfgRepository
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


class SystemInitWizardService:
    def __init__(self):
        self.system_init_repo = SystemInitRepository()
        self.ai_chat_cfg_repo = AiChatCfgRepository()

    @staticmethod
    def _get_first_record() -> Any:
        repo = SystemInitRepository()
        records = repo.get_all(is_delete=False)
        return records[0] if records else None

    @staticmethod
    def _split_map_value(value: str, map_type: str) -> str:
        if not value:
            return ""
        parts = value.split(',')
        if map_type == "Google":
            if len(parts) >= 1 and parts[0] != "N/A":
                return parts[0]
            return ""
        if len(parts) >= 2 and parts[1] not in ("N/A", "do_not_need_map_id"):
            return parts[1]
        if len(parts) >= 2 and parts[1] == "do_not_need_map_id":
            return "do_not_need_map_id"
        return ""

    @staticmethod
    def _combine_map_values(map_type: str, map_api_key: str, map_id: str) -> Dict[str, str]:
        map_api_key = (map_api_key or "").strip()
        map_id = (map_id or "").strip()
        if map_type == "Google":
            return {
                "map_api_key": f"{map_api_key},N/A",
                "map_id": f"{map_id},N/A",
            }
        return {
            "map_api_key": f"N/A,{map_api_key}",
            "map_id": "N/A,do_not_need_map_id",
        }

    def get_draft(self) -> Dict[str, Any]:
        record = self._get_first_record()
        if not record:
            return {}

        map_type = record.map or "Google"
        return {
            "id": record.id,
            "name": record.name,
            "avatar": record.avatar,
            "password": record.password,
            "confirm_password": record.confirm_password,
            "profile": record.profile,
            "llm": record.llm,
            "llm_server": record.llm_server,
            "api_key": record.api_key,
            "avatar3d": record.avatar3d,
            "account": record.account,
            "account_password": record.account_password,
            "sns_url": record.sns_url,
            "map": map_type,
            "map_api_key": self._split_map_value(record.map_api_key, map_type),
            "map_id": self._split_map_value(record.map_id, map_type),
            "status": record.status,
        }

    def save_draft(self, data: Dict[str, Any]) -> Dict[str, Any]:
        record = self._get_first_record()

        map_type = data.get("map") or (record.map if record else "Google") or "Google"
        combined = self._combine_map_values(map_type, data.get("map_api_key") or "", data.get("map_id") or "")

        payload = {
            "name": data.get("name"),
            "avatar": data.get("avatar"),
            "password": data.get("password"),
            "confirm_password": data.get("confirm_password"),
            "profile": data.get("profile"),
            "llm": data.get("llm"),
            "llm_server": data.get("llm_server"),
            "api_key": data.get("api_key"),
            "avatar3d": data.get("avatar3d"),
            "account": data.get("account"),
            "account_password": data.get("account_password"),
            "sns_url": data.get("sns_url"),
            "map": map_type,
            "map_api_key": combined["map_api_key"],
            "map_id": combined["map_id"],
            "status": 0,
            "is_delete": False,
        }

        if record:
            self.system_init_repo.update(record.id, **payload)
            return {"id": record.id}
        created = self.system_init_repo.create(**payload)
        return {"id": created.id}

    def list_avatar3d(self, request_base_url: str) -> List[Dict[str, str]]:
        base = request_base_url.rstrip('/')
        folder = Path("scripts") / "avatar3d"
        if not folder.exists():
            return []

        glb_files = {p.stem: p.name for p in folder.glob("*.glb")}
        png_files = {p.stem: p.name for p in folder.glob("*.png")}

        keys = sorted(set(glb_files.keys()) & set(png_files.keys()))
        return [
            {
                "key": key,
                "png_url": f"{base}/scripts/avatar3d/{png_files[key]}",
                "glb_url": f"{base}/scripts/avatar3d/{glb_files[key]}",
            }
            for key in keys
        ]

    @staticmethod
    def _save_uploaded_avatar(file_bytes: bytes, filename: str) -> str:
        avatars_dir = Path("images") / "avatars"
        avatars_dir.mkdir(parents=True, exist_ok=True)
        file_path = avatars_dir / filename
        file_path.write_bytes(file_bytes)
        return filename

    @staticmethod
    def _generate_avatar_map(avatar_filename: str) -> str:
        avatars_dir = Path("images") / "avatars"
        avatar_path = avatars_dir / avatar_filename
        if not avatar_path.exists():
            raise FileNotFoundError(str(avatar_path))

        pin_path = Path("images") / "pin.png"
        if not pin_path.exists():
            pin_path = Path("pin.png")
        if not pin_path.exists():
            raise FileNotFoundError(str(pin_path))

        pin = Image.open(pin_path).convert("RGBA")
        avatar = Image.open(avatar_path).convert("RGBA")

        avatar = avatar.resize((70, 70), Image.LANCZOS)
        composite = Image.new("RGBA", pin.size, (0, 0, 0, 0))
        composite.paste(pin, (0, 0), pin)
        composite.paste(avatar, (1, 2), avatar)

        scaled = composite.resize((pin.size[0] // 2, pin.size[1] // 2), Image.LANCZOS)
        name_without_ext, _ext = os.path.splitext(avatar_filename)
        map_filename = f"{name_without_ext}_map.png"
        out_path = avatars_dir / map_filename
        scaled.save(out_path, format="PNG", optimize=True)
        return map_filename

    def upload_avatar(self, file_bytes: bytes, file_extension: str) -> Dict[str, str]:
        import uuid

        ext = (file_extension or "").lower()
        if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
            ext = ".png"

        filename = f"{uuid.uuid4()}{ext}"
        avatar_filename = self._save_uploaded_avatar(file_bytes, filename)
        avatar_map_filename = self._generate_avatar_map(avatar_filename)
        return {
            "avatar": avatar_filename,
            "avatar_map": avatar_map_filename,
        }

    async def fetch_captcha(self) -> Dict[str, Any]:
        url = "http://www.ai-sns.org/api/captcha/"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return {
                "captcha_id": resp.headers.get("X-Captcha-ID", ""),
                "content": resp.content,
                "content_type": resp.headers.get("content-type", "image/png"),
            }

    async def register_remote(self, data: Dict[str, Any], avatar_map_filename: str) -> Dict[str, Any]:
        avatars_dir = Path("images") / "avatars"
        avatar_map_path = avatars_dir / avatar_map_filename
        if not avatar_map_path.exists():
            raise FileNotFoundError(str(avatar_map_path))

        register_url = "http://www.ai-sns.org/api/register/"
        files = {"avatar_file": (avatar_map_path.name, avatar_map_path.read_bytes(), "image/png")}

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(register_url, data=data, files=files)
            if resp.status_code not in (200, 201):
                raise ValueError(f"Remote register failed: {resp.status_code} - {resp.text}")
            return resp.json()

    def submit(self, draft: Dict[str, Any], nation_id: str) -> None:
        record = self._get_first_record()
        if not record:
            raise ValueError("SystemInit not found")
        self.system_init_repo.update(record.id, status=1)

        sns_record = self.ai_chat_cfg_repo.get_map_config()
        if sns_record:
            map_type_text = draft.get("map") or record.map or "Google"
            map_type_value = "0" if map_type_text == "Google" else "1"
            combined = self._combine_map_values(map_type_text, draft.get("map_api_key") or "", draft.get("map_id") or "")
            self.ai_chat_cfg_repo.update(
                sns_record.id,
                nationid=nation_id,
                avatar=record.avatar,
                name=record.name,
                nationpassword=record.password,
                sign=record.profile,
                avatar3d=record.avatar3d,
                account=record.account,
                password=record.account_password,
                sns_url=record.sns_url,
                map_type=map_type_value,
                map_api_key=combined["map_api_key"],
                map_id=combined["map_id"],
            )
