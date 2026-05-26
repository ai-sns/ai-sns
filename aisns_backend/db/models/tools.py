"""Tool management ORM models (Plugin, Function, MCP, Skill)."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from db.base import Base
from runtime.shared import debug_info


class PluginMng(Base):
    """Plugin management model."""
    __tablename__ = 'pluginmng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    plugin_id = Column(String(100), doc="Plugin ID")
    company = Column(String(200), doc="Company")
    company_abbr = Column(String(100), doc="Company abbreviation")
    name = Column(String(100), doc="Name")
    version = Column(String(100), doc="Version")
    alias_name = Column(String(100), doc="Alias name")
    filename = Column(String(200), doc="Filename")
    run_mode = Column(String(100), doc="Run mode")
    run_scope = Column(String(100), doc="Run scope")
    instruction = Column(String(100), doc="Instruction")
    runtime_main = Column(String(200), doc="Runtime main")
    runtime_test = Column(String(200), doc="Runtime test")
    description = Column(Text, doc="Description")
    plugin_directory = Column(String(100), doc="Plugin directory")
    plugin_type = Column(String(100), doc="Plugin type")
    plugin_executed = Column(String(100), doc="Plugin executed")
    plugin_event = Column(String(100), doc="Plugin event")
    plugin_title = Column(Text, doc="Plugin title")
    detail = Column(Text, doc="Detail")
    parameter = Column(Text, doc="Parameter schema (JSON)")
    confirm_needed = Column(Boolean, default=True, doc="Confirm needed")
    can_be_sold = Column(Boolean, default=False, doc="Can be sold")
    used_in_sns = Column(Boolean, default=False, doc="Used in SNS")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class FunctionMng(Base):
    """Function management model."""
    __tablename__ = 'function_mng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    function_id = Column(String(100), doc="Function ID")
    name = Column(String(100), doc="Name")
    instruction = Column(String(100), doc="Instruction")
    file_path = Column(String(200), doc="File path")
    requirement = Column(Text, doc="Requirement")
    parameter = Column(Text, doc="Parameter")
    description = Column(String(100), doc="Description")
    detail = Column(Text, doc="Detail")
    function_type = Column(String(100), doc="Function type")
    function_event = Column(String(100), doc="Function event")
    confirm_needed = Column(Boolean, default=True, doc="Confirm needed")
    can_be_sold = Column(Boolean, default=False, doc="Can be sold")
    used_in_sns = Column(Boolean, default=False, doc="Used in SNS")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class McpMng(Base):
    """MCP management model."""
    __tablename__ = 'mcp_mng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mcp_id = Column(String(100), doc="MCP ID")
    name = Column(String(100), doc="Name")
    instruction = Column(String(100), doc="Instruction")
    file_path = Column(String(200), doc="File path")
    requirement = Column(Text, doc="Requirement")
    parameter = Column(Text, doc="Parameter")
    description = Column(String(100), doc="Description")
    detail = Column(Text, doc="Detail")
    mcp_type = Column(String(100), doc="MCP type")
    mcp_event = Column(String(100), doc="MCP event")
    confirm_needed = Column(Boolean, default=True, doc="Confirm needed")
    can_be_sold = Column(Boolean, default=False, doc="Can be sold")
    used_in_sns = Column(Boolean, default=False, doc="Used in SNS")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class SkillMng(Base):
    """Skill management model."""
    __tablename__ = 'skill_mng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(String(100), doc="Skill ID")
    name = Column(String(100), doc="Name")
    instruction = Column(String(100), doc="Instruction")
    file_path = Column(String(200), doc="File path")
    requirement = Column(Text, doc="Requirement")
    parameter = Column(Text, doc="Parameter")
    description = Column(String(100), doc="Description")
    detail = Column(Text, doc="Detail")
    skill_type = Column(String(100), doc="Skill type")
    skill_event = Column(String(100), doc="Skill event")
    confirm_needed = Column(Boolean, default=True, doc="Confirm needed")
    can_be_sold = Column(Boolean, default=False, doc="Can be sold")
    used_in_sns = Column(Boolean, default=False, doc="Used in SNS")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
