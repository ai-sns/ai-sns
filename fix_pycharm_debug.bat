@echo off
chcp 65001 >nul
echo ==========================================
echo PyCharm 调试问题诊断
echo ==========================================
echo.

echo [问题说明]
echo PyCharm 调试模式运行: 404
echo 命令行直接运行: 正常
echo.

echo [可能的原因]
echo 1. PyCharm 调试器 (pydevd.py) 可能在某些情况下影响模块导入
echo 2. 工作目录可能不同
echo 3. Python 路径可能被修改
echo.

echo [解决方案]
echo.

echo [方案1] 修改 PyCharm 运行配置 (推荐)
echo --------------------------------
echo 1. 在 PyCharm 中打开 Run ^> Edit Configurations...
echo 2. 选择 api_server 配置
echo 3. 确认以下设置:
echo    - Interpreter: C:\dev\agi-ev\ai-sns-el\venv\Scripts\python.exe
echo    - Working directory: C:\dev\agi-ev\ai-sns-el
echo    - Environment variables: PYTHONUNBUFFERED=1
echo 4. 在 Environment variables 中添加:
echo    - PYTHONPATH=C:\dev\agi-ev\ai-sns-el
echo 5. 保存配置
echo.

echo [方案2] 禁用调试器，直接运行
echo --------------------------------
echo 在 PyCharm 中点击运行按钮（绿色三角形）而不是调试按钮
echo 或者使用 Ctrl+Shift+F10 (运行) 而不是 Shift+F9 (调试)
echo.

echo [方案3] 使用命令行启动，在 PyCharm 中附加调试器
echo --------------------------------
echo 1. 在命令行中运行:
echo    cd C:\dev\agi-ev\ai-sns-el
echo    venv\Scripts\python.exe api_server.py
echo 2. 在 PyCharm 中:
echo    - Run ^> Attach to Process
echo    - 选择 python.exe 进程
echo.

echo [方案4] 创建专用的启动脚本
echo --------------------------------
echo 创建 api_server_debug.bat:
echo.
echo   @echo off
echo   set PYTHONPATH=C:\dev\agi-ev\ai-sns-el
echo   cd C:\dev\agi-ev\ai-sns-el
echo   venv\Scripts\python.exe api_server.py
echo.
echo 然后在 PyCharm 中配置运行这个 .bat 文件
echo.

echo [快速验证]
echo --------------------------------
echo 在 PyCharm 中运行以下代码查看环境:
echo.
echo   import sys; print('Working dir:', __import__('os').getcwd())
echo   import os; os.chdir(r'C:\dev\agi-ev\ai-sns-el'); sys.path.insert(0, r'C:\dev\agi-ev\ai-sns-el')
echo   from backend.modules.km.router import router; print('KM routes:', len(router.routes))
echo.

echo ==========================================
echo 建议优先尝试方案1
echo ==========================================
pause
