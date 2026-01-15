# -*- coding: utf-8 -*-
"""
Tools module - Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ==================== Plugin Schemas ====================

class PluginBase(BaseModel):
    """Plugin base schema"""
    name: str = Field(..., description="Plugin name")
    company: Optional[str] = Field(None, description="Company")
    company_abbr: Optional[str] = Field(None, description="Company abbreviation")
    version: Optional[str] = Field("1.0.0", description="Version")
    alias_name: Optional[str] = Field(None, description="Alias name")
    filename: Optional[str] = Field(None, description="Filename")
    run_mode: Optional[str] = Field(None, description="Run mode")
    run_scope: Optional[str] = Field(None, description="Run scope")
    instruction: Optional[str] = Field(None, description="Instruction")
    runtime_main: Optional[str] = Field(None, description="Runtime main")
    runtime_test: Optional[str] = Field(None, description="Runtime test")
    description: Optional[str] = Field(None, description="Description")
    plugin_directory: Optional[str] = Field(None, description="Plugin directory")
    plugin_type: Optional[str] = Field("tool", description="Plugin type")
    plugin_executed: Optional[str] = Field(None, description="Plugin executed")
    plugin_event: Optional[str] = Field(None, description="Plugin event")
    plugin_title: Optional[str] = Field(None, description="Plugin title")
    detail: Optional[str] = Field(None, description="Detail")
    confirm_needed: Optional[bool] = Field(True, description="Confirm needed")
    can_be_sold: Optional[bool] = Field(False, description="Can be sold")
    used_in_sns: Optional[bool] = Field(False, description="Used in SNS")
    creator: Optional[str] = Field(None, description="Creator")


class PluginCreate(PluginBase):
    """Plugin creation schema"""
    pass


class PluginUpdate(BaseModel):
    """Plugin update schema"""
    name: Optional[str] = None
    company: Optional[str] = None
    company_abbr: Optional[str] = None
    version: Optional[str] = None
    alias_name: Optional[str] = None
    filename: Optional[str] = None
    run_mode: Optional[str] = None
    run_scope: Optional[str] = None
    instruction: Optional[str] = None
    runtime_main: Optional[str] = None
    runtime_test: Optional[str] = None
    description: Optional[str] = None
    plugin_directory: Optional[str] = None
    plugin_type: Optional[str] = None
    plugin_executed: Optional[str] = None
    plugin_event: Optional[str] = None
    plugin_title: Optional[str] = None
    detail: Optional[str] = None
    confirm_needed: Optional[bool] = None
    can_be_sold: Optional[bool] = None
    used_in_sns: Optional[bool] = None
    creator: Optional[str] = None


class PluginResponse(PluginBase):
    """Plugin response schema"""
    id: int
    plugin_id: str
    create_time: datetime
    is_delete: bool

    class Config:
        from_attributes = True


# ==================== MCP Schemas ====================

class MCPBase(BaseModel):
    """MCP base schema"""
    name: str = Field(..., description="MCP name")
    instruction: Optional[str] = Field(None, description="Instruction")
    file_path: Optional[str] = Field(None, description="File path")
    requirement: Optional[str] = Field(None, description="Requirement")
    parameter: Optional[str] = Field(None, description="Parameter JSON")
    description: Optional[str] = Field(None, description="Description")
    detail: Optional[str] = Field(None, description="Detail")
    mcp_type: Optional[str] = Field("stdio", description="MCP type: stdio/sse")
    mcp_event: Optional[str] = Field(None, description="MCP event")
    confirm_needed: Optional[bool] = Field(True, description="Confirm needed")
    can_be_sold: Optional[bool] = Field(False, description="Can be sold")
    used_in_sns: Optional[bool] = Field(False, description="Used in SNS")
    creator: Optional[str] = Field(None, description="Creator")


class MCPCreate(MCPBase):
    """MCP creation schema"""
    pass


class MCPUpdate(BaseModel):
    """MCP update schema"""
    name: Optional[str] = None
    instruction: Optional[str] = None
    file_path: Optional[str] = None
    requirement: Optional[str] = None
    parameter: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None
    mcp_type: Optional[str] = None
    mcp_event: Optional[str] = None
    confirm_needed: Optional[bool] = None
    can_be_sold: Optional[bool] = None
    used_in_sns: Optional[bool] = None
    creator: Optional[str] = None


class MCPResponse(MCPBase):
    """MCP response schema"""
    id: int
    mcp_id: str
    create_time: datetime
    is_delete: bool

    class Config:
        from_attributes = True


# ==================== Function Schemas ====================

class FunctionBase(BaseModel):
    """Function base schema"""
    name: str = Field(..., description="Function name")
    instruction: Optional[str] = Field(None, description="Instruction")
    file_path: Optional[str] = Field(None, description="File path")
    requirement: Optional[str] = Field(None, description="Requirement")
    parameter: Optional[str] = Field(None, description="Parameter JSON")
    description: Optional[str] = Field(None, description="Description")
    detail: Optional[str] = Field(None, description="Detail")
    function_type: Optional[str] = Field("python", description="Function type")
    function_event: Optional[str] = Field(None, description="Function event")
    confirm_needed: Optional[bool] = Field(True, description="Confirm needed")
    can_be_sold: Optional[bool] = Field(False, description="Can be sold")
    used_in_sns: Optional[bool] = Field(False, description="Used in SNS")
    creator: Optional[str] = Field(None, description="Creator")


class FunctionCreate(FunctionBase):
    """Function creation schema"""
    pass


class FunctionUpdate(BaseModel):
    """Function update schema"""
    name: Optional[str] = None
    instruction: Optional[str] = None
    file_path: Optional[str] = None
    requirement: Optional[str] = None
    parameter: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None
    function_type: Optional[str] = None
    function_event: Optional[str] = None
    confirm_needed: Optional[bool] = None
    can_be_sold: Optional[bool] = None
    used_in_sns: Optional[bool] = None
    creator: Optional[str] = None


class FunctionResponse(FunctionBase):
    """Function response schema"""
    id: int
    function_id: str
    create_time: datetime
    is_delete: bool

    class Config:
        from_attributes = True


# ==================== Computer Use (Skill) Schemas ====================

class SkillBase(BaseModel):
    """Skill/Computer Use base schema"""
    name: str = Field(..., description="Skill name")
    instruction: Optional[str] = Field(None, description="Instruction")
    file_path: Optional[str] = Field(None, description="File path")
    requirement: Optional[str] = Field(None, description="Requirement")
    parameter: Optional[str] = Field(None, description="Parameter JSON")
    description: Optional[str] = Field(None, description="Description")
    detail: Optional[str] = Field(None, description="Detail")
    skill_type: Optional[str] = Field("computer_use", description="Skill type")
    skill_event: Optional[str] = Field(None, description="Skill event")
    confirm_needed: Optional[bool] = Field(True, description="Confirm needed")
    can_be_sold: Optional[bool] = Field(False, description="Can be sold")
    used_in_sns: Optional[bool] = Field(False, description="Used in SNS")
    creator: Optional[str] = Field(None, description="Creator")


class SkillCreate(SkillBase):
    """Skill creation schema"""
    pass


class SkillUpdate(BaseModel):
    """Skill update schema"""
    name: Optional[str] = None
    instruction: Optional[str] = None
    file_path: Optional[str] = None
    requirement: Optional[str] = None
    parameter: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None
    skill_type: Optional[str] = None
    skill_event: Optional[str] = None
    confirm_needed: Optional[bool] = None
    can_be_sold: Optional[bool] = None
    used_in_sns: Optional[bool] = None
    creator: Optional[str] = None


class SkillResponse(SkillBase):
    """Skill response schema"""
    id: int
    skill_id: str
    create_time: datetime
    is_delete: bool

    class Config:
        from_attributes = True
