"""Knowledge management ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from backend.config.database import Base


class KMCfg(Base):
    """Knowledge base configuration model."""
    __tablename__ = 'km_cfg'

    id = Column(Integer, primary_key=True, autoincrement=True)
    km_id = Column(String(100), doc="Knowledge base ID")
    name = Column(String(200), doc="Name")
    memo = Column(String(200), doc="Memo")
    label = Column(String(100), doc="Label")
    kmpath = Column(String(250), doc="Knowledge base path")
    vectorization = Column(Boolean, default=True, doc="Enable vectorization")
    stopvectorization = Column(Boolean, default=False, doc="Stop vectorization")
    kmtype = Column(String(100), doc="Knowledge base type")
    vectortype = Column(String(150), doc="Vector type")
    embeddingmodel = Column(String(150), doc="Embedding model")
    textblocklength = Column(Integer, doc="Text block length")
    overlaplength = Column(Integer, doc="Overlap length")
    titleaugment = Column(Boolean, default=True, doc="Title augmentation")
    position = Column(Integer, default=9999, doc="Display position")
    is_show = Column(Boolean, default=True, doc="Is visible")
    config_param = Column(Text, doc="Configuration parameters")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class KMData(Base):
    """Knowledge base data model."""
    __tablename__ = 'km_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    km_id = Column(String(100), doc="Knowledge base ID")
    filename = Column(String(200), doc="File name")
    filenum = Column(Integer, default=1, doc="File number")
    textblocklength = Column(Integer, default=1, doc="Text block length")
    overlaplength = Column(Integer, default=1, doc="Overlap length")
    waitvectorization = Column(Boolean, default=False, doc="Wait for vectorization")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")


class NoteMng(Base):
    """Note management model."""
    __tablename__ = 'note_mng'

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(String(100), doc="Note ID")
    title = Column(String(100), doc="Title")
    file_name = Column(String(200), doc="File name")
    content = Column(Text, doc="Content")
    km_id = Column(String(100), doc="Knowledge base ID")
    tag_1 = Column(String(100), doc="Tag 1")
    tag_2 = Column(String(100), doc="Tag 2")
    tag_3 = Column(String(100), doc="Tag 3")
    tags = Column(Text, doc="Tags as JSON string")  # New: stores all tags as a JSON string
    is_pinned = Column(Boolean, default=False, doc="Is pinned")  # New: whether pinned
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, doc="Update time")  # New: update time
    waitvectorization = Column(Boolean, default=False, doc="Wait for vectorization")
    creator = Column(String(100), doc="Creator")
    is_delete = Column(Boolean, default=False, doc="Soft delete")
    create_time = Column(DateTime, default=datetime.now, doc="Create time")
    stick_time = Column(DateTime, nullable=True, doc="Stick time")
    label = Column(String(50), doc="Category label")

