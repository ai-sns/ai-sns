#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-SNS API Server - Tools模块可用版本
临时跳过有问题的依赖，优先启动Tools模块
"""

import os
import sys
from pathlib import Path

# 设置工作目录
app_directory = Path(__file__).resolve().parent
os.chdir(app_directory)
sys.path.insert(0, str(app_directory / 'backend'))

import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AI-SNS API",
    description="AI-SNS API Server with Tools Module",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
try:
    if os.path.exists("images"):
        app.mount("/images", StaticFiles(directory="images"), name="images")
    if os.path.exists("resource"):
        app.mount("/resource", StaticFiles(directory="resource"), name="resource")
    if os.path.exists("scripts"):
        app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
except Exception as e:
    logger.warning(f"Failed to mount static files: {e}")

# 导入Tools模块 - 这是主要功能
try:
    from backend.modules.tools.router import router as tools_router
    app.include_router(tools_router, prefix="/api/tools", tags=["Tools"])
    logger.info("✓ Tools Module loaded")
except Exception as e:
    logger.error(f"✗ Failed to load Tools module: {e}")

# 尝试导入其他模块（如果可用）
try:
    from backend.modules.system.router import router as system_router
    app.include_router(system_router, prefix="/api/system", tags=["System"])
    logger.info("✓ System Module loaded")
except Exception as e:
    logger.warning(f"⚠ System module not available: {e}")

try:
    from backend.modules.map.router import router as map_router
    app.include_router(map_router, prefix="/api/map", tags=["Map"])
    logger.info("✓ Map Module loaded")
except Exception as e:
    logger.warning(f"⚠ Map module not available: {e}")

try:
    from backend.modules.km.router import router as km_router
    app.include_router(km_router, prefix="/api/km", tags=["Knowledge Base"])
    logger.info("✓ KM Module loaded")
except Exception as e:
    logger.warning(f"⚠ KM module not available: {e}")

try:
    from backend.modules.plugins.router import router as plugins_router
    app.include_router(plugins_router, prefix="/api/plugins", tags=["Plugins"])
    logger.info("✓ Plugins Module loaded")
except Exception as e:
    logger.warning(f"⚠ Plugins module not available: {e}")

# JSON-RPC端点（兼容性）
@app.post("/jsonrpc")
async def jsonrpc_endpoint(request: Request):
    """JSON-RPC 2.0 接口（基本响应）"""
    try:
        body = await request.json()
        return {
            "jsonrpc": "2.0",
            "result": {"status": "ok"},
            "id": body.get("id")
        }
    except:
        return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}

# 健康检查
@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# 根端点
@app.get("/")
async def root():
    return {
        "message": "AI-SNS API Server",
        "version": "2.0.0",
        "status": "running",
        "modules": ["tools", "system", "map", "km", "plugins"],
        "docs": "/docs"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("="*60)
    logger.info("AI-SNS API Server Starting...")
    logger.info("Version: 2.0.0")
    logger.info("Primary Module: Tools")
    logger.info("="*60)

# 主函数
def main():
    try:
        uvicorn.run(
            "api_server_tools_ready:app",
            host="0.0.0.0",
            port=8788,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
