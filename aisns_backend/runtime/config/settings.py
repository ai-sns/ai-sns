"""
Application Configuration

Loads configuration from environment variables and defaults.
Priority: Environment Variables > Defaults
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """AI service configuration"""
    api_base: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 1.0
    max_tokens: int = 4096
    stream: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration"""
    sql_url: str = field(default_factory=lambda: os.path.join(
        Path(__file__).parent.parent.parent,
        "db"
    ))
    database_name: str = "db.sqlite"

    @property
    def full_path(self) -> str:
        """Get full database path"""
        return os.path.join(self.sql_url, self.database_name)


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 8788
    reload: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "your-secret-key-change-in-production"
    api_key_expire_days: int = 365


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    default_limit: int = 100
    window_seconds: int = 60


@dataclass
class StorageConfig:
    """File storage configuration"""
    upload_dir: str = field(default_factory=lambda: os.path.join(
        Path(__file__).parent.parent.parent,
        "uploads"
    ))
    max_upload_size: int = 50 * 1024 * 1024  # 50MB

    km_base_dir: str = field(default_factory=lambda: os.path.join(
        Path(__file__).parent.parent.parent,
        "km"
    ))


@dataclass
class ToolsConfig:
    """Tools module configuration"""
    page_size: int = 50  # Number of tools to load per page


class Settings:
    """
    Application Settings Manager

    Loads and manages configuration from multiple sources:
    1. Environment variables (highest priority)
    2. Default values (lowest priority)
    """

    def __init__(self):
        self.app_name = "AI-SNS API Server"
        self.app_version = "1.0.0"
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
        self.environment = os.environ.get("ENVIRONMENT", "development")

        # Initialize configs
        self.ai = self._load_ai_config()
        self.database = self._load_database_config()
        self.server = self._load_server_config()
        self.security = self._load_security_config()
        self.rate_limit = self._load_rate_limit_config()
        self.storage = self._load_storage_config()
        self.tools = self._load_tools_config()

        # Ensure directories exist
        self._ensure_directories()

    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration with priority: env > defaults"""
        config = AIConfig()

        # Override with environment variables if set
        if os.environ.get('OPENAI_API_KEY'):
            config.api_key = os.environ['OPENAI_API_KEY']
            config.api_base = os.environ.get('OPENAI_API_BASE', config.api_base)
            config.model = os.environ.get('OPENAI_MODEL', config.model)
            config.embedding_model = os.environ.get('OPENAI_EMBEDDING_MODEL', config.embedding_model)
            config.temperature = float(os.environ.get('OPENAI_TEMPERATURE', str(config.temperature)))
            config.max_tokens = int(os.environ.get('OPENAI_MAX_TOKENS', str(config.max_tokens)))
            logger.info("Loaded AI config from environment variables")

        return config

    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        config = DatabaseConfig()

        # Override with environment variables
        if os.environ.get('DATABASE_URL'):
            config.sql_url = os.environ['DATABASE_URL']
        if os.environ.get('DATABASE_NAME'):
            config.database_name = os.environ['DATABASE_NAME']

        return config

    def _load_server_config(self) -> ServerConfig:
        """Load server configuration"""
        config = ServerConfig()

        config.host = os.environ.get('HOST', config.host)
        config.port = int(os.environ.get('PORT', str(config.port)))
        config.reload = os.environ.get('RELOAD', 'false').lower() == 'true'

        cors_origins = os.environ.get('CORS_ORIGINS', '')
        if cors_origins:
            config.cors_origins = [origin.strip() for origin in cors_origins.split(',')]

        return config

    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        config = SecurityConfig()

        config.secret_key = os.environ.get('SECRET_KEY', config.secret_key)
        config.api_key_expire_days = int(os.environ.get('API_KEY_EXPIRE_DAYS', str(config.api_key_expire_days)))

        return config

    def _load_rate_limit_config(self) -> RateLimitConfig:
        """Load rate limiting configuration"""
        config = RateLimitConfig()

        config.default_limit = int(os.environ.get('RATE_LIMIT', str(config.default_limit)))
        config.window_seconds = int(os.environ.get('RATE_LIMIT_WINDOW', str(config.window_seconds)))

        return config

    def _load_storage_config(self) -> StorageConfig:
        """Load storage configuration"""
        config = StorageConfig()

        if os.environ.get('UPLOAD_DIR'):
            config.upload_dir = os.environ['UPLOAD_DIR']
        if os.environ.get('MAX_UPLOAD_SIZE'):
            config.max_upload_size = int(os.environ['MAX_UPLOAD_SIZE'])
        if os.environ.get('KM_BASE_DIR'):
            config.km_base_dir = os.environ['KM_BASE_DIR']

        return config

    def _load_tools_config(self) -> ToolsConfig:
        """Load tools configuration"""
        config = ToolsConfig()

        # Override with environment variable if set
        if os.environ.get('TOOLS_PAGE_SIZE'):
            config.page_size = int(os.environ['TOOLS_PAGE_SIZE'])

        return config

    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.database.sql_url, exist_ok=True)
        os.makedirs(self.storage.upload_dir, exist_ok=True)
        os.makedirs(self.storage.km_base_dir, exist_ok=True)

    def has_valid_api_key(self) -> bool:
        """Check if a valid API key is configured"""
        return bool(self.ai.api_key and self.ai.api_key.strip())


# Singleton instance
_settings = None


def get_settings() -> Settings:
    """Get the singleton settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
