#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test all four tools modules execute functions
测试四个工具模块的执行功能
"""

import requests
import json


API_BASE_URL = "http://127.0.0.1:8788/api/tools"


def test_all_tools():
    """测试所有工具的执行功能"""
    print("=" * 70)
    print("Testing All Tools Execute Functions")
    print("=" * 70)

    categories = [
        ("plugins", "Plugin"),
        ("mcp", "MCP"),
        ("functions", "Function"),
        ("skills", "Skill")
    ]

    for endpoint, name in categories:
        print(f"\n{name}s:")
        print("-" * 70)

        try:
            # Get all tools
            response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
            if response.status_code != 200:
                print(f"  ✗ Failed to get {name}s: {response.status_code}")
                continue

            tools = response.json()
            if not tools:
                print(f"  ⚠ No {name}s found")
                continue

            print(f"  Found {len(tools)} {name}(s)\n")

            # Test each tool
            for i, tool in enumerate(tools[:3], 1):  # Test first 3 only
                tool_id = tool.get(f'{endpoint[:-1]}_id')  # Remove 's' from endpoint
                tool_name = tool.get('name', 'Unnamed')

                print(f"  {i}. {tool_name} (ID: {tool_id})")

                # Execute the tool
                try:
                    exec_response = requests.post(
                        f"{API_BASE_URL}/{endpoint}/{tool_id}/execute",
                        json={},
                        timeout=5
                    )

                    if exec_response.status_code == 200:
                        result = exec_response.json()
                        exec_result = result.get('result', {})

                        print(f"     ✓ Execution successful!")
                        print(f"     Status: {exec_result.get('status', 'N/A')}")
                        print(f"     Message: {exec_result.get('message', 'N/A')}")
                        print(f"     Timestamp: {exec_result.get('timestamp', 'N/A')}")
                    else:
                        print(f"     ✗ Execution failed: {exec_response.status_code}")
                        print(f"     Error: {exec_response.text[:200]}")

                except Exception as e:
                    print(f"     ✗ Error: {e}")

                print()

        except Exception as e:
            print(f"  ✗ Error testing {name}s: {e}\n")

    print("=" * 70)
    print("Testing Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_all_tools()
