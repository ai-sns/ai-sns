"""Agent repository with specialized CRUD operations."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session
from .base import BaseRepository
from db.models.agent import AgentCfg, AgentTools, Prompt, LLMConfig, RoleConfig
from db.database import get_db_session as get_session
from db.write_queue import db_write
from runtime.shared import debug_info

logger = logging.getLogger(__name__)


# ==================== Agent Config ====================

class AgentCfgRepository(BaseRepository[AgentCfg]):
    """Agent configuration repository."""

    def __init__(self):
        super().__init__(AgentCfg)

    def get_all_ordered(self, **filters) -> List[AgentCfg]:
        """Get all agents ordered by position."""
        session = get_session()
        try:
            return session.query(self.model).filter_by(**filters).order_by(asc(AgentCfg.position)).all()
        finally:
            session.close()

    def get_system_prompt(self, name: str) -> Optional[str]:
        """Get agent system prompt by name."""
        session = get_session()
        try:
            agent = session.query(self.model).filter_by(name=name).first()
            return agent.prompt if agent else None
        finally:
            session.close()

    def get_specialization(self, name: str) -> Optional[str]:
        """Get agent specialization by name."""
        session = get_session()
        try:
            agent = session.query(self.model).filter_by(name=name).first()
            return agent.specialization if agent else None
        finally:
            session.close()


# ==================== Agent Tools ====================

class AgentToolsRepository:
    """Repository for agent_tools table"""

    def __init__(self, db: Session):
        self.db = db

    def _row_to_dict(self, row: AgentTools) -> Dict[str, Any]:
        """Convert an ORM row to a plain dict."""
        return {
            "id": row.id,
            "agent_id": row.agent_id,
            "tool_type": row.tool_type,
            "tool_id": row.tool_id,
            "enabled": row.enabled,
            "priority": row.priority,
            "create_time": row.create_time,
        }

    def get_agent_tools(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get all tools associated with an agent"""
        try:
            rows = (
                self.db.query(AgentTools)
                .filter(AgentTools.agent_id == agent_id, AgentTools.enabled == 1)
                .order_by(desc(AgentTools.priority), asc(AgentTools.create_time))
                .all()
            )
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to get agent tools: {e}")
            return []

    def add_agent_tool(self, agent_id: int, tool_type: str, tool_id: str, enabled: int = 1, priority: int = 0) -> bool:
        """Add a tool to an agent"""
        try:
            existing = (
                self.db.query(AgentTools)
                .filter_by(agent_id=agent_id, tool_type=tool_type, tool_id=tool_id)
                .first()
            )
            if existing:
                logger.warning(f"Tool {tool_type}/{tool_id} already associated with agent {agent_id}")
                return False

            _agent_id = agent_id
            _tool_type = tool_type
            _tool_id = tool_id
            _enabled = enabled
            _priority = priority

            def _do(session):
                record = AgentTools(
                    agent_id=_agent_id,
                    tool_type=_tool_type,
                    tool_id=_tool_id,
                    enabled=_enabled,
                    priority=_priority,
                )
                session.add(record)

            db_write(_do, description="agent_tools_add")
            logger.info(f"Added tool {tool_type}/{tool_id} to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add agent tool: {e}")
            return False

    def remove_agent_tool(self, agent_id: int, tool_type: str, tool_id: str) -> bool:
        """Remove a tool from an agent"""
        try:
            _agent_id = agent_id
            _tool_type = tool_type
            _tool_id = tool_id

            def _do(session):
                record = (
                    session.query(AgentTools)
                    .filter_by(agent_id=_agent_id, tool_type=_tool_type, tool_id=_tool_id)
                    .first()
                )
                if record:
                    session.delete(record)
                    return True
                return False

            result = db_write(_do, description="agent_tools_remove")
            if result:
                logger.info(f"Removed tool {tool_type}/{tool_id} from agent {agent_id}")
                return True
            logger.warning(f"Tool {tool_type}/{tool_id} not found for agent {agent_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to remove agent tool: {e}")
            return False

    def clear_agent_tools(self, agent_id: int) -> bool:
        """Remove all tools from an agent"""
        try:
            _agent_id = agent_id

            def _do(session):
                records = session.query(AgentTools).filter_by(agent_id=_agent_id).all()
                for r in records:
                    session.delete(r)

            db_write(_do, description="agent_tools_clear")
            logger.info(f"Cleared all tools from agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear agent tools: {e}")
            return False

    def update_tool_priority(self, agent_id: int, tool_type: str, tool_id: str, priority: int) -> bool:
        """Update tool priority"""
        try:
            _agent_id = agent_id
            _tool_type = tool_type
            _tool_id = tool_id
            _priority = priority

            def _do(session):
                record = (
                    session.query(AgentTools)
                    .filter_by(agent_id=_agent_id, tool_type=_tool_type, tool_id=_tool_id)
                    .first()
                )
                if record:
                    record.priority = _priority
                    return True
                return False

            result = db_write(_do, description="agent_tools_update_priority")
            if result:
                logger.info(f"Updated priority for tool {tool_type}/{tool_id} in agent {agent_id}")
                return True
            logger.warning(f"Tool {tool_type}/{tool_id} not found for agent {agent_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to update tool priority: {e}")
            return False

    def toggle_tool_enabled(self, agent_id: int, tool_type: str, tool_id: str, enabled: bool) -> bool:
        """Enable or disable a tool"""
        try:
            _agent_id = agent_id
            _tool_type = tool_type
            _tool_id = tool_id
            _enabled = 1 if enabled else 0

            def _do(session):
                record = (
                    session.query(AgentTools)
                    .filter_by(agent_id=_agent_id, tool_type=_tool_type, tool_id=_tool_id)
                    .first()
                )
                if record:
                    record.enabled = _enabled
                    return True
                return False

            result = db_write(_do, description="agent_tools_toggle_enabled")
            if result:
                logger.info(f"{'Enabled' if enabled else 'Disabled'} tool {tool_type}/{tool_id} for agent {agent_id}")
                return True
            logger.warning(f"Tool {tool_type}/{tool_id} not found for agent {agent_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to toggle tool enabled: {e}")
            return False


