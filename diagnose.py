#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-SNS 配置诊断工具
检查 API 配置是否正确
"""

import sys
import os
import requests
import yaml
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}")

def print_info(msg):
    print(f"ℹ {msg}")

def check_config_file():
    """检查配置文件"""
    print_header("1. 检查配置文件")

    config_file = Path('ai_config.yaml')
    if not config_file.exists():
        print_error("配置文件 ai_config.yaml 不存在")
        print_info("请运行: cp ai_config.yaml.example ai_config.yaml")
        return False

    print_success("配置文件存在")

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        ai_config = config.get('ai', {})
        api_key = ai_config.get('api_key', '')
        api_base = ai_config.get('api_base', '')
        model = ai_config.get('model', '')

        print_info(f"API Base: {api_base}")
        print_info(f"Model: {model}")

        if not api_key:
            print_error("API key 未配置")
            print_info("请在 ai_config.yaml 中配置 api_key")
            return False

        if api_key == "your-api-key-here":
            print_error("API key 仍是示例值，请修改为真实的 API key")
            return False

        print_success(f"API Key: {api_key[:10]}...{api_key[-4:]}")
        return True

    except Exception as e:
        print_error(f"读取配置文件失败: {e}")
        return False

def check_api_server():
    """检查 API 服务器"""
    print_header("2. 检查 API 服务器")

    try:
        response = requests.get('http://localhost:8788/health', timeout=5)
        if response.status_code == 200:
            print_success("API 服务器运行正常")
            data = response.json()
            print_info(f"状态: {data.get('status')}")
            print_info(f"时间: {data.get('timestamp')}")
            return True
        else:
            print_error(f"API 服务器响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("无法连接到 API 服务器")
        print_info("请启动服务: python api_server.py --port 8788")
        return False
    except Exception as e:
        print_error(f"检查失败: {e}")
        return False

def check_config_status():
    """检查配置状态"""
    print_header("3. 检查 AI 配置状态")

    try:
        response = requests.get('http://localhost:8788/api/config/status', timeout=5)
        if response.status_code == 200:
            data = response.json()

            if data.get('has_api_key'):
                print_success("API Key 已配置")
                print_info(f"API Base: {data.get('api_base')}")
                print_info(f"Model: {data.get('model')}")
                print_info(f"API Key: {data.get('api_key_preview')}")
                return True
            else:
                print_error("API Key 未配置")
                print_info(data.get('recommendation', ''))
                return False
        else:
            print_error(f"获取配置状态失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"检查失败: {e}")
        return False

def test_stream_api():
    """测试流式 API"""
    print_header("4. 测试流式聊天 API")

    try:
        response = requests.post(
            'http://localhost:8788/api/chat/stream',
            json={'messages': [{'role': 'user', 'content': '你好'}]},
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=30
        )

        if response.status_code != 200:
            print_error(f"API 请求失败: HTTP {response.status_code}")
            print_info(response.text)
            return False

        print_info("正在接收流式响应...")
        received_data = False

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data:'):
                    import json
                    try:
                        data_str = line_str[5:].strip()
                        data = json.loads(data_str)

                        if data.get('content'):
                            received_data = True
                            print(data['content'], end='', flush=True)

                        if data.get('error'):
                            print()
                            print_error(f"API 返回错误: {data['error']}")
                            return False

                        if data.get('status') == 'completed':
                            break
                    except:
                        pass

        print()
        if received_data:
            print_success("流式聊天 API 测试成功")
            return True
        else:
            print_error("未接收到任何数据")
            return False

    except Exception as e:
        print_error(f"测试失败: {e}")
        return False

def main():
    print("\n🔍 AI-SNS 配置诊断工具\n")

    results = []

    # 1. 检查配置文件
    results.append(("配置文件", check_config_file()))

    # 2. 检查 API 服务器
    results.append(("API 服务器", check_api_server()))

    # 如果服务器运行，继续检查
    if results[-1][1]:
        # 3. 检查配置状态
        results.append(("配置状态", check_config_status()))

        # 如果配置正常，测试 API
        if results[-1][1]:
            # 4. 测试流式 API
            results.append(("流式 API", test_stream_api()))

    # 显示总结
    print_header("诊断总结")

    all_passed = True
    for name, passed in results:
        if passed:
            print_success(f"{name}: 正常")
        else:
            print_error(f"{name}: 异常")
            all_passed = False

    print()
    if all_passed:
        print("🎉 所有检查通过！系统运行正常。")
        return 0
    else:
        print("⚠️  发现问题，请根据上述提示进行修复。")
        print()
        print("常见问题解决方案:")
        print("1. 配置文件问题: cp ai_config.yaml.example ai_config.yaml")
        print("2. API Key 未配置: 编辑 ai_config.yaml，填入正确的 API key")
        print("3. 服务未启动: python api_server.py --port 8788")
        return 1

if __name__ == "__main__":
    sys.exit(main())
