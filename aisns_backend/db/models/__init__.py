"""Database models package."""
from .agent import (
    AgentCfg, AgentDocSkill, AgentMemory, AgentTools,
    Prompt, LLMConfig, RoleConfig
)
from .aisns import (
    AIChatMessages, AIFriend, AISnsCfg,
    MapTrade, MapVisit, MapActivity, MapPresetMsg
)
from .km import KeyValue, KMCfg, KMData, NoteMng
from .tools import PluginMng, FunctionMng, McpMng, SkillMng
from .web import WebMng
from .system import SystemCfg, SystemInit
from runtime.shared import debug_info

__all__ = [
    # Agent models
    'AgentCfg', 'AgentDocSkill', 'AgentMemory', 'AgentTools',
    'Prompt', 'LLMConfig', 'RoleConfig',

    # AI SNS & Map models
    'AIChatMessages', 'AIFriend', 'AISnsCfg',
    'MapTrade', 'MapVisit', 'MapActivity', 'MapPresetMsg',

    # KM models
    'KeyValue', 'KMCfg', 'KMData', 'NoteMng',

    # Tool models
    'PluginMng', 'FunctionMng', 'McpMng', 'SkillMng',

    # Web models
    'WebMng',

    # System models
    'SystemCfg', 'SystemInit',
]
