"""Backend database package.

This package contains the refactored database layer extracted from DBFactory.py.

Structure:
- base.py: OLD database session management (deprecated, use backend.config.database instead)
- models/: ORM model definitions
  - agent.py: Agent-related models
  - chat.py: Chat and messaging models
  - km.py: Knowledge management models
  - map.py: Map-related models
  - system.py: System configuration and management models
- repositories/: Data access layer with CRUD operations
  - base.py: Base repository with common CRUD operations
  - agent_repository.py: Agent CRUD operations
  - chat_repository.py: Chat CRUD operations
  - km_repository.py: Knowledge management CRUD operations
  - map_repository.py: Map CRUD operations
  - system_repository.py: System CRUD operations

Usage:
    from backend.database import models, repositories
    from backend.config.database import get_db, get_db_session, init_db

    # Initialize database
    init_db()

    # Use repositories
    agent_repo = repositories.AgentCfgRepository()
    agents = agent_repo.get_all()
"""

# Don't import from .base - it creates a duplicate engine!
# Use backend.config.database instead
from . import models
from . import repositories

__all__ = [
    'models',
    'repositories'
]
