#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools Module - 测试数据创建脚本
快速创建测试数据以验证Tools模块功能
"""

import requests
import json
import sys

API_BASE = "http://127.0.0.1:8788/api/tools"

# 测试数据
TEST_DATA = {
    "plugins": [
        {
            "name": "天气查询插件",
            "description": "实时获取全球任意城市的天气信息，包括温度、湿度、风速等详细数据",
            "plugin_type": "weather",
            "instruction": "使用此插件获取指定城市的实时天气数据，支持中英文城市名称",
            "confirm_needed": False
        },
        {
            "name": "网页搜索插件",
            "description": "在互联网上搜索相关信息，支持多个搜索引擎",
            "plugin_type": "search",
            "instruction": "输入搜索关键词，返回搜索结果列表",
            "confirm_needed": False
        },
        {
            "name": "文件操作插件",
            "description": "读取、写入、修改本地文件系统中的文件",
            "plugin_type": "file_system",
            "instruction": "提供文件路径和操作类型，支持读、写、删除等操作",
            "confirm_needed": True
        }
    ],
    "mcp": [
        {
            "name": "本地文件服务器",
            "description": "MCP服务器，用于访问本地文件系统",
            "mcp_type": "stdio",
            "instruction": "通过stdio协议连接本地文件系统",
            "confirm_needed": False
        },
        {
            "name": "数据库连接服务",
            "description": "MCP服务器，提供数据库查询功能",
            "mcp_type": "http",
            "instruction": "通过HTTP协议连接到数据库服务",
            "confirm_needed": True
        }
    ],
    "functions": [
        {
            "name": "calculate_sum",
            "description": "计算一组数字的总和",
            "function_type": "python",
            "instruction": "输入数字数组，返回总和",
            "confirm_needed": False
        },
        {
            "name": "format_date",
            "description": "格式化日期字符串",
            "function_type": "python",
            "instruction": "输入日期和格式模板，返回格式化后的日期字符串",
            "confirm_needed": False
        },
        {
            "name": "execute_shell",
            "description": "执行系统shell命令",
            "function_type": "shell",
            "instruction": "输入shell命令，返回执行结果",
            "confirm_needed": True
        }
    ],
    "skills": [
        {
            "name": "屏幕截图",
            "description": "捕获当前屏幕或指定区域的截图",
            "skill_type": "screenshot",
            "instruction": "可选指定截图区域坐标，返回图片路径",
            "confirm_needed": False
        },
        {
            "name": "鼠标点击",
            "description": "模拟鼠标点击操作",
            "skill_type": "mouse_click",
            "instruction": "指定坐标位置进行鼠标点击",
            "confirm_needed": True
        },
        {
            "name": "键盘输入",
            "description": "模拟键盘输入文本",
            "skill_type": "keyboard_input",
            "instruction": "输入要模拟键入的文本内容",
            "confirm_needed": True
        }
    ]
}

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get("http://127.0.0.1:8788/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务器连接成功")
            return True
        else:
            print(f"❌ API服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保服务器正在运行")
        print("   运行命令: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def create_plugins():
    """创建测试插件"""
    print("\n📦 创建测试插件...")
    created = 0
    for plugin in TEST_DATA["plugins"]:
        try:
            response = requests.post(
                f"{API_BASE}/plugins",
                json=plugin,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 创建插件: {plugin['name']}")
                created += 1
            else:
                print(f"  ❌ 创建失败: {plugin['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {plugin['name']} - {e}")
    print(f"成功创建 {created}/{len(TEST_DATA['plugins'])} 个插件")
    return created

def create_mcps():
    """创建测试MCP"""
    print("\n🖥️  创建测试MCP...")
    created = 0
    for mcp in TEST_DATA["mcp"]:
        try:
            response = requests.post(
                f"{API_BASE}/mcp",
                json=mcp,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 创建MCP: {mcp['name']}")
                created += 1
            else:
                print(f"  ❌ 创建失败: {mcp['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {mcp['name']} - {e}")
    print(f"成功创建 {created}/{len(TEST_DATA['mcp'])} 个MCP")
    return created

def create_functions():
    """创建测试函数"""
    print("\n⚙️  创建测试函数...")
    created = 0
    for function in TEST_DATA["functions"]:
        try:
            response = requests.post(
                f"{API_BASE}/functions",
                json=function,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 创建函数: {function['name']}")
                created += 1
            else:
                print(f"  ❌ 创建失败: {function['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {function['name']} - {e}")
    print(f"成功创建 {created}/{len(TEST_DATA['functions'])} 个函数")
    return created

def create_skills():
    """创建测试技能"""
    print("\n🎯 创建测试技能...")
    created = 0
    for skill in TEST_DATA["skills"]:
        try:
            response = requests.post(
                f"{API_BASE}/skills",
                json=skill,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ 创建技能: {skill['name']}")
                created += 1
            else:
                print(f"  ❌ 创建失败: {skill['name']} - {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {skill['name']} - {e}")
    print(f"成功创建 {created}/{len(TEST_DATA['skills'])} 个技能")
    return created

def verify_data():
    """验证创建的数据"""
    print("\n🔍 验证数据...")

    endpoints = [
        ("Plugins", f"{API_BASE}/plugins"),
        ("MCP", f"{API_BASE}/mcp"),
        ("Functions", f"{API_BASE}/functions"),
        ("Skills", f"{API_BASE}/skills")
    ]

    for name, url in endpoints:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ {name}: {len(data)} 条记录")
            else:
                print(f"  ❌ {name}: 获取失败")
        except Exception as e:
            print(f"  ❌ {name}: 错误 - {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("Tools Module - 测试数据创建脚本")
    print("=" * 60)

    # 测试连接
    if not test_api_connection():
        print("\n请先启动API服务器:")
        print("  cd /root/sharedata3/ai-sns-el")
        print("  python api_server.py")
        sys.exit(1)

    # 创建测试数据
    total_created = 0
    total_created += create_plugins()
    total_created += create_mcps()
    total_created += create_functions()
    total_created += create_skills()

    # 验证数据
    verify_data()

    print("\n" + "=" * 60)
    print(f"✅ 完成！共创建 {total_created} 条测试数据")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 刷新 Electron 应用 (Ctrl+R 或 F5)")
    print("  2. 点击 Tools 图标")
    print("  3. 点击侧边栏的4个分类查看数据")
    print("\n如需清空数据，请手动删除数据库文件:")
    print("  rm db/db.sqlite")
    print("  然后重启API服务器")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
