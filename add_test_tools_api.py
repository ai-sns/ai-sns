#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add test tools data via API
通过API为四个工具模块添加测试数据
"""

import requests
import json
from datetime import datetime


API_BASE_URL = "http://127.0.0.1:8788/api/tools"


def add_test_plugins():
    """添加Plugin测试数据"""
    print("Adding test plugins via API...")

    plugins = [
        {
            "name": "Weather Query Plugin",
            "description": "Query weather information for any city using OpenWeatherMap API",
            "instruction": "Use this plugin to get current weather data. Provide city name as parameter.",
            "plugin_type": "Tool_API",
            "runtime_main": "def get_weather(city): return {'temp': 25, 'condition': 'sunny'}",
            "confirm_needed": True
        },
        {
            "name": "Text Analyzer",
            "description": "Analyze text sentiment, keywords and summary",
            "instruction": "Send text content to analyze its sentiment and extract key information.",
            "plugin_type": "Tool_AI",
            "confirm_needed": False
        }
    ]

    for plugin in plugins:
        try:
            response = requests.post(f"{API_BASE_URL}/plugins", json=plugin, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Added plugin: {plugin['name']} (ID: {result.get('plugin_id', 'N/A')})")
            else:
                print(f"  ✗ Failed to add plugin: {plugin['name']} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding plugin: {plugin['name']} - {e}")


def add_test_mcps():
    """添加MCP测试数据"""
    print("\nAdding test MCPs via API...")

    mcps = [
        {
            "name": "File System MCP",
            "description": "Model Context Protocol server for file system operations",
            "instruction": "Use this MCP to read, write and manage files on the local filesystem.",
            "mcp_type": "stdio",
            "file_path": "/mcp_servers/filesystem_server.py",
            "parameter": '{"root_dir": "/data"}',
            "requirement": "mcp==1.0.0\nfsspec==2023.1.0",
            "confirm_needed": True
        },
        {
            "name": "Database MCP",
            "description": "MCP server for database query operations",
            "instruction": "Query and manage database records through this MCP interface.",
            "mcp_type": "sse",
            "file_path": "/mcp_servers/database_server.py",
            "parameter": '{"db_url": "sqlite:///data.db"}',
            "confirm_needed": True
        }
    ]

    for mcp in mcps:
        try:
            response = requests.post(f"{API_BASE_URL}/mcp", json=mcp, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Added MCP: {mcp['name']} (ID: {result.get('mcp_id', 'N/A')})")
            else:
                print(f"  ✗ Failed to add MCP: {mcp['name']} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding MCP: {mcp['name']} - {e}")


def add_test_functions():
    """添加Function测试数据"""
    print("\nAdding test functions via API...")

    functions = [
        {
            "name": "calculate_sum",
            "description": "Calculate sum of two numbers",
            "instruction": "Pass two numbers as parameters to get their sum.",
            "function_type": "python",
            "file_path": "/functions/calculate_sum.py",
            "parameter": '{"a": {"type": "number", "description": "First number"}, "b": {"type": "number", "description": "Second number"}}',
            "confirm_needed": False
        },
        {
            "name": "string_reverse",
            "description": "Reverse a string",
            "instruction": "Provide a string to get its reversed version.",
            "function_type": "javascript",
            "file_path": "/functions/string_reverse.js",
            "parameter": '{"text": {"type": "string", "description": "Text to reverse"}}',
            "confirm_needed": False
        }
    ]

    for function in functions:
        try:
            response = requests.post(f"{API_BASE_URL}/functions", json=function, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Added function: {function['name']} (ID: {result.get('function_id', 'N/A')})")
            else:
                print(f"  ✗ Failed to add function: {function['name']} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding function: {function['name']} - {e}")


def add_test_skills():
    """添加Computer Use Skill测试数据"""
    print("\nAdding test computer use skills via API...")

    skills = [
        {
            "name": "Screenshot Capture",
            "description": "Capture screenshot of the entire screen or specific window",
            "instruction": "Use this skill to take screenshots. Specify window name or leave empty for full screen.",
            "skill_type": "screenshot",
            "parameter": '{"region": "full", "format": "png"}',
            "confirm_needed": True
        },
        {
            "name": "Mouse Click",
            "description": "Perform mouse click at specified coordinates",
            "instruction": "Provide x, y coordinates to perform a mouse click action.",
            "skill_type": "mouse_click",
            "parameter": '{"x": 0, "y": 0, "button": "left"}',
            "confirm_needed": True
        },
        {
            "name": "Keyboard Input",
            "description": "Type text using keyboard simulation",
            "instruction": "Send text string to type it on the active window.",
            "skill_type": "keyboard_input",
            "parameter": '{"text": "", "interval_ms": 50}',
            "confirm_needed": True
        }
    ]

    for skill in skills:
        try:
            response = requests.post(f"{API_BASE_URL}/skills", json=skill, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Added skill: {skill['name']} (ID: {result.get('skill_id', 'N/A')})")
            else:
                print(f"  ✗ Failed to add skill: {skill['name']} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error adding skill: {skill['name']} - {e}")


def test_execute():
    """测试执行功能"""
    print("\n" + "=" * 60)
    print("Testing Execute Functions")
    print("=" * 60)

    # 获取所有工具的列表
    try:
        # Test plugin
        print("\n1. Testing Plugin Execution...")
        plugins_response = requests.get(f"{API_BASE_URL}/plugins", timeout=5)
        if plugins_response.status_code == 200:
            plugins = plugins_response.json()
            if plugins:
                plugin_id = plugins[0].get('plugin_id')
                exec_response = requests.post(f"{API_BASE_URL}/plugins/{plugin_id}/execute", json={}, timeout=5)
                if exec_response.status_code == 200:
                    result = exec_response.json()
                    print(f"  ✓ Plugin execution successful!")
                    print(f"    Result: {json.dumps(result.get('result', {}), indent=2)}")
                else:
                    print(f"  ✗ Plugin execution failed: {exec_response.status_code}")

        # Test MCP
        print("\n2. Testing MCP Execution...")
        mcps_response = requests.get(f"{API_BASE_URL}/mcp", timeout=5)
        if mcps_response.status_code == 200:
            mcps = mcps_response.json()
            if mcps:
                mcp_id = mcps[0].get('mcp_id')
                exec_response = requests.post(f"{API_BASE_URL}/mcp/{mcp_id}/execute", json={}, timeout=5)
                if exec_response.status_code == 200:
                    result = exec_response.json()
                    print(f"  ✓ MCP execution successful!")
                    print(f"    Result: {json.dumps(result.get('result', {}), indent=2)}")
                else:
                    print(f"  ✗ MCP execution failed: {exec_response.status_code}")

        # Test Function
        print("\n3. Testing Function Execution...")
        functions_response = requests.get(f"{API_BASE_URL}/functions", timeout=5)
        if functions_response.status_code == 200:
            functions = functions_response.json()
            if functions:
                function_id = functions[0].get('function_id')
                exec_response = requests.post(f"{API_BASE_URL}/functions/{function_id}/execute", json={}, timeout=5)
                if exec_response.status_code == 200:
                    result = exec_response.json()
                    print(f"  ✓ Function execution successful!")
                    print(f"    Result: {json.dumps(result.get('result', {}), indent=2)}")
                else:
                    print(f"  ✗ Function execution failed: {exec_response.status_code}")

        # Test Skill
        print("\n4. Testing Skill Execution...")
        skills_response = requests.get(f"{API_BASE_URL}/skills", timeout=5)
        if skills_response.status_code == 200:
            skills = skills_response.json()
            if skills:
                skill_id = skills[0].get('skill_id')
                exec_response = requests.post(f"{API_BASE_URL}/skills/{skill_id}/execute", json={}, timeout=5)
                if exec_response.status_code == 200:
                    result = exec_response.json()
                    print(f"  ✓ Skill execution successful!")
                    print(f"    Result: {json.dumps(result.get('result', {}), indent=2)}")
                else:
                    print(f"  ✗ Skill execution failed: {exec_response.status_code}")

    except Exception as e:
        print(f"  ✗ Error during testing: {e}")


def main():
    """Main function"""
    print("=" * 60)
    print("Adding Test Tools Data via API")
    print("=" * 60)
    print(f"API Server: {API_BASE_URL}")
    print()

    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/plugins", timeout=2)
        if response.status_code != 200:
            print("⚠ API server may not be running properly")
    except:
        print("✗ Cannot connect to API server!")
        print("Please make sure api_server.py is running.")
        return

    add_test_plugins()
    add_test_mcps()
    add_test_functions()
    add_test_skills()

    print("\n" + "=" * 60)
    print("✓ All test data added successfully!")
    print("=" * 60)

    # Test execute functions
    test_execute()

    print("\n" + "=" * 60)
    print("Done! You can now test in the frontend.")
    print("=" * 60)


if __name__ == "__main__":
    main()
