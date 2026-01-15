#!/usr/bin/env python3
"""
最小化API服务器 - 仅启动Tools模块用于测试
"""
import sys
import os
sys.path.insert(0, '/root/sharedata3/ai-sns-el')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 仅导入Tools模块
from backend.modules.tools.router import router as tools_router

app = FastAPI(title="AI-SNS Tools API (Minimal)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册Tools路由
app.include_router(tools_router, prefix="/api/tools", tags=["Tools"])

@app.get("/")
def root():
    return {"status": "running", "module": "tools-only"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("="*60)
    print("Starting Minimal API Server (Tools Module Only)")
    print("Port: 8788")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8788)
