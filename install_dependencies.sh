#!/bin/bash
# 安装缺失的依赖包

echo "安装Python依赖包..."

pip3 install aiosqlite
pip3 install geopy
pip3 install geographiclib

echo "依赖安装完成！"
