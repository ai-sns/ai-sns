"""
Database Configuration

Manages SQLAlchemy database connection and session.
Extracted from db/database.py for better organization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import logging

from .settings import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# SQLAlchemy Base
Base = declarative_base()

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.database.full_path}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.debug  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database
    Creates all tables if they don't exist
    """
    try:
        # Import all new backend models to register them with Base
        from backend.database.models import agent, chat, km, map, system

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db_session() -> Session:
    """
    Get a new database session (for non-FastAPI use)

    Usage:
        db = get_db_session()
        try:
            # Use db
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()


def close_db():
    """Close database connection"""
    engine.dispose()
    logger.info("Database connection closed")
