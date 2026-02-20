"""Database session management and base configuration."""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for ORM models
Base = declarative_base()

# Database path configuration
DBPath = os.path.join(Path(__file__).resolve().parent.parent.parent, "db", "db.sqlite")
print("DBPath", DBPath)
SQL_DATABASE_URL = fr"sqlite:///{DBPath}"

# Create engine with connection pool settings
# Note: For SQLite, it is not recommended to set a very large connection pool
# For higher concurrency, consider migrating to PostgreSQL/MySQL
engine = create_engine(
    SQL_DATABASE_URL,
    pool_size=10,           # Persistent connections (recommended 10-20)
    max_overflow=20,        # Overflow connections (recommended 20-30)
    pool_timeout=60,        # Connection wait timeout (seconds)
    pool_recycle=3600,      # Connection recycle time (1 hour)
    pool_pre_ping=True,     # Check connection health
    echo=False,             # Disable SQL logs in production
    connect_args={
        "check_same_thread": False,  # Allow SQLite across threads
        "timeout": 30                # SQLite lock timeout (seconds)
    }
)

# For higher concurrency, you can adjust to:
# pool_size=20, max_overflow=30  -> 50 total connections
# pool_size=30, max_overflow=50  -> 80 total connections
# Note: SQLite writes are still single-threaded; increasing the pool will not improve write performance

# Session factory
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Get a new database session."""
    return SessionLocal()


def create_all_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
