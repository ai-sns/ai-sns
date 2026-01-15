#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add test tools data to database
为四个工具模块添加测试数据
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config.database import get_db_session
from backend.database.models.system import PluginMng, McpMng, FunctionMng, SkillMng
from datetime import datetime


def add_test_plugins(db):
    """添加Plugin测试数据"""
    print("Adding test plugins...")

    plugins = [
        {
            "plugin_id": "PL2026011500000001",
            "name": "Weather Query Plugin",
            "description": "Query weather information for any city using OpenWeatherMap API",
            "instruction": "Use this plugin to get current weather data. Provide city name as parameter.",
            "plugin_type": "Tool_API",
            "filename": "weather_query.py",  # 使用filename而不是file_path
            "runtime_main": "def get_weather(city): return {'temp': 25, 'condition': 'sunny'}",
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        },
        {
            "plugin_id": "PL2026011500000002",
            "name": "Text Analyzer",
            "description": "Analyze text sentiment, keywords and summary",
            "instruction": "Send text content to analyze its sentiment and extract key information.",
            "plugin_type": "Tool_AI",
            "filename": "text_analyzer.py",  # 使用filename而不是file_path
            "confirm_needed": False,
            "is_delete": False,
            "create_time": datetime.now()
        }
    ]

    for plugin_data in plugins:
        existing = db.query(PluginMng).filter(PluginMng.plugin_id == plugin_data["plugin_id"]).first()
        if not existing:
            plugin = PluginMng(**plugin_data)
            db.add(plugin)
            print(f"  ✓ Added plugin: {plugin_data['name']}")
        else:
            print(f"  - Plugin already exists: {plugin_data['name']}")

    db.commit()


def add_test_mcps(db):
    """添加MCP测试数据"""
    print("\nAdding test MCPs...")

    mcps = [
        {
            "mcp_id": "MC2026011500000001",
            "name": "File System MCP",
            "description": "Model Context Protocol server for file system operations",
            "instruction": "Use this MCP to read, write and manage files on the local filesystem.",
            "mcp_type": "stdio",
            "file_path": "/mcp_servers/filesystem_server.py",
            "parameter": '{"root_dir": "/data"}',
            "requirement": "mcp==1.0.0\nfsspec==2023.1.0",
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        },
        {
            "mcp_id": "MC2026011500000002",
            "name": "Database MCP",
            "description": "MCP server for database query operations",
            "instruction": "Query and manage database records through this MCP interface.",
            "mcp_type": "sse",
            "file_path": "/mcp_servers/database_server.py",
            "parameter": '{"db_url": "sqlite:///data.db"}',
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        }
    ]

    for mcp_data in mcps:
        existing = db.query(McpMng).filter(McpMng.mcp_id == mcp_data["mcp_id"]).first()
        if not existing:
            mcp = McpMng(**mcp_data)
            db.add(mcp)
            print(f"  ✓ Added MCP: {mcp_data['name']}")
        else:
            print(f"  - MCP already exists: {mcp_data['name']}")

    db.commit()


def add_test_functions(db):
    """添加Function测试数据"""
    print("\nAdding test functions...")

    functions = [
        {
            "function_id": "FN2026011500000001",
            "name": "calculate_sum",
            "description": "Calculate sum of two numbers",
            "instruction": "Pass two numbers as parameters to get their sum.",
            "function_type": "python",
            "file_path": "/functions/calculate_sum.py",
            "parameter": '{"a": {"type": "number", "description": "First number"}, "b": {"type": "number", "description": "Second number"}}',
            "confirm_needed": False,
            "is_delete": False,
            "create_time": datetime.now()
        },
        {
            "function_id": "FN2026011500000002",
            "name": "string_reverse",
            "description": "Reverse a string",
            "instruction": "Provide a string to get its reversed version.",
            "function_type": "javascript",
            "file_path": "/functions/string_reverse.js",
            "parameter": '{"text": {"type": "string", "description": "Text to reverse"}}',
            "confirm_needed": False,
            "is_delete": False,
            "create_time": datetime.now()
        }
    ]

    for function_data in functions:
        existing = db.query(FunctionMng).filter(FunctionMng.function_id == function_data["function_id"]).first()
        if not existing:
            function = FunctionMng(**function_data)
            db.add(function)
            print(f"  ✓ Added function: {function_data['name']}")
        else:
            print(f"  - Function already exists: {function_data['name']}")

    db.commit()


def add_test_skills(db):
    """添加Computer Use Skill测试数据"""
    print("\nAdding test computer use skills...")

    skills = [
        {
            "skill_id": "SK2026011500000001",
            "name": "Screenshot Capture",
            "description": "Capture screenshot of the entire screen or specific window",
            "instruction": "Use this skill to take screenshots. Specify window name or leave empty for full screen.",
            "skill_type": "screenshot",
            "file_path": None,  # Built-in skill
            "parameter": '{"region": "full", "format": "png"}',
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        },
        {
            "skill_id": "SK2026011500000002",
            "name": "Mouse Click",
            "description": "Perform mouse click at specified coordinates",
            "instruction": "Provide x, y coordinates to perform a mouse click action.",
            "skill_type": "mouse_click",
            "parameter": '{"x": 0, "y": 0, "button": "left"}',
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        },
        {
            "skill_id": "SK2026011500000003",
            "name": "Keyboard Input",
            "description": "Type text using keyboard simulation",
            "instruction": "Send text string to type it on the active window.",
            "skill_type": "keyboard_input",
            "parameter": '{"text": "", "interval_ms": 50}',
            "confirm_needed": True,
            "is_delete": False,
            "create_time": datetime.now()
        }
    ]

    for skill_data in skills:
        existing = db.query(SkillMng).filter(SkillMng.skill_id == skill_data["skill_id"]).first()
        if not existing:
            skill = SkillMng(**skill_data)
            db.add(skill)
            print(f"  ✓ Added skill: {skill_data['name']}")
        else:
            print(f"  - Skill already exists: {skill_data['name']}")

    db.commit()


def main():
    """Main function"""
    print("=" * 60)
    print("Adding Test Tools Data to Database")
    print("=" * 60)

    db = get_db_session()

    try:
        add_test_plugins(db)
        add_test_mcps(db)
        add_test_functions(db)
        add_test_skills(db)

        print("\n" + "=" * 60)
        print("✓ All test data added successfully!")
        print("=" * 60)
        print("\nYou can now test the execute buttons in the frontend.")

    except Exception as e:
        print(f"\n✗ Error adding test data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
