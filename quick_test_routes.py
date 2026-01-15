#!/usr/bin/env python3
"""快速测试：检查api_server.py中的路由配置"""
import sys
sys.path.insert(0, '/root/sharedata3/ai-sns-el')

print("Checking api_server.py configuration...")
print("="*60)

# 检查文件内容
with open('api_server.py', 'r') as f:
    content = f.read()
    
# 检查tools_router导入
if 'from backend.modules.tools.router import router as tools_router' in content:
    print("✓ tools_router imported")
else:
    print("✗ tools_router NOT imported")

# 检查路由注册
if 'app.include_router(tools_router' in content:
    print("✓ tools_router registered")
    # 找到具体的注册行
    for line in content.split('\n'):
        if 'tools_router' in line and 'include_router' in line:
            print(f"  Line: {line.strip()}")
else:
    print("✗ tools_router NOT registered")

print("="*60)

# 检查router.py
print("\nChecking backend/modules/tools/router.py...")
with open('backend/modules/tools/router.py', 'r') as f:
    router_content = f.read()
    
if 'router = APIRouter()' in router_content:
    print("✓ router = APIRouter() (no prefix)")
elif 'router = APIRouter(prefix=' in router_content:
    print("⚠ router has prefix defined (might cause double prefix)")
    for line in router_content.split('\n'):
        if 'router = APIRouter' in line:
            print(f"  Line: {line.strip()}")
            
print("="*60)
