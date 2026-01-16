#!/usr/bin/env python3
import sys, json
print("=" * 50)
print("真实Greeting Function执行")
print("=" * 50)
if len(sys.argv) > 1:
    params = json.loads(sys.argv[1])
    name = params.get('name', '朋友')
else:
    name = '朋友'
print(f"\n你好，{name}！很高兴见到你！")
print("祝你今天过得愉快！")
print("\n✓ 问候成功!")
