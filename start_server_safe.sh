#!/bin/bash
cd /root/sharedata3/ai-sns-el

echo "=================================================="
echo "启动 AI-SNS API Server"
echo "=================================================="

# 清理数据库锁
rm -f data/db.sqlite-shm data/db.sqlite-wal db/db.sqlite-shm db/db.sqlite-wal 2>/dev/null
echo "✓ 数据库锁已清理"

# 检查端口
if lsof -i:8788 >/dev/null 2>&1; then
    echo "⚠ 端口8788已被占用，正在停止..."
    pkill -9 -f "python.*8788"
    sleep 2
fi

echo "✓ 端口8788可用"
echo ""
echo "正在启动服务器..."
echo "=================================================="

# 启动服务器
python3 api_server.py

