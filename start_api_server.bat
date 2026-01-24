@echo off
chcp 65001 >nul
title AI-SNS API Server (Virtual Environment)

echo ==========================================
echo   AI-SNS API Server
echo   Using Virtual Environment: venv
echo ==========================================
echo.

cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please create virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting API server with virtual environment...
echo.
venv\Scripts\python.exe api_server.py