# ==================== Prompt ====================

class PromptRepository(BaseRepository[Prompt]):
    """Prompt repository."""

    def __init__(self):
        super().__init__(Prompt)

    def get_by_title(self, title: str) -> Optional[str]:
        """Get prompt content by title."""
        session = get_session()
        try:
            prompt = session.query(self.model).filter_by(title=title).first()
            return prompt.content if prompt else None
        finally:
            session.close()

    def get_content_by_id(self, id: int) -> Optional[str]:
        """Get prompt content by ID."""
        session = get_session()
        try:
            prompt = session.query(self.model).filter_by(id=id).first()
            return prompt.content if prompt else None
        finally:
            session.close()

    def get_all_ordered(self, **kwargs) -> List[Prompt]:
        """Get all prompts ordered by ID desc."""
        session = get_session()
        try:
            filter_expr = [getattr(self.model, key) == value for key, value in kwargs.items()]
            return session.query(self.model).filter(*filter_expr).order_by(desc(Prompt.id)).all()
        finally:
            session.close()

    def get_by_model_name(self, model_name: str) -> List[Prompt]:
        """Get prompts by model name (including empty/null)."""
        session = get_session()
        try:
            return session.query(self.model).filter(
                (Prompt.model_name == model_name) |
                (Prompt.model_name.is_(None)) |
                (Prompt.model_name == '')
            ).all()
        finally:
            session.close()


# ==================== LLM Config ====================

class LLMConfigRepository(BaseRepository[LLMConfig]):
    """LLM config repository."""

    def __init__(self):
        super().__init__(LLMConfig)


# ==================== Role Config ====================

class RoleConfigRepository(BaseRepository[RoleConfig]):
    """Role config repository."""

    def __init__(self):
        super().__init__(RoleConfig)
