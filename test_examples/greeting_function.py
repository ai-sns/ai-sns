#!/usr/bin/env python3
import sys, json, platform
print("=" * 50)
print("真实Function执行")
print("=" * 50)
try:
    params = json.loads(sys.stdin.read()) if sys.stdin.read() else {}
    name = params.get('name', 'World')
    count = params.get('count', 3)
except:
    name, count = 'World', 3
print(f"\n参数: name={name}, count={count}")
for i in range(count):
    print(f"  [{i+1}] Hello, {name}!")
print(f"\n系统: {platform.system()} Python {platform.python_version()}")
print("✓ Function执行成功!")
