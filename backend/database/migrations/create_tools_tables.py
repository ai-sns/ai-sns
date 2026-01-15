# -*- coding: utf-8 -*-
"""
Create tools module tables in database
"""
import sys
import os
# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from backend.config.database import SessionLocal, engine
from backend.database.models.system import (
    PluginMng, McpMng, FunctionMng, SkillMng
)
from backend.database.base import Base

def create_tools_tables():
    """Create all tools-related tables"""
    print("Creating tools module tables...")

    try:
        # Create tables
        Base.metadata.create_all(bind=engine, tables=[
            PluginMng.__table__,
            McpMng.__table__,
            FunctionMng.__table__,
            SkillMng.__table__
        ])

        print("✓ Successfully created tables:")
        print("  - pluginmng")
        print("  - mcp_mng")
        print("  - function_mng")
        print("  - skill_mng")

    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tools_tables()
