# -*- coding: utf-8 -*-
"""
Chat module - Service layer
"""
import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from db.DBFactory import (
    query_AISnsCfg_All,
    add_AISnsCfg,
    query_AIChatMessages_All as query_AIChatMessages,
    add_AIChatMessages as add_AIChatMessage
)

from db.repositories import AIChatMessagesRepository
from runtime.modules.agent.llm_service import LLMConfigService
from runtime.shared.llm_endpoints import normalize_openai_base_url

logger = logging.getLogger(__name__)

# Agent instances management
agent_instances: Dict[str, Any] = {}


class ChatService:
    """Service for managing chat functionality"""

    def __init__(self):
        self._chat_repo = AIChatMessagesRepository()

    @staticmethod
    def get_ai_config():
        """
        Get AI configuration.
        Priority: Default LLM Config (DB) > Environment Variables > Defaults
        """
        # 1. Try to load from default LLM config in database
        try:
            default_cfg = LLMConfigService().get_default_config()
            if default_cfg and default_cfg.get('api_key'):
                raw_endpoint = default_cfg.get('api_endpoint') or 'https://api.openai.com/v1'
                api_base = normalize_openai_base_url(raw_endpoint)
                logger.info("Using AI config from default LLM config")
                return {
                    "api_base": api_base,
                    "api_key": default_cfg['api_key'],
                    "provider": default_cfg.get('provider'),
                    "model": default_cfg.get('model_name', 'gpt-4o-mini'),
                    "temperature": default_cfg.get('temperature', 0.7),
                    "max_tokens": default_cfg.get('max_tokens', 2048)
                }
        except Exception as e:
            logger.warning(f"Failed to load default LLM config: {e}")

        # 2. Try to load from environment variables
        if os.environ.get('OPENAI_API_KEY'):
            logger.info("Using AI config from environment variables")
            return {
                "api_base": os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
                "api_key": os.environ.get('OPENAI_API_KEY'),
                "model": os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                "temperature": float(os.environ.get('OPENAI_TEMPERATURE', '1.0')),
                "max_tokens": int(os.environ.get('OPENAI_MAX_TOKENS', '4096'))
            }

        # 3. Default configuration (no valid source found)
        logger.error("No valid AI config found! Please configure a default LLM in Settings.")
        return {
            "api_base": 'https://api.openai.com/v1',
            "api_key": '',
            "model": 'gpt-4o-mini',
            "temperature": 1.0,
            "max_tokens": 4096
        }

    @staticmethod
    def get_all_ai_chat_configs() -> List[Dict[str, Any]]:
        """Get all AI chat configurations"""
        configs = query_AISnsCfg_All(is_delete=0)
        result = []
        for cfg in configs:
            result.append({
                "id": cfg.id,
                "name": getattr(cfg, 'name', ''),
                "model": getattr(cfg, 'model', 'gpt-4'),
                "api_base": getattr(cfg, 'api_base', ''),
                "temperature": getattr(cfg, 'temperature', 0.7)
            })
        return result

    @staticmethod
    def create_ai_chat_config(**kwargs) -> int:
        """Create AI chat configuration"""
        config_id = add_AISnsCfg(**kwargs)
        return config_id

    @staticmethod
    async def send_chat_message(
        agent_id: int,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send chat message and get response"""
        # Get or create Agent instance
        agent_key = f"agent_{agent_id}"
        if agent_key not in agent_instances:
            from Agent import Agent
            agent_instances[agent_key] = Agent()

        agent = agent_instances[agent_key]

        # Send message and get reply
        response = await asyncio.to_thread(
            agent.chat,
            message,
            conversation_id
        )

        # Save messages to database
        add_AIChatMessage(
            agent_id=agent_id,
            role="user",
            content=message,
            conversation_id=conversation_id
        )
        add_AIChatMessage(
            agent_id=agent_id,
            role="assistant",
            content=response,
            conversation_id=conversation_id
        )

        return {
            "response": response,
            "conversation_id": conversation_id
        }

    @staticmethod
    def get_chat_history(
        agent_id: int,
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get chat history"""
        messages = query_AIChatMessages(
            limit=None,  # Fetch all messages
            agent_id=agent_id,
            conversation_id=conversation_id
        )
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": str(msg.timestamp) if hasattr(msg, 'timestamp') else None
            })
        return result

    @staticmethod
    def get_conversations(limit: int = 50, agent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation list (ordered by last message time)

        Args:
            limit: Maximum number of conversations to return
            agent_id: Filter by agent ID (optional)

        Returns:
            List of conversations with title and last message time
        """
        try:
            repo = AIChatMessagesRepository()
            rows = repo.get_conversation_summaries(limit=limit, agent_id=agent_id)
            for r in rows:
                if r.get('last_message_time') is not None:
                    r['last_message_time'] = r['last_message_time'].isoformat()
                if r.get('stick_time') is not None:
                    r['stick_time'] = r['stick_time'].isoformat()
            return rows
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []

    def delete_conversation(self, conversation_id: str) -> int:
        return self._chat_repo.soft_delete_conversation(conversation_id)

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        return self._chat_repo.update_conversation_title(conversation_id, title)

    def toggle_conversation_pin(self, conversation_id: str) -> Dict[str, Any]:
        found, dt = self._chat_repo.toggle_conversation_pin(conversation_id)
        return {
            'found': bool(found),
            'stick_time': dt.isoformat() if dt is not None else None
        }

    def update_conversation_tag(self, conversation_id: str, tag: Optional[str]) -> bool:
        return self._chat_repo.update_conversation_tag(conversation_id, tag)

    def get_conversation_tag_stats(self, agent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._chat_repo.get_tag_stats(agent_id=agent_id)

    @staticmethod
    def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation

        Args:
            conversation_id: The conversation ID

        Returns:
            List of messages in chronological order
        """
        try:
            messages = query_AIChatMessages(
                limit=None,  # Fetch all messages
                conversation_id=conversation_id,
                is_delete=False
            )

            result = []
            for msg in messages:
                # Determine role from flag (0=user, 1=assistant)
                role = "user" if msg.flag == 0 else "assistant"

                attachments = []
                try:
                    if getattr(msg, 'attachment_list', None):
                        raw = json.loads(msg.attachment_list)
                        if isinstance(raw, list):
                            attachments = [
                                {
                                    'id': a.get('id'),
                                    'name': a.get('name'),
                                    'size': a.get('size'),
                                    'type': a.get('type')
                                }
                                for a in raw
                                if isinstance(a, dict)
                            ]
                except Exception:
                    attachments = []

                result.append({
                    "id": msg.id,
                    "role": role,
                    "content": msg.content,
                    "attachments": attachments,
                    "create_time": str(msg.create_time) if hasattr(msg, 'create_time') else None
                })

            # Sort by create_time
            result.sort(key=lambda x: x.get("create_time", ""))

            return result
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []

