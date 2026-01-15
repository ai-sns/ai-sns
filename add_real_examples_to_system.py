#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将真实执行例子添加到系统数据库
Add Real Execution Examples to System Database

这个脚本会创建4个模块的真实测试例子，并添加到数据库
您可以在前端界面上看到这些例子，点击"测试"按钮执行
"""

import requests
import json
import os
import time

API_BASE_URL = "http://127.0.0.1:8788/api/tools"

# 创建测试文件目录
TEST_FILES_DIR = "/root/sharedata3/ai-sns-el/test_examples"
os.makedirs(TEST_FILES_DIR, exist_ok=True)

def wait_and_retry(func, max_retries=3, delay=3):
    """重试机制避免数据库锁定"""
    for i in range(max_retries):
        try:
            result = func()
            if result.status_code == 200:
                return result
            elif result.status_code == 500 and "database is locked" in result.text:
                if i < max_retries - 1:
                    print(f"  数据库锁定，{delay}秒后重试... ({i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    return result
            else:
                return result
        except Exception as e:
            if i < max_retries - 1:
                print(f"  错误: {str(e)[:100]}, {delay}秒后重试...")
                time.sleep(delay)
            else:
                print(f"  最终失败: {str(e)[:100]}")
                return None
    return None

print("=" * 70)
print("将真实执行例子添加到系统")
print("Adding Real Execution Examples to System")
print("=" * 70)

# =============================================================================
# 1. Plugin 例子 - 真实计算器
# =============================================================================
print("\n1. 添加 Plugin 例子 - 真实计算器")
print("-" * 70)

plugin_data = {
    "name": "✓ Real Calculator Plugin",
    "description": "真实的计算器插件 - 演示Python代码执行。点击测试按钮查看真实的subprocess执行结果！",
    "instruction": "执行加减乘除计算，展示真实的Python代码执行，不是mock！",
    "plugin_type": "Tool_Code",
    "runtime_main": """import sys

print("=" * 50)
print("真实Plugin执行 / Real Plugin Execution")
print("=" * 50)

# 真实的计算
a = 100
b = 25

print(f"\\n输入 / Input: a={a}, b={b}")
print(f"\\n计算结果 / Results:")
print(f"  加法 / Sum: {a} + {b} = {a + b}")
print(f"  减法 / Difference: {a} - {b} = {a - b}")
print(f"  乘法 / Product: {a} × {b} = {a * b}")
print(f"  除法 / Quotient: {a} ÷ {b} = {a / b}")

print(f"\\n✓ Plugin执行成功!")
print(f"✓ 这是真实的subprocess执行，不是mock!")
print(f"✓ 查看日志: tail -f /tmp/api_server.log | grep tool_executor")
""",
    "confirm_needed": False
}

response = wait_and_retry(lambda: requests.post(f"{API_BASE_URL}/plugins", json=plugin_data, timeout=30))
if response and response.status_code == 200:
    result = response.json()
    print(f"✓ Plugin创建成功!")
    print(f"  ID: {result.get('plugin_id')}")
    print(f"  名称: {result.get('name')}")
    print(f"  类型: runtime_main Python代码执行")
else:
    print(f"✗ Plugin创建失败: {response.status_code if response else 'No response'}")

time.sleep(1)

# =============================================================================
# 2. Function 例子 - 真实问候函数
# =============================================================================
print("\n2. 添加 Function 例子 - 真实问候函数")
print("-" * 70)

# 创建Function文件
function_file = os.path.join(TEST_FILES_DIR, "greeting_function.py")
function_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import platform

print("=" * 50)
print("真实Function执行 / Real Function Execution")
print("=" * 50)

# 读取stdin参数
try:
    input_data = sys.stdin.read()
    if input_data:
        params = json.loads(input_data)
        name = params.get('name', 'World')
        count = params.get('count', 3)
    else:
        name = 'World'
        count = 3
except:
    name = 'World'
    count = 3

print(f"\\n参数 / Parameters:")
print(f"  name: {name}")
print(f"  count: {count}")

print(f"\\n问候 / Greetings:")
for i in range(count):
    print(f"  [{i+1}] Hello, {name}!")
    print(f"  [{i+1}] 你好, {name}!")

print(f"\\n系统信息 / System Info:")
print(f"  OS: {platform.system()}")
print(f"  Python: {platform.python_version()}")

print(f"\\n✓ Function执行成功!")
print(f"✓ 这是真实的文件执行，不是mock!")
print(f"✓ 文件路径: {__file__}")
"""

with open(function_file, 'w') as f:
    f.write(function_code)
os.chmod(function_file, 0o755)

function_data = {
    "name": "✓ Real Greeting Function",
    "description": "真实的问候函数 - 演示Python文件执行。传入name和count参数，输出问候语和系统信息！",
    "instruction": "点击测试按钮，会执行真实的Python文件。参数: name(姓名), count(次数)",
    "function_type": "python",
    "file_path": function_file,
    "parameter": json.dumps({
        "name": {"type": "string", "description": "要问候的名字"},
        "count": {"type": "number", "description": "问候次数"}
    }),
    "confirm_needed": False
}

response = wait_and_retry(lambda: requests.post(f"{API_BASE_URL}/functions", json=function_data, timeout=30))
if response and response.status_code == 200:
    result = response.json()
    print(f"✓ Function创建成功!")
    print(f"  ID: {result.get('function_id')}")
    print(f"  名称: {result.get('name')}")
    print(f"  文件: {function_file}")
else:
    print(f"✗ Function创建失败: {response.status_code if response else 'No response'}")

time.sleep(1)

# =============================================================================
# 3. Skill 例子1 - 真实截图
# =============================================================================
print("\n3. 添加 Skill 例子1 - 真实截图")
print("-" * 70)

skill_screenshot_data = {
    "name": "✓ Real Screenshot Skill",
    "description": "真实的屏幕截图技能 - 演示系统自动化。会尝试真实的pyautogui调用进行截图！",
    "instruction": "点击测试按钮，会真实尝试截图。如果pyautogui已安装会真实截图，否则显示库缺失信息。",
    "skill_type": "screenshot",
    "parameter": json.dumps({
        "region": "full",
        "format": "png"
    }),
    "confirm_needed": False
}

response = wait_and_retry(lambda: requests.post(f"{API_BASE_URL}/skills", json=skill_screenshot_data, timeout=30))
if response and response.status_code == 200:
    result = response.json()
    print(f"✓ Skill创建成功!")
    print(f"  ID: {result.get('skill_id')}")
    print(f"  名称: {result.get('name')}")
    print(f"  类型: screenshot (系统自动化)")
else:
    print(f"✗ Skill创建失败: {response.status_code if response else 'No response'}")

time.sleep(1)

# =============================================================================
# 4. Skill 例子2 - 真实系统检查
# =============================================================================
print("\n4. 添加 Skill 例子2 - 真实系统检查")
print("-" * 70)

# 创建Skill文件
skill_file = os.path.join(TEST_FILES_DIR, "system_check_skill.py")
skill_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import platform
import os

print("=" * 50)
print("真实Skill脚本执行 / Real Skill Script Execution")
print("=" * 50)

print(f"\\n系统信息 / System Information:")
print(f"  操作系统: {platform.system()}")
print(f"  平台: {platform.platform()}")
print(f"  Python版本: {platform.python_version()}")
print(f"  进程ID: {os.getpid()}")

print(f"\\n文件系统 / Filesystem:")
cwd = os.getcwd()
print(f"  当前目录: {cwd}")
files = os.listdir(cwd)
print(f"  文件总数: {len(files)}")
print(f"  前10个文件:")
for f in files[:10]:
    print(f"    - {f}")

print(f"\\n环境变量 / Environment:")
print(f"  HOME: {os.environ.get('HOME', 'N/A')}")
print(f"  USER: {os.environ.get('USER', 'N/A')}")
print(f"  PATH前100字符: {os.environ.get('PATH', 'N/A')[:100]}")

