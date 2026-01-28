#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 reorder API
"""

import requests
import json

BASE_URL = "http://localhost:8788"

def test_reorder():
    """测试重排序 API"""
    print("=== 测试重排序 API ===")
    
    # 测试数据
    test_data = [
        {"id": 1, "position": 0},
        {"id": 2, "position": 1},
        {"id": 3, "position": 2}
    ]
    
    print(f"发送数据: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/system/web-mng/reorder",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"响应数据: {response.json()}")
            print("\n✅ 测试成功！")
        else:
            print(f"错误响应: {response.text}")
            print("\n❌ 测试失败！")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reorder()
