# -*- coding: utf-8 -*-
"""
PyCharm 调试问题的修复启动脚本
在 PyCharm 中运行此文件而不是直接运行 api_server.py
"""
import os
import sys
from pathlib import Path

# 强制设置工作目录
project_dir = Path(__file__).resolve().parent
os.chdir(project_dir)

# 强制添加 backend 到 sys.path
backend_dir = project_dir / 'backend'
sys.path.insert(0, str(backend_dir))

# 打印调试信息
print("=" * 60)
print("API Server 启动 (PyCharm 调试兼容模式)")
print("=" * 60)
print(f"工作目录: {os.getcwd()}")
print(f"Python 路径: {sys.executable}")
print(f"Backend 路径: {backend_dir}")
print()

# 测试关键模块导入
print("[测试模块导入]")
try:
    from backend.modules.km.router import router as km_router
    print(f"✓ KM 模块导入成功")
    print(f"  路由数量: {len(km_router.routes)}")
except Exception as e:
    print(f"✗ KM 模块导入失败: {e}")
    sys.exit(1)

try:
    from backend.modules.tools.router import router as tools_router
    print(f"✓ Tools 模块导入成功")
except Exception as e:
    print(f"✗ Tools 模块导入失败: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("模块导入测试通过，启动 API Server...")
print("=" * 60)
print()

# 导入并运行 api_server
exec(open('api_server.py', encoding='utf-8').read())
