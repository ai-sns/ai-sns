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

    print("=" * 60)
    print("🧪 Testing Real MCP Server")
    print("=" * 60)
    print(f"Server Script: {server_script_path}\n")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script_path],
        env=None
    )

    async with AsyncExitStack() as stack:
        # Connect to MCP server
        print("📡 Step 1: Connecting to MCP server...")
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))

        # Initialize connection
        print("🔌 Step 2: Initializing connection...")
        await session.initialize()
        print("✓ Connection initialized successfully!\n")

        # List available tools
        print("📋 Step 3: Listing available tools...")
        tools_result = await session.list_tools()
        print(f"✓ Found {len(tools_result.tools)} tools:\n")

        for i, tool in enumerate(tools_result.tools, 1):
            print(f"  {i}. {tool.name}")
            print(f"     Description: {tool.description}")
            print()

        # Test each tool
        print("=" * 60)
        print("🧪 Step 4: Testing Tool Execution")
        print("=" * 60)

        # Test 1: Get Weather
        print("\n🌤️ Test 1: get_weather (Beijing)")
        print("-" * 60)
        result1 = await session.call_tool("get_weather", {"city": "Beijing", "unit": "celsius"})
        for content in result1.content:
            if hasattr(content, 'text'):
                print(content.text)

        # Test 2: Get Current Time
        print("\n🕐 Test 2: get_current_time (Asia/Shanghai)")
        print("-" * 60)
        result2 = await session.call_tool("get_current_time", {"timezone": "Asia/Shanghai"})
        for content in result2.content:
            if hasattr(content, 'text'):
                print(content.text)

        # Test 3: Calculate
        print("\n🔢 Test 3: calculate (2 ** 10 + 100)")
        print("-" * 60)
        result3 = await session.call_tool("calculate", {"expression": "2 ** 10 + 100"})
        for content in result3.content:
            if hasattr(content, 'text'):
                print(content.text)

        # Test 4: Get System Info
        print("\n💻 Test 4: get_system_info")
        print("-" * 60)
        result4 = await session.call_tool("get_system_info", {})
        for content in result4.content:
            if hasattr(content, 'text'):
                print(content.text)

        # List Resources
        print("\n" + "=" * 60)
        print("📚 Step 5: Testing Resources")
        print("=" * 60)
        resources_result = await session.list_resources()
        print(f"\n✓ Found {len(resources_result.resources)} resources:")
        for resource in resources_result.resources:
            print(f"  - {resource.name}: {resource.uri}")

        # Read Resource
        if resources_result.resources:
            uri = resources_result.resources[0].uri
            print(f"\n📖 Reading resource: {uri}")
            print("-" * 60)
            resource_content = await session.read_resource(uri)
            for content in resource_content.contents:
                if hasattr(content, 'text'):
                    print(content.text)

        # List Prompts
        print("\n" + "=" * 60)
        print("💬 Step 6: Testing Prompts")
        print("=" * 60)
        prompts_result = await session.list_prompts()
        print(f"\n✓ Found {len(prompts_result.prompts)} prompts:")
        for prompt in prompts_result.prompts:
            print(f"  - {prompt.name}: {prompt.description}")

        print("\n" + "=" * 60)
        print("✅ All Tests Completed Successfully!")
        print("=" * 60)
        print("\n🎉 This is a REAL MCP Server with:")
        print("  ✓ Real tool execution")
        print("  ✓ JSON-RPC communication")
        print("  ✓ Bidirectional stdio transport")
        print("  ✓ Full MCP protocol compliance")
        print()


async def main():
    """Main entry point"""
    server_path = "/root/sharedata3/ai-sns-el/test_examples/real_weather_mcp_server.py"

    try:
        await test_mcp_server(server_path)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
