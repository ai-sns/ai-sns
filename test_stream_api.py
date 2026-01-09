#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试流式聊天 API
"""

import requests
import json
import sys

def test_stream_api():
    """测试流式聊天 API"""
    url = "http://localhost:8788/api/chat/stream"

    # 测试数据
    data = {
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍自己"}
        ]
    }

    print("=" * 60)
    print("测试流式聊天 API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("=" * 60)
    print("AI 回复:")
    print("-" * 60)

    try:
        # 发送流式请求
        response = requests.post(
            url,
            json=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            print(f"错误: HTTP {response.status_code}")
            print(response.text)
            return False

        # 处理流式响应
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')

                # 处理 SSE 格式
                if line_str.startswith('event:'):
                    event_type = line_str[6:].strip()
                    continue

                if line_str.startswith('data:'):
                    data_str = line_str[5:].strip()
                    try:
                        data_obj = json.loads(data_str)

                        # 打印内容
                        if 'content' in data_obj:
                            content = data_obj['content']
                            print(content, end='', flush=True)
                            full_response += content

                        # 检查完成状态
                        if data_obj.get('status') == 'completed':
                            break

                        # 检查错误
                        if 'error' in data_obj:
                            print(f"\n错误: {data_obj['error']}")
                            return False

                    except json.JSONDecodeError:
                        pass

        print()
        print("-" * 60)
        print(f"✓ 测试成功！共接收 {len(full_response)} 个字符")
        print("=" * 60)
        return True

    except requests.exceptions.ConnectionError:
        print("✗ 连接失败：无法连接到 API 服务器")
        print("请确保后端服务已启动: python api_server.py --port 8788")
        return False
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
        return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_health():
    """测试健康检查端点"""
    url = "http://localhost:8788/health"
    print("\n检查 API 服务健康状态...")

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API 服务运行正常")
            print(f"  状态: {data.get('status')}")
            print(f"  时间: {data.get('timestamp')}")
            return True
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到 API 服务器: {e}")
        print("请确保后端服务已启动: python api_server.py --port 8788")
        return False

if __name__ == "__main__":
    print("\n🚀 AI-SNS 流式聊天 API 测试工具\n")

    # 先检查健康状态
    if not test_health():
        sys.exit(1)

    print()

    # 测试流式聊天
    if test_stream_api():
        sys.exit(0)
    else:
        sys.exit(1)
