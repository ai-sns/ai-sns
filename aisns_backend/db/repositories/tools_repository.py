"""Tool management repository with specialized CRUD operations."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc, asc, or_
from .base import BaseRepository
from db.models.tools import PluginMng, FunctionMng, McpMng, SkillMng
from db.database import get_db_session as get_session
from db.write_queue import db_write
from runtime.shared import debug_info


# ==================== Plugin Management ====================

class PluginMngRepository(BaseRepository[PluginMng]):
    """Plugin management repository."""

    def __init__(self):
        super().__init__(PluginMng)

    def get_all_tools(self, **kwargs) -> List[PluginMng]:
        """Get all tool plugins."""
        session = get_session()
        try:
            query = session.query(self.model)
            plugin_types = ["Tool_Headless", "Tool_Gui"]
            query = query.filter(or_(PluginMng.plugin_type == pt for pt in plugin_types))

            if kwargs:
                query = query.filter_by(**kwargs)

            return query.order_by(desc(PluginMng.run_mode)).all()
        finally:
            session.close()

    def get_search_tools(self, **kwargs) -> List[PluginMng]:
        """Get search tool plugins."""
        session = get_session()
        try:
            query = session.query(self.model)
            plugin_types = ["Tool_Headless", "Tool_Gui"]
            query = query.filter(or_(PluginMng.plugin_type == pt for pt in plugin_types))
            query = query.filter(PluginMng.plugin_event.contains("search_before_ask"))

            if kwargs:
                query = query.filter_by(**kwargs)

            return query.order_by(desc(PluginMng.run_mode)).all()
        finally:
            session.close()

    def copy_plugin(self, plugin_id: str, new_plugin_id: str, **kwargs) -> Optional[PluginMng]:
        """Copy plugin record."""
        def _do(session):
            record_to_copy = session.query(PluginMng).filter_by(plugin_id=plugin_id).first()
            if not record_to_copy:
                return None
            new_record = PluginMng(
                plugin_id=new_plugin_id,
                company=kwargs.get('company', record_to_copy.company),
                company_abbr=kwargs.get('company_abbr', record_to_copy.company_abbr),
                name=kwargs.get('name', record_to_copy.name),
                version=kwargs.get('version', record_to_copy.version),
                alias_name=kwargs.get('alias_name', record_to_copy.alias_name),
                filename=kwargs.get('filename', record_to_copy.filename),
                run_mode=kwargs.get('run_mode', record_to_copy.run_mode),
                run_scope=kwargs.get('run_scope', record_to_copy.run_scope),
                instruction=kwargs.get('instruction', record_to_copy.instruction),
                runtime_main=kwargs.get('runtime_main', record_to_copy.runtime_main),
                runtime_test=kwargs.get('runtime_test', record_to_copy.runtime_test),
                description=kwargs.get('description', record_to_copy.description),
                plugin_directory=kwargs.get('plugin_directory', record_to_copy.plugin_directory),
                plugin_type=kwargs.get('plugin_type', record_to_copy.plugin_type),
                plugin_executed=kwargs.get('plugin_executed', record_to_copy.plugin_executed),
                plugin_event=kwargs.get('plugin_event', record_to_copy.plugin_event),
                plugin_title=kwargs.get('plugin_title', record_to_copy.plugin_title),
                detail=kwargs.get('detail', record_to_copy.detail),
                creator=kwargs.get('creator', record_to_copy.creator),
                is_delete=record_to_copy.is_delete,
                create_time=datetime.now()
            )
            session.add(new_record)
            return new_record
        return db_write(_do, description="repo_copy_plugin")


# ==================== Function Management ====================

class FunctionMngRepository(BaseRepository[FunctionMng]):
    """Function management repository."""

    def __init__(self):
        super().__init__(FunctionMng)

    def create_with_id(self, **kwargs) -> int:
        """Create function and return its ID."""
        _model = self.model
        def _do(session):
            func = _model(**kwargs)
            session.add(func)
            session.flush()
            return func.id
        return db_write(_do, description="repo_create_function_mng")

    def update_by_function_id(self, function_id: str, **kwargs):
        """Update function by function_id."""
        self.update_by_filter({'function_id': function_id}, **kwargs)


# ==================== MCP Management ====================

class McpMngRepository(BaseRepository[McpMng]):
    """MCP management repository."""

    def __init__(self):
        super().__init__(McpMng)

    def create_with_id(self, **kwargs) -> int:
        """Create MCP and return its ID."""
        _model = self.model
        def _do(session):
            mcp = _model(**kwargs)
            session.add(mcp)
            session.flush()
            return mcp.id
        return db_write(_do, description="repo_create_mcp_mng")

    def update_by_mcp_id(self, mcp_id: str, **kwargs):
        """Update MCP by mcp_id."""
        self.update_by_filter({'mcp_id': mcp_id}, **kwargs)


# ==================== Skill Management ====================

class SkillMngRepository(BaseRepository[SkillMng]):
    """Skill management repository."""

    def __init__(self):
        super().__init__(SkillMng)

    def create_with_id(self, **kwargs) -> int:
        """Create skill and return its ID."""
        _model = self.model
        def _do(session):
            skill = _model(**kwargs)
            session.add(skill)
            session.flush()
            return skill.id
        return db_write(_do, description="repo_create_skill_mng")

    def update_by_skill_id(self, skill_id: str, **kwargs):
        """Update skill by skill_id."""
        self.update_by_filter({'skill_id': skill_id}, **kwargs)
