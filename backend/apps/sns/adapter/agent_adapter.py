"""Agent adapter for SNS module.

This file is intended as the customization point for how SNS talks to the Agent module.
"""

import logging
from typing import Optional, Callable, Dict, Any

from backend.modules.agent.agent_manager import agent_manager

logger = logging.getLogger(__name__)


class AgentAdapter:
    def __init__(self):
        self._command_status_agent_resolvers: Dict[str, Callable[..., Optional[str]]] = {}
        self._command_status_role_overrides: Dict[str, Callable[..., Dict[str, Any]]] = {}
        self._command_status_prompt_builders: Dict[str, Callable[..., str]] = {}
        self._register_builtin_handlers()

    def register_command_status_agent_resolver(self, command_status: str, resolver: Callable[..., Optional[str]]):
        self._command_status_agent_resolvers[command_status] = resolver

    def register_command_status_role_overrides(self, command_status: str, provider: Callable[..., Dict[str, Any]]):
        self._command_status_role_overrides[command_status] = provider

    def register_command_status_prompt_builder(self, command_status: str, builder: Callable[..., str]):
        self._command_status_prompt_builders[command_status] = builder

    def _register_builtin_handlers(self):
        self.register_command_status_agent_resolver(
            "moderation",
            self._moderation_agent_resolver,
        )
        self.register_command_status_role_overrides(
            "moderation",
            self._moderation_role_overrides,
        )
        self.register_command_status_prompt_builder(
            "moderation",
            self._moderation_prompt_builder,
        )

    # ===== moderation handlers =====

    def _moderation_agent_resolver(self, *, command_status, ai_chat_cfg):
        return "moderation_agent"

    def _moderation_role_overrides(self, *, command_status, ai_chat_cfg, agent):
        return {
            "temperature": 0.0,
            "style": "strict",
        }

    def _moderation_prompt_builder(
            self,
            *,
            command_status,
            system_role_prompt,
            original_prompt,
            ai_chat_cfg,
            agent,
    ):
        return f"MODERATION MODE:\n{original_prompt}"



    def get_agent_by_identifier(self, agent_identifier: str):
        if not agent_identifier:
            return None
        if str(agent_identifier).isdigit():
            return agent_manager.get_agent_by_id(int(agent_identifier))
        return agent_manager.get_agent_by_name(str(agent_identifier))

    def get_agent_identifier_for_command_status(self, *, command_status: str, ai_chat_cfg=None) -> Optional[str]:
        resolver = self._command_status_agent_resolvers.get(command_status)
        if resolver is None:
            return None
        try:
            return resolver(command_status=command_status, ai_chat_cfg=ai_chat_cfg)
        except Exception as e:
            logger.error(f"command_status resolver failed: {e}", exc_info=True)
            return None

    def get_role_config_overrides_for_command_status(
        self,
        *,
        command_status: str,
        ai_chat_cfg=None,
        agent=None,
    ) -> Dict[str, Any]:
        provider = self._command_status_role_overrides.get(command_status)
        if provider is None:
            return {}
        try:
            overrides = provider(command_status=command_status, ai_chat_cfg=ai_chat_cfg, agent=agent)
            return overrides if isinstance(overrides, dict) else {}
        except Exception as e:
            logger.error(f"command_status role overrides failed: {e}", exc_info=True)
            return {}

    def apply_role_config_overrides(self, *, agent, overrides: Dict[str, Any]):
        original = {}
        if not overrides:
            return lambda: None
        for key, value in overrides.items():
            original[key] = agent.role_config.get(key)
            agent.role_config[key] = value

        def _restore():
            for key, value in original.items():
                if value is None:
                    agent.role_config.pop(key, None)
                else:
                    agent.role_config[key] = value

        return _restore

    def get_agent_for_ai_chat_cfg(self, ai_chat_cfg, *, command_status: Optional[str] = None):
        if command_status:
            agent_identifier = self.get_agent_identifier_for_command_status(
                command_status=command_status,
                ai_chat_cfg=ai_chat_cfg,
            )
            if agent_identifier:
                agent = self.get_agent_by_identifier(agent_identifier)
                if agent is not None:
                    return agent
        agent_id = getattr(ai_chat_cfg, "agent_id", None)
        if not agent_id:
            return None
        return agent_manager.get_agent_by_id(agent_id)

    def build_conversation_id(self, *, prefix: str = "sns", suffix: str = "agent_conversation") -> str:
        return f"{prefix}_{suffix}"

    def build_system_prompt(
        self,
        *,
        system_role_prompt: str,
        original_prompt: str,
        ai_chat_cfg=None,
        command_status: Optional[str] = None,
        agent=None,
    ) -> str:
        if command_status:
            builder = self._command_status_prompt_builders.get(command_status)
            if builder is not None:
                try:
                    return builder(
                        command_status=command_status,
                        system_role_prompt=system_role_prompt,
                        original_prompt=original_prompt,
                        ai_chat_cfg=ai_chat_cfg,
                        agent=agent,
                    )
                except Exception as e:
                    logger.error(f"command_status prompt builder failed: {e}", exc_info=True)
        return system_role_prompt

    async def chat(
        self,
        *,
        agent,
        message: str,
        conversation_id: str,
        use_tools: Optional[bool] = None,
        use_memory: bool = False,
        use_knowledge_base: bool = False,
    ):
        kwargs = {
            "message": message,
            "conversation_id": conversation_id,
            "use_memory": use_memory,
            "use_knowledge_base": use_knowledge_base,
        }
        if use_tools is not None:
            kwargs["use_tools"] = use_tools
        return await agent.chat(**kwargs)
