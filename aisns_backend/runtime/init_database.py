# -*- coding: utf-8 -*-
"""
Initialize tools tables in the correct database (data/db.sqlite)
"""
import sys
import os
from runtime.shared import debug_info
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from db.database import engine
from db.base import Base

def init_database():
    """Create all tables"""
    print("Initializing database and creating all tables...")
    print(f"Database path: {engine.url}")

    try:
        # Import all models to register them
        from db.models import agent, aisns, km, tools, web, system

        # Create all tables
        Base.metadata.create_all(bind=engine)

        print("✓ Successfully created all tables")

    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    init_database()
