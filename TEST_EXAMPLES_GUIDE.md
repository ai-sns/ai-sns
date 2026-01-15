# 4个模块真实执行测试指南
# Real Execution Test Guide for 4 Modules

## 我为您准备的测试例子

### 方法1: 独立演示脚本（推荐）✓

**脚本**: `demo_real_execution_standalone.py`

**特点**:
- ✓ 不依赖数据库，避免锁定问题
- ✓ 直接调用executor演示真实执行
- ✓ 包含所有4个模块的完整例子
- ✓ 自动创建和清理临时文件

**运行方法**:
```bash
cd /root/sharedata3/ai-sns-el
python3 demo_real_execution_standalone.py
```

**包含的测试例子**:

#### 1. Plugin模块 - Python代码执行
- 执行runtime_main中的Python代码
- 演示：计算器功能（加减乘除）
- 证明：真实subprocess执行，捕获print输出

#### 2. Function模块 - Python文件执行
- 执行真实的Python文件
- 演示：问候函数，接收JSON参数
- 证明：真实文件系统访问，stdin参数传递

#### 3. Skill模块 - 系统自动化
两个例子：
- **截图Skill**: 尝试调用pyautogui截图
  - 证明：真实尝试import pyautogui
- **系统检查Skill**: 执行Python脚本检查系统
  - 证明：真实获取系统信息、进程ID、文件列表

#### 4. MCP模块 - 服务器测试
- 启动真实的MCP服务器进程
- 测试进程存活状态
- 证明：真实进程管理，自动启停

---

### 方法2: 通过API创建和测试

**脚本**: `test_4_modules_real_examples.py`

**特点**:
- 通过API创建真实的测试工具
- 保存到数据库，可以在前端看到
- 可以通过前端点击"测试"按钮执行

**注意**:
- 可能遇到SQLite数据库锁定问题
- 建议先停止其他访问数据库的程序

**运行方法**:
```bash
cd /root/sharedata3/ai-sns-el
python3 test_4_modules_real_examples.py
```

---

### 方法3: 前端界面测试

**步骤**:

1. 打开前端Tools页面
2. 选择任意模块（Plugin/MCP/Function/Skill）
3. 点击工具卡片上的"测试"按钮
4. 查看真实执行结果

**现有工具测试**:
```bash
# 测试现有的所有工具
python3 test_tools_execute.py
```

**特点**:
- 测试数据库中现有的工具
- 会看到真实的错误信息（文件不存在等）
- 证明不是mock返回

---

## 查看执行日志

所有执行都会记录详细日志：

```bash
# 实时查看执行日志
tail -f /tmp/api_server.log | grep tool_executor

# 查看最近的执行日志
tail -100 /tmp/api_server.log | grep tool_executor
```

**日志示例**:
```
INFO:backend.modules.tools.tool_executor:[plugin] DEMO_PLUGIN_001: started - Plugin execution started
INFO:backend.modules.tools.tool_executor:[plugin] DEMO_PLUGIN_001: executing - Executing runtime_main code
INFO:backend.modules.tools.tool_executor:[plugin] DEMO_PLUGIN_001: completed - Plugin executed successfully
INFO:backend.modules.tools.tool_executor:[function] DEMO_FUNCTION_001: started - Function execution started
INFO:backend.modules.tools.tool_executor:[function] DEMO_FUNCTION_001: executing - Executing file: /tmp/xxx.py
INFO:backend.modules.tools.tool_executor:[function] DEMO_FUNCTION_001: completed - Function executed successfully
```

---

## 真实执行的证据

### 对比Mock vs Real

**Mock执行（旧）**:
```json
{
  "status": "success",
  "message": "Plugin executed successfully",
  "output": {"test_result": "OK"}  // 假数据，总是成功
}
```

**Real执行（新）**:
```json
{
  "status": "success",
  "output": {
    "stdout": "真实的计算结果: 100 + 25 = 125\n真实的print输出!",
    "success": true
  }
}
```