print(f"\\n✓ Skill脚本执行成功!")
print(f"✓ 这是真实的系统交互，不是mock!")
print(f"✓ 文件路径: {__file__}")
"""

with open(skill_file, 'w') as f:
    f.write(skill_code)
os.chmod(skill_file, 0o755)

skill_custom_data = {
    "name": "✓ Real System Check Skill",
    "description": "真实的系统检查技能 - 演示自定义Python脚本执行。获取真实的系统信息、进程ID、文件列表！",
    "instruction": "点击测试按钮，会执行真实的Python脚本，获取系统信息、文件列表、环境变量等。",
    "skill_type": "custom",
    "file_path": skill_file,
    "parameter": json.dumps({}),
    "confirm_needed": False
}

response = wait_and_retry(lambda: requests.post(f"{API_BASE_URL}/skills", json=skill_custom_data, timeout=30))
if response and response.status_code == 200:
    result = response.json()
    print(f"✓ Skill创建成功!")
    print(f"  ID: {result.get('skill_id')}")
    print(f"  名称: {result.get('name')}")
    print(f"  文件: {skill_file}")
else:
    print(f"✗ Skill创建失败: {response.status_code if response else 'No response'}")

time.sleep(1)

# =============================================================================
# 5. MCP 例子 - 真实测试服务器
# =============================================================================
print("\n5. 添加 MCP 例子 - 真实测试服务器")
print("-" * 70)

# 创建MCP服务器文件
mcp_file = os.path.join(TEST_FILES_DIR, "test_mcp_server.py")
mcp_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import json

# 简单的MCP测试服务器
print("=" * 50, file=sys.stderr)
print("真实MCP服务器启动 / Real MCP Server Starting", file=sys.stderr)
print("=" * 50, file=sys.stderr)

print("MCP Server initializing...", file=sys.stderr)
time.sleep(0.2)
print("MCP Server ready!", file=sys.stderr)
print("Server Type: stdio", file=sys.stderr)
print("Status: Running", file=sys.stderr)

# 输出服务器信息到stdout
server_info = {
    "status": "running",
    "type": "stdio",
    "message": "MCP test server is running"
}
print(json.dumps(server_info))
sys.stdout.flush()

# 保持运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("MCP Server stopped", file=sys.stderr)
"""

with open(mcp_file, 'w') as f:
    f.write(mcp_code)
os.chmod(mcp_file, 0o755)

mcp_data = {
    "name": "✓ Real Test MCP Server",
    "description": "真实的MCP测试服务器 - 演示MCP服务器启动测试。会真实启动进程并测试连接！",
    "instruction": "点击测试按钮，会真实启动MCP服务器进程，测试其存活状态，然后自动停止。",
    "mcp_type": "stdio",
    "file_path": mcp_file,
    "parameter": json.dumps({}),
    "requirement": "python>=3.7",
    "confirm_needed": False
}

response = wait_and_retry(lambda: requests.post(f"{API_BASE_URL}/mcp", json=mcp_data, timeout=30))
if response and response.status_code == 200:
    result = response.json()
    print(f"✓ MCP创建成功!")
    print(f"  ID: {result.get('mcp_id')}")
    print(f"  名称: {result.get('name')}")
    print(f"  文件: {mcp_file}")
else:
    print(f"✗ MCP创建失败: {response.status_code if response else 'No response'}")

# =============================================================================
# 总结
# =============================================================================
print("\n" + "=" * 70)
print("添加完成! / Addition Complete!")
print("=" * 70)

print("""
✓ 已添加4个模块的真实执行例子到系统数据库！

1. Plugin 模块 ✓
   名称: ✓ Real Calculator Plugin
   功能: Python代码执行（加减乘除计算）

2. Function 模块 ✓
   名称: ✓ Real Greeting Function
   功能: Python文件执行（问候函数）
   文件: {}/greeting_function.py

3. Skill 模块 ✓
   a) ✓ Real Screenshot Skill
      功能: 系统自动化（截图）
   b) ✓ Real System Check Skill
      功能: 自定义脚本（系统检查）
      文件: {}/system_check_skill.py

4. MCP 模块 ✓
   名称: ✓ Real Test MCP Server
   功能: 服务器启动测试
   文件: {}/test_mcp_server.py

现在您可以：
1. 刷新前端页面
2. 在Tools的4个模块中找到这些例子（名称以✓开头）
3. 点击卡片上的"测试"按钮
4. 查看真实执行结果！

查看执行日志：
  tail -f /tmp/api_server.log | grep tool_executor
""".format(TEST_FILES_DIR, TEST_FILES_DIR, TEST_FILES_DIR))

print("=" * 70)
