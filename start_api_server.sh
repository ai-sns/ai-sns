#!/bin/bash
echo "Starting AI-SNS API Server with Tools module..."
echo "=============================================="
cd /root/sharedata3/ai-sns-el

# 设置Python路径
export PYTHONPATH=/root/sharedata3/ai-sns-el:$PYTHONPATH

# 启动服务器
python3 api_server_modular.py

# 或者使用uvicorn
# uvicorn api_server_modular:app --host 0.0.0.0 --port 8788 --reload