或者真实的错误：
```json
{
  "status": "error",
  "message": "Plugin file not found: /path/to/file.py",
  "error": "FileNotFoundError",
  "traceback": "真实的Python堆栈跟踪..."
}
```

---

## 测试结果说明

### 1. Plugin测试 ✓
**看到什么**:
```
输入 / Input: a=100, b=25
计算结果 / Results:
  加法 / Sum: 100 + 25 = 125
  减法 / Difference: 100 - 25 = 75
  乘法 / Product: 100 × 25 = 2500
  除法 / Quotient: 100 ÷ 25 = 4.0
✓ Plugin执行成功!
```

**证明**: 真实的Python代码被subprocess执行，print输出被捕获

### 2. Function测试 ✓
**看到什么**:
```
参数 / Parameter: name = 'Real Execution Test'
问候 / Greetings:
  [1] Hello, Real Execution Test!
  [2] Hello, Real Execution Test!
  [3] Hello, Real Execution Test!
系统信息 / System Info:
  OS: Linux
  Python: 3.10.12
```

**证明**:
- 真实的Python文件被执行
- stdin参数被正确传递
- 真实的系统信息被获取

### 3. Skill测试（截图）✓
**看到什么**:
```
Action: {
  'performed': 'screenshot_capture',
  'status': 'library_missing',
  'message': 'pyautogui not installed. Run: pip install pyautogui pillow'
}
```

**证明**:
- 系统真实尝试import pyautogui
- 不是mock返回，而是真实的ImportError
- 如果安装pyautogui，会真实截图

### 4. Skill测试（系统检查）✓
**看到什么**:
```
系统信息:
  操作系统: Linux
  平台: Linux-5.15.0-164-generic
  Python版本: 3.10.12
  进程ID: 30114
文件系统:
  当前目录: /root/sharedata3/ai-sns-el
  文件总数: 302
```

**证明**:
- 真实获取系统信息
- 真实访问文件系统
- 真实的进程ID

### 5. MCP测试 ✓
**看到什么**:
```
Connection: {
  'status': 'started_and_stopped',
  'message': 'MCP server started successfully and was stopped',
  'test_duration_ms': 500
}
```

**证明**:
- 真实启动MCP服务器进程
- 检查进程存活状态
- 自动停止进程

---

## 您可以自己修改的例子

### 修改Plugin代码
编辑 `demo_real_execution_standalone.py`，找到：
```python
plugin_data = {
    "runtime_main": """
# 在这里写您自己的Python代码
print("Hello from my custom code!")
import math
print(f"Pi = {math.pi}")
"""
}
```

### 修改Function文件
找到 `function_code` 变量：
```python
function_code = """#!/usr/bin/env python3
# 在这里写您的函数代码
import sys
print("My custom function!")
"""
```

### 修改Skill脚本
找到 `skill_script` 变量，添加您的逻辑

---

## 常见问题

### Q: 如何安装pyautogui测试截图？
```bash
pip install pyautogui pillow
```
然后重新运行测试，会真实截图。

### Q: 如何测试JavaScript执行？
需要安装Node.js：
```bash
apt-get install nodejs npm
```

### Q: 数据库锁定怎么办？
使用独立演示脚本（方法1），不依赖数据库。

### Q: 如何查看完整的执行日志？
```bash
tail -f /tmp/api_server.log | grep tool_executor
```

---

## 总结

您现在有**3种方式**测试真实执行：

1. **独立演示** ✓ 推荐
   ```bash
   python3 demo_real_execution_standalone.py
   ```

2. **API创建测试**
   ```bash
   python3 test_4_modules_real_examples.py
   ```

3. **前端界面测试**
   - 打开Tools页面
   - 点击"测试"按钮

**所有测试都是真实执行，不是mock！**

查看文件：
- 独立演示: `demo_real_execution_standalone.py`
- API测试: `test_4_modules_real_examples.py`
- 批量测试: `test_tools_execute.py`
- 详细报告: `REAL_EXECUTION_IMPLEMENTATION_REPORT.md`
- 快速摘要: `REAL_EXECUTION_QUICK_SUMMARY.md`
