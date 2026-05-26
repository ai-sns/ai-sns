"""System configuration ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from db.base import Base
from runtime.shared import debug_info


class SystemCfg(Base):
    """System configuration model."""
    __tablename__ = 'system_cfg'

    id = Column(Integer, primary_key=True, autoincrement=True)
    autorun = Column(Boolean, default=False, doc="Auto-run on startup")
    showtaskbar = Column(Boolean, default=False, doc="Show in taskbar")
    updateinfo = Column(Boolean, default=False, doc="Update notification")
    minirunontray = Column(Boolean, default=False, doc="Minimize to tray")
    closebuttontype = Column(String(100), doc="Close button behavior")
    style = Column(String(500), doc="UI style")
    showinfo = Column(Boolean, default=True, doc="Show notifications")
    showinfoicon = Column(Boolean, default=True, doc="Show notification icon")
    infosound = Column(Boolean, default=True, doc="Notification sound")
    agent_server = Column(Text, doc="agent server url")
    ai_sns_server = Column(Text, doc="ai-sns server url")
    conversation_timeout_seconds = Column(Integer, default=60, doc="Conversation timeout seconds")
    contact_cooldown_seconds = Column(Integer, default=300, doc="Contact cooldown seconds")
    contact_recent_limit = Column(Integer, default=3, doc="Contact recent limit")
    process_info_compact_every_n = Column(Integer, default=50, doc="Process info compact every N")
    process_info_plan_summary_every_n = Column(Integer, default=5, doc="Process info plan summary every N")
    memory_enabled = Column(Boolean, default=True, doc="Memory enabled")
    memory_embedding_enabled = Column(Boolean, default=False, doc="Memory embedding enabled")
    log_retention_days = Column(Integer, default=3, doc="Log retention days")
    tool_check_every_n = Column(Integer, default=0, doc="Tool check every N")
    tool_check_before_review_enabled = Column(Boolean, default=False, doc="Tool check before review enabled")
    agent_card_before_review_enabled = Column(Boolean, default=False, doc="Agent card before review enabled")
    language = Column(String(10), default='en', doc="Language")
    a2a_server_enabled = Column(Boolean, default=False, doc="A2A server enabled")
    debug_mode = Column(Text, default='', doc="Debug mode filter: empty=off, '*'=all, or comma-separated tag list")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class SystemInit(Base):
    """System initialization model."""
    __tablename__ = 'system_init'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), doc="Name")
    avatar = Column(Text, doc="Avatar")
    password = Column(String(128), doc="Password")
    confirm_password = Column(String(128), doc="Confirm password")
    profile = Column(String(500), doc="Profile")
    llm = Column(String(100), doc="LLM")
    llm_server = Column(String(500), doc="LLM server URL")
    api_key = Column(String(200), doc="API key")
    avatar3d = Column(Text, doc="3D avatar")
    account = Column(String(128), doc="Account")
    account_password = Column(String(128), doc="Account password")
    sns_url = Column(Text, doc="SNS URL")
    map = Column(String, doc="Map")
    map_api_key = Column(String(128), doc="Map API key")
    map_id = Column(String(128), doc="Map ID")
    status = Column(Integer, doc="Status")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
