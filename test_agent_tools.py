#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Tools Integration Test Script
测试Agent工具集成功能
"""

import requests
import json
import time

# 配置
API_BASE = "http://localhost:8788/api"
AGENT_ID = 1  # Agent 1 (Altman)

def test_get_agent_tools():
    """测试获取Agent的工具列表"""
    print("\n" + "="*60)
    print("测试 1: 获取Agent的工具列表")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/agent/{AGENT_ID}/tools")
        result = response.json()

        if result.get("success"):
            tools = result.get("data", {}).get("tools", [])
            print(f"✓ 成功获取 {len(tools)} 个工具")

            for i, tool in enumerate(tools, 1):
                tool_type = tool.get("tool_type")
                tool_name = tool.get("name")
                priority = tool.get("priority")
                enabled = tool.get("enabled")

                print(f"\n  {i}. [{tool_type.upper()}] {tool_name}")
                print(f"     优先级: {priority}, 状态: {'启用' if enabled else '禁用'}")

                # 显示工具描述
                description = tool.get("description", "").strip()
                if description:
                    print(f"     描述: {description[:80]}...")

            return True
        else:
            print(f"✗ 获取工具失败: {result.get('error', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_agent_info():
    """测试获取Agent实例信息"""
    print("\n" + "="*60)
    print("测试 2: 获取Agent实例信息")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE}/agent/{AGENT_ID}/info")
        result = response.json()

        if result.get("success"):
            agent = result.get("data", {})
            print(f"✓ Agent名称: {agent.get('name')}")
            print(f"  模型: {agent.get('llm_config', {}).get('model_name')}")
            print(f"  工具数量: {agent.get('tools_count')}")
            print(f"  工具已加载: {'是' if agent.get('tools_loaded') else '否'}")
            return True
        else:
            print(f"✗ 获取Agent信息失败: {result.get('error', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_agent_chat_with_calculator():
    """测试Agent调用计算器工具"""
    print("\n" + "="*60)
    print("测试 3: Agent调用计算器工具")
    print("="*60)

    message = "帮我计算: 123 * 456 + 789"
    print(f"发送消息: {message}")

    try:
        response = requests.post(
            f"{API_BASE}/agent/{AGENT_ID}/chat",
            json={
                "message": message,
                "conversation_id": f"test_calc_{int(time.time())}",
                "use_memory": False
            }
        )
        result = response.json()

        if result.get("success"):
            reply = result.get("data", {}).get("reply", "")
            print(f"\n✓ Agent回复:\n{reply}")

            # 检查是否包含计算结果
            expected_result = 123 * 456 + 789  # 56877
            if str(expected_result) in reply:
                print(f"\n✓ 工具调用成功！计算结果正确: {expected_result}")
                return True
            else:
                print(f"\n⚠ Agent返回了回复，但未找到预期的计算结果 {expected_result}")
                return False
        else:
            print(f"✗ 聊天失败: {result.get('error', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_agent_chat_with_greeting():
    """测试Agent调用问候函数"""
    print("\n" + "="*60)
    print("测试 4: Agent调用问候函数")
    print("="*60)

    message = "向我问好"
    print(f"发送消息: {message}")

    try:
        response = requests.post(
            f"{API_BASE}/agent/{AGENT_ID}/chat",
            json={
                "message": message,
                "conversation_id": f"test_greeting_{int(time.time())}",
                "use_memory": False
            }
        )
        result = response.json()

        if result.get("success"):
            reply = result.get("data", {}).get("reply", "")
            print(f"\n✓ Agent回复:\n{reply}")

            # 检查是否包含问候语
            if any(word in reply.lower() for word in ["hello", "你好", "hi", "欢迎", "问候"]):
                print(f"\n✓ 工具调用成功！包含问候语")
                return True
            else:
                print(f"\n⚠ Agent返回了回复，但未找到问候语")
                return False
        else:
            print(f"✗ 聊天失败: {result.get('error', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def verify_database_tools():
    """验证数据库中的工具配置"""
    print("\n" + "="*60)
    print("验证: 数据库中的工具配置")
    print("="*60)

    import sqlite3

    try:
        conn = sqlite3.connect('db/db.sqlite')
        cursor = conn.cursor()

        # 查询Agent 1的工具
        cursor.execute('''
            SELECT
                at.tool_type,
                at.tool_id,
                CASE at.tool_type
                    WHEN 'plugin' THEN (SELECT name FROM pluginmng WHERE plugin_id = at.tool_id)
                    WHEN 'mcp' THEN (SELECT name FROM mcp_mng WHERE mcp_id = at.tool_id)
                    WHEN 'function' THEN (SELECT name FROM function_mng WHERE function_id = at.tool_id)
                    WHEN 'skill' THEN (SELECT name FROM skill_mng WHERE skill_id = at.tool_id)
                END as tool_name,
                at.enabled,
                at.priority
            FROM agent_tools at
            WHERE at.agent_id = ?
            ORDER BY at.priority DESC
        ''', (AGENT_ID,))

        rows = cursor.fetchall()

        if rows:
            print(f"✓ 数据库中找到 {len(rows)} 个工具配置:")
            for row in rows:
                tool_type, tool_id, tool_name, enabled, priority = row
                status = "启用" if enabled else "禁用"
                print(f"  [{tool_type:8}] {tool_name:40} (优先级: {priority}, {status})")

            conn.close()
            return True
        else:
            print("✗ 数据库中没有找到工具配置")
            conn.close()
            return False

    except Exception as e:
        print(f"✗ 数据库查询失败: {e}")
        return False


def main():
    """主测试流程"""
    print("\n" + "#"*60)
    print("# Agent Tools Integration Test")
    print("# Agent工具集成测试")
    print("#"*60)

    # 检查后端是否运行
    print("\n检查后端服务器...")
    try:
        response = requests.get(f"{API_BASE}/agent")
        print("✓ 后端服务器运行正常")
    except Exception as e:
        print(f"✗ 无法连接到后端服务器: {e}")
        print("\n请先启动后端服务器:")
        print("  cd /mnt/c/dev/agi-ev/ai-sns-el")
        print("  python3 api_server.py")
        return

    # 运行测试
    results = []

    # 1. 验证数据库配置
    results.append(("数据库工具配置", verify_database_tools()))

    # 2. 测试API接口
    results.append(("获取Agent工具列表", test_get_agent_tools()))
    results.append(("获取Agent实例信息", test_agent_info()))

    # 3. 测试工具调用
    results.append(("调用计算器工具", test_agent_chat_with_calculator()))
    results.append(("调用问候函数", test_agent_chat_with_greeting()))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status:8} - {test_name}")

    print("\n" + "-"*60)
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！Agent工具集成成功！")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查配置")
        print("\n常见问题:")
        print("  1. 确认后端服务器正在运行: python3 api_server.py")
        print("  2. 确认Agent 1已关联工具（运行 verify_database_tools）")
        print("  3. 确认LLM配置正确（需要API key）")
        print("  4. 查看后端日志了解详细错误信息")


if __name__ == "__main__":
    main()
