#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Web Sidebar API 功能
"""

import requests
import json

BASE_URL = "http://localhost:8788"

def test_get_web_mng():
    """测试获取 web 管理数据"""
    print("\n=== 测试获取 Web 管理数据 ===")
    response = requests.get(f"{BASE_URL}/api/system/web-mng")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data.get('success')}")
    print(f"数据数量: {len(data.get('data', []))}")
    if data.get('data'):
        print(f"第一项: {data['data'][0]}")
    return data.get('data', [])

def test_create_web_mng():
    """测试创建 web 管理项"""
    print("\n=== 测试创建 Web 管理项 ===")
    new_item = {
        "name": "Test LLM",
        "title": "Test LLM Service",
        "type": "LLM",
        "url": "https://test.example.com",
        "description": "This is a test LLM service",
        "filename": "test.png"
    }
    response = requests.post(f"{BASE_URL}/api/system/web-mng", json=new_item)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data.get('success')}")
    if data.get('data'):
        print(f"创建的项目 ID: {data['data'].get('id')}")
        return data['data'].get('id')
    return None

def test_update_web_mng(item_id):
    """测试更新 web 管理项"""
    print(f"\n=== 测试更新 Web 管理项 (ID: {item_id}) ===")
    update_data = {
        "name": "Updated Test LLM",
        "title": "Updated Test LLM Service",
        "description": "This is an updated test LLM service"
    }
    response = requests.put(f"{BASE_URL}/api/system/web-mng/{item_id}", json=update_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data.get('success')}")
    if data.get('data'):
        print(f"更新后的名称: {data['data'].get('name')}")

def test_reorder_web_mng(items):
    """测试重排序 web 管理项"""
    print("\n=== 测试重排序 Web 管理项 ===")
    # 反转前3个项目的顺序
    reorder_data = [
        {"id": items[i]['id'], "position": i}
        for i in range(min(3, len(items)))
    ]
    response = requests.put(f"{BASE_URL}/api/system/web-mng/reorder", json=reorder_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data.get('success')}")

def test_delete_web_mng(item_id):
    """测试删除 web 管理项"""
    print(f"\n=== 测试删除 Web 管理项 (ID: {item_id}) ===")
    response = requests.delete(f"{BASE_URL}/api/system/web-mng/{item_id}")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data.get('success')}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("Web Sidebar API 功能测试")
    print("=" * 60)
    
    try:
        # 1. 获取现有数据
        items = test_get_web_mng()
        
        # 2. 创建新项目
        new_item_id = test_create_web_mng()
        
        if new_item_id:
            # 3. 更新项目
            test_update_web_mng(new_item_id)
            
            # 4. 重新获取数据
            items = test_get_web_mng()
            
            # 5. 测试重排序
            if len(items) >= 2:
                test_reorder_web_mng(items)
            
            # 6. 删除测试项目
            test_delete_web_mng(new_item_id)
            
            # 7. 最终验证
            test_get_web_mng()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到后端服务器")
        print("请确保后端服务器正在运行: python api_server.py")
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
