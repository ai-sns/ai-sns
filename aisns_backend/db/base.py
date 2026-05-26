"""Shared SQLAlchemy declarative Base for all ORM models.

Every model file should import Base from here:
    from db.base import Base
"""
from sqlalchemy.orm import declarative_base
from runtime.shared import debug_info

Base = declarative_base()
