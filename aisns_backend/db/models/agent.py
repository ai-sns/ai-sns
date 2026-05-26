"""Agent-related ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from db.base import Base
from runtime.shared import debug_info


class AgentCfg(Base):
    """Agent configuration model."""
    __tablename__ = 'agent_cfg'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), doc="User ID")
    name = Column(String(200), doc="Agent name")
    memo = Column(String(200), doc="Memo")
    borndate = Column(DateTime, default=datetime.now, doc="Birth date")
    borncontry = Column(String(100), doc="Birth country")
    language = Column(String(100), doc="Language")
    gender = Column(Integer, doc="Gender")
    joinfederation = Column(Boolean, default=False, doc="Join federation")
    syncfederation = Column(Boolean, default=False, doc="Sync federation")
    federationid = Column(String(150), doc="Federation ID")
    defaultmodel = Column(String(200), doc="Default model")
    defaultrole = Column(String(200), doc="Default role")
    lastmodel = Column(String(200), doc="Last model")
    lastrole = Column(String(200), doc="Last role")
    specialization = Column(Text, doc="Specialization")
    plugins = Column(Text, doc="Plugins")
    kms = Column(Text, doc="Knowledge bases")
    last_plugins = Column(Text, doc="Last plugins")
    last_kms = Column(Text, doc="Last knowledge bases")
    prompt = Column(Text, doc="System prompt")
    snsaccount = Column(String(100), doc="SNS account")
    snsnickname = Column(String(100), doc="SNS nickname")
    islimittotalmessage = Column(Boolean, default=True, doc="Limit total messages")
    islimitmessagepp = Column(Boolean, default=True, doc="Limit messages per person")
    totalmessages = Column(Integer, doc="Total messages")
    ppmessages = Column(Integer, doc="Messages per person")
    readfile = Column(Boolean, default=True, doc="Can read files")
    writefile = Column(Boolean, default=True, doc="Can write files")
    deletefile = Column(Boolean, default=True, doc="Can delete files")
    execfile = Column(Boolean, default=True, doc="Can execute files")
    uselastmodel = Column(Boolean, default=False, doc="Use last model")
    uselastrole = Column(Boolean, default=False, doc="Use last role")
    uselastplugins = Column(Boolean, default=False, doc="Use last plugins")
    uselastkms = Column(Boolean, default=False, doc="Use last KMs")
    callpluginbyinstruct = Column(Boolean, default=True, doc="Call plugin by instruction")
    modelfrequent = Column(Boolean, default=False, doc="Model frequent")
    rolefrequent = Column(Boolean, default=False, doc="Role frequent")
    multimodelfrequent = Column(Boolean, default=False, doc="Multi-model frequent")
    multimodellastmodel = Column(String(500), doc="Multi-model last model")
    multimodellastrole = Column(String(100), doc="Multi-model last role")
    autorunrounds = Column(Integer, doc="Auto run rounds")
    position = Column(Integer, default=9999, doc="Display position")
    is_show = Column(Boolean, default=True, doc="Is visible")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
    agent_card = Column(Text, doc="Agent card JSON")
    capabilities = Column(Text, doc="Agent capabilities JSON")
    skills = Column(Text, doc="Agent skills JSON")
    a2a_endpoint = Column(String(500), doc="A2A endpoint URL")
    memory_enabled = Column(Boolean, default=True, doc="Memory enabled")
    multimodal_enabled = Column(Boolean, default=True, doc="Multimodal enabled")
    avatar_url = Column(String(500), doc="Avatar URL")


class AgentDocSkill(Base):
    __tablename__ = 'agent_doc_skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, nullable=False)
    skill_key = Column(String(200), nullable=False)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)


class AgentMemory(Base):
    """Agent memory storage model."""
    __tablename__ = 'agent_memory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(200), nullable=False, doc="Agent ID")
    memory_type = Column(String(50), nullable=False, doc="Memory type")
    key = Column(String(200), doc="Memory key")
    content = Column(Text, nullable=False, doc="Memory content")
    # 'metadata' is reserved by SQLAlchemy declarative; map via Column("metadata")
    meta_data = Column("metadata", Text, doc="Metadata JSON")
    importance = Column(Float, default=0.5, doc="Importance score")
    access_count = Column(Integer, default=0, doc="Access count")
    last_accessed = Column(DateTime, doc="Last accessed time")
    created_at = Column(DateTime, default=datetime.utcnow, doc="Created at")
    expires_at = Column(DateTime, nullable=True, doc="Expiration time")
    is_delete = Column(Boolean, default=False, doc="Soft delete")


class AgentTools(Base):
    """Agent-tool association model."""
    __tablename__ = 'agent_tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, nullable=False, doc="Agent ID")
    tool_type = Column(Text, nullable=False, doc="Tool type: plugin|mcp|function|skill")
    tool_id = Column(Text, nullable=False, doc="Tool ID")
    enabled = Column(Integer, default=1, doc="Whether enabled")
    priority = Column(Integer, default=0, doc="Priority")
    create_time = Column(DateTime, default=datetime.utcnow, doc="Create time")


class Prompt(Base):
    """Prompt model."""
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, doc="Title")
    caption = Column(String, doc="Caption")
    content = Column(String, doc="Content")
    question = Column(String, doc="Question")
    tags = Column(String, doc="Tags")
    model_name = Column(String(100), doc="Model name")
    position = Column(Integer, doc="Position")


class LLMConfig(Base):
    """LLM model configuration."""
    __tablename__ = 'llm_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(50), unique=True, nullable=False, doc="Configuration unique ID")
    name = Column(String(100), nullable=False, doc="Display name")
    provider = Column(String(50), nullable=False, doc="Provider type: openai|claude|gemini|custom")
    plugin_id = Column(String(100), doc="Associated plugin ID")

    # Basic connection configuration
    api_endpoint = Column(String(500), doc="API endpoint URL")
    api_key = Column(Text, doc="API key (encrypted)")
    model_name = Column(String(100), doc="Model name")

    # Advanced parameters
    temperature = Column(Float, default=0.7, doc="Temperature (0-2)")
    max_tokens = Column(Integer, default=2048, doc="Max tokens")
    top_p = Column(Float, default=1.0, doc="Top P")
    frequency_penalty = Column(Float, default=0.0, doc="Frequency penalty")
    presence_penalty = Column(Float, default=0.0, doc="Presence penalty")
    stream = Column(Boolean, default=True, doc="Enable streaming")

    # Custom parameters (JSON format)
    custom_params = Column(Text, doc="Custom parameters in JSON")

    # Metadata
    description = Column(Text, doc="Description")
    is_active = Column(Boolean, default=True, doc="Is active")
    is_default = Column(Boolean, default=False, doc="Is default model")
    position = Column(Integer, default=9999, doc="Display position")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
    update_time = Column(DateTime, onupdate=datetime.now, doc="Update time")


class RoleConfig(Base):
    """Role/Persona configuration."""
    __tablename__ = 'role_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String(50), unique=True, nullable=False, doc="Role unique ID")
    name = Column(String(100), nullable=False, doc="Role name")
    display_name = Column(String(100), doc="Display name")

    # Prompt configuration
    system_prompt = Column(Text, nullable=False, doc="System prompt")
    greeting_message = Column(Text, doc="Greeting message")

    # Role attributes
    role_type = Column(String(50), doc="Role type: preset|custom")
    category = Column(String(50), doc="Category: developer|writer|analyst|assistant|other")
    avatar = Column(String(200), doc="Avatar URL or icon")

    # Metadata
    description = Column(Text, doc="Description")
    tags = Column(String(200), doc="Tags (comma separated)")
    is_active = Column(Boolean, default=True, doc="Is active")
    is_default = Column(Boolean, default=False, doc="Is default role")
    is_preset = Column(Boolean, default=False, doc="Is preset template")
    position = Column(Integer, default=9999, doc="Display position")
    usage_count = Column(Integer, default=0, doc="Usage count")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
    update_time = Column(DateTime, onupdate=datetime.now, doc="Update time")
