"""System repository with specialized CRUD operations."""
from .base import BaseRepository
from db.models.system import SystemCfg, SystemInit
from runtime.shared import debug_info


class SystemCfgRepository(BaseRepository[SystemCfg]):
    """System configuration repository."""

    def __init__(self):
        super().__init__(SystemCfg)


class SystemInitRepository(BaseRepository[SystemInit]):
    """System initialization repository."""

    def __init__(self):
        super().__init__(SystemInit)
