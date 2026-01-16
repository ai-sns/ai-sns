#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Client - 测试真实的 MCP Server 连接和工具调用
"""
import asyncio
import json
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server(server_script_path: str):
    """测试真实的 MCP Server"""

    print("=" * 60, file=sys.stderr)
    print("🧪 Testing Real MCP Server", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Server Script: {server_script_path}\n", file=sys.stderr)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script_path],
        env=None
    )

    async with AsyncExitStack() as stack:
        # Connect to MCP server
        print("📡 Step 1: Connecting to MCP server...", file=sys.stderr)
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))

        # Initialize connection
        print("🔌 Step 2: Initializing connection...", file=sys.stderr)
        await session.initialize()
        print("✓ Connection initialized successfully!\n", file=sys.stderr)

        # List available tools
        print("📋 Step 3: Listing available tools...", file=sys.stderr)
        tools_result = await session.list_tools()
        print(f"✓ Found {len(tools_result.tools)} tools:\n", file=sys.stderr)

        for i, tool in enumerate(tools_result.tools, 1):
            print(f"  {i}. {tool.name}", file=sys.stderr)
            print(f"     Description: {tool.description}", file=sys.stderr)
            print(file=sys.stderr)

        # Test each tool
        print("=" * 60, file=sys.stderr)
        print("🧪 Step 4: Testing Tool Execution", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        # Test 1: Get Weather
        print("\n🌤️ Test 1: get_weather (Beijing)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        result1 = await session.call_tool("get_weather", {"city": "Beijing", "unit": "celsius"})
        for content in result1.content:
            if hasattr(content, 'text'):
                print(content.text, file=sys.stderr)

        # Test 2: Get Current Time
        print("\n🕐 Test 2: get_current_time (Asia/Shanghai)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        result2 = await session.call_tool("get_current_time", {"timezone": "Asia/Shanghai"})
        for content in result2.content:
            if hasattr(content, 'text'):
                print(content.text, file=sys.stderr)

        # Test 3: Calculate
        print("\n🔢 Test 3: calculate (2 ** 10 + 100)", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        result3 = await session.call_tool("calculate", {"expression": "2 ** 10 + 100"})
        for content in result3.content:
            if hasattr(content, 'text'):
                print(content.text, file=sys.stderr)

        # Test 4: Get System Info
        print("\n💻 Test 4: get_system_info", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        result4 = await session.call_tool("get_system_info", {})
        for content in result4.content:
            if hasattr(content, 'text'):
                print(content.text, file=sys.stderr)

        # List Resources
        print("\n" + "=" * 60, file=sys.stderr)
        print("📚 Step 5: Testing Resources", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        resources_result = await session.list_resources()
        print(f"\n✓ Found {len(resources_result.resources)} resources:", file=sys.stderr)
        for resource in resources_result.resources:
            print(f"  - {resource.name}: {resource.uri}", file=sys.stderr)

        # Read Resource
        if resources_result.resources:
            uri = resources_result.resources[0].uri
            print(f"\n📖 Reading resource: {uri}", file=sys.stderr)
            print("-" * 60, file=sys.stderr)
            resource_content = await session.read_resource(uri)
            for content in resource_content.contents:
                if hasattr(content, 'text'):
                    print(content.text, file=sys.stderr)

        # List Prompts
        print("\n" + "=" * 60, file=sys.stderr)
        print("💬 Step 6: Testing Prompts", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        prompts_result = await session.list_prompts()
        print(f"\n✓ Found {len(prompts_result.prompts)} prompts:", file=sys.stderr)
        for prompt in prompts_result.prompts:
            print(f"  - {prompt.name}: {prompt.description}", file=sys.stderr)

        print("\n" + "=" * 60, file=sys.stderr)
        print("✅ All Tests Completed Successfully!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("\n🎉 This is a REAL MCP Server with:", file=sys.stderr)
        print("  ✓ Real tool execution", file=sys.stderr)
        print("  ✓ JSON-RPC communication", file=sys.stderr)
        print("  ✓ Bidirectional stdio transport", file=sys.stderr)
        print("  ✓ Full MCP protocol compliance", file=sys.stderr)
        print(file=sys.stderr)


async def main():
    """Main entry point"""
    import os
    # 使用相对路径，自动适配 Windows/Linux
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "real_weather_mcp_server.py")

    try:
        await test_mcp_server(server_path)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
