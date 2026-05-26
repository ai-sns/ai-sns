"""Web management repository with specialized CRUD operations."""
from typing import List, Optional
from sqlalchemy import asc
from .base import BaseRepository
from db.models.web import WebMng
from db.database import get_db_session as get_session
from db.write_queue import db_write
from runtime.shared import debug_info


class WebMngRepository(BaseRepository[WebMng]):
    """Web management repository."""

    def __init__(self):
        super().__init__(WebMng)

    def create_with_id(self, **kwargs) -> int:
        """Create web entry and return its ID."""
        _model = self.model
        def _do(session):
            web = _model(**kwargs)
            session.add(web)
            session.flush()
            return web.id
        return db_write(_do, description="repo_create_web_mng")

    def get_all_ordered(self, **kwargs) -> List[WebMng]:
        """Get all web entries ordered by position."""
        session = get_session()
        try:
            return session.query(self.model).filter_by(**kwargs).order_by(asc(WebMng.position)).all()
        finally:
            session.close()

    def update_by_web_id(self, web_id: str, **kwargs):
        """Update web entry by web_id."""
        self.update_by_filter({'web_id': web_id}, **kwargs)
