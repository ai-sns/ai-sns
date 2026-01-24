# PyCharm 调试 404 问题修复指南

## 问题描述
- **PyCharm 调试模式运行：** `http://localhost:8788/api/km` 返回 404
- **命令行直接运行：** 正常工作

## 根本原因
PyCharm 调试器（`pydevd.py`）在多进程或某些特定情况下，可能会影响模块的导入时机或 sys.path 的设置，导致 KM 模块未正确加载。

## 解决方案

### 方案 1：在运行配置中设置 PYTHONPATH（推荐）

1. 在 PyCharm 中打开 `Run` → `Edit Configurations...`
2. 选择 `api_server` 配置
3. 找到 `Environment variables` 字段
4. 点击文件夹图标或输入以下内容：
   ```
   PYTHONPATH=C:\dev\agi-ev\ai-sns-el;C:\dev\agi-ev\ai-sns-el\backend
   ```
5. 保存配置并重新运行

### 方案 2：使用修复版启动脚本

在 PyCharm 中运行 `api_server_with_path_fix.py` 而不是 `api_server.py`

这个脚本会：
- 强制设置正确的工作目录
- 确保在导入模块前设置好 sys.path
- 在启动前测试关键模块导入

### 方案 3：修改 api_server.py（临时方案）

在 `api_server.py` 的最前面添加：

```python
import sys
import os
from pathlib import Path

# 确保工作目录正确
project_dir = Path(__file__).resolve().parent
os.chdir(project_dir)

# 确保 backend 在 sys.path 中
backend_dir = project_dir / 'backend'
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
```

### 方案 4：使用"运行"而不是"调试"

- 点击绿色三角形（Run）而不是虫子图标（Debug）
- 快捷键：`Ctrl+Shift+F10` 而不是 `Shift+F9`

### 方案 5：禁用多进程调试

1. 打开 `Run` → `Edit Configurations...`
2. 选择 `api_server` 配置
3. 找到 `PyDev debugger` 相关设置
4. 禁用 `--multiprocess` 选项（如果有的话）

## 快速验证

在 PyCharm 的 Python 控制台中运行：

```python
import os, sys
from pathlib import Path

# 检查环境
print("Working dir:", os.getcwd())
print("Python:", sys.executable)

# 设置环境
project_dir = Path(os.getcwd()).resolve()
backend_dir = project_dir / 'backend'
sys.path.insert(0, str(backend_dir))
os.chdir(str(project_dir))

# 测试导入
from backend.modules.km.router import router as km_router
print("KM routes:", len(km_router.routes))
```

## 推荐方案

**方案 1（设置 PYTHONPATH）** 是最干净、最推荐的解决方案，因为它：
- 不需要修改代码
- 对所有运行模式（调试、运行）都有效
- 符合 PyCharm 的最佳实践

## 注意事项

- 修改配置后，需要停止当前运行的服务器并重新启动
- 如果问题持续，请检查 PyCharm 的 Python 解释器配置是否指向虚拟环境
