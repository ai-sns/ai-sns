"""Database repositories package."""
from .base import BaseRepository
from .agent_repository import (
    AgentCfgRepository,
    AgentToolsRepository,
    PromptRepository,
    LLMConfigRepository,
    RoleConfigRepository,
)
from .aisns_repository import (
    AIChatMessagesRepository,
    AIFriendRepository,
    AISnsCfgRepository,
    MapTradeRepository,
    MapVisitRepository,
    MapActivityRepository,
    MapPresetMsgRepository,
)
from .km_repository import (
    KeyValueRepository,
    KMCfgRepository,
    KMDataRepository,
    NoteMngRepository,
)
from .tools_repository import (
    PluginMngRepository,
    FunctionMngRepository,
    McpMngRepository,
    SkillMngRepository,
)
from .web_repository import WebMngRepository
from .system_repository import SystemCfgRepository, SystemInitRepository
from runtime.shared import debug_info

# Backward compatibility aliases
AISnsCfgRepository = AISnsCfgRepository

__all__ = [
    # Base
    'BaseRepository',
    # Agent repositories
    'AgentCfgRepository',
    'AgentToolsRepository',
    'PromptRepository',
    'LLMConfigRepository',
    'RoleConfigRepository',
    # AI SNS & Map repositories
    'AIChatMessagesRepository',
    'AIFriendRepository',
    'AISnsCfgRepository',
    'MapTradeRepository',
    'MapVisitRepository',
    'MapActivityRepository',
    'MapPresetMsgRepository',
    # KM repositories
    'KeyValueRepository',
    'KMCfgRepository',
    'KMDataRepository',
    'NoteMngRepository',
    # Tool repositories
    'PluginMngRepository',
    'FunctionMngRepository',
    'McpMngRepository',
    'SkillMngRepository',
    # Web repositories
    'WebMngRepository',
    # System repositories
    'SystemCfgRepository',
    'SystemInitRepository',
    # Backward compatibility
    'AISnsCfgRepository',
]
