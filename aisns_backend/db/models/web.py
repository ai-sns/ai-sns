"""Web management ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from db.base import Base
from runtime.shared import debug_info


class WebMng(Base):
    """Web management model."""
    __tablename__ = 'web_mng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    web_id = Column(String(100), doc="Web ID")
    name = Column(String(100), doc="Name")
    title = Column(String(100), doc="Title")
    type = Column(String(100), doc="Type")
    description = Column(Text, doc="Description")
    filename = Column(String(200), doc="Filename")
    url = Column(String(500), doc="URL")
    position = Column(Integer, default=999, doc="Position")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
