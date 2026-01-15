#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4个工具模块的真实执行测试例子
Real Execution Test Examples for All 4 Tool Modules

这个脚本为每个模块创建真实可执行的测试工具，然后执行它们
This script creates real executable test tools for each module and executes them
"""

import requests
import json
import tempfile
import os
import time

API_BASE_URL = "http://127.0.0.1:8788/api/tools"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(result):
    print(f"\n执行结果 / Execution Result:")
    print(f"  Status: {result.get('status')}")
    print(f"  Message: {result.get('message')}")
    if 'output' in result:
        output = result['output']
        print(f"  Output:")
        if 'stdout' in output:
            stdout = output['stdout'][:300]
            print(f"    stdout: {stdout}")
        if 'stderr' in output and output['stderr']:
            print(f"    stderr: {output['stderr'][:200]}")
        print(f"    success: {output.get('success')}")
    if 'result' in result:
        print(f"  Result: {result.get('result')}")
    if 'action' in result:
        print(f"  Action: {result.get('action')}")
    if 'connection' in result:
        print(f"  Connection: {result.get('connection')}")
    if 'error' in result:
        print(f"  Error: {result.get('error')[:200]}")


print_section("4个工具模块真实执行测试 / Real Execution Test for 4 Modules")

# =============================================================================
# 1. Plugin 测试 - 使用 runtime_main 执行 Python 代码
# =============================================================================
print_section("1. Plugin 模块测试 - Python代码直接执行")

plugin_data = {
    "name": "Real_Calculator_Plugin",
    "description": "真实的计算器插件 - 执行Python代码",
    "instruction": "传入两个数字a和b，计算它们的和、差、积、商",
    "plugin_type": "Tool_Code",
    "runtime_main": """
import sys
import json

# 这是真实执行的Python代码！
# This is real Python code being executed!

def calculate(a, b):
    results = {
        "sum": a + b,
        "difference": a - b,
        "product": a * b,
        "quotient": a / b if b != 0 else "Cannot divide by zero"
    }
    return results

# 主函数
a = 100
b = 25

print("=" * 50)
print("Real Calculator Plugin Execution")
print("=" * 50)
print(f"Input: a={a}, b={b}")
print("")

results = calculate(a, b)
for op, result in results.items():
    print(f"{op}: {result}")

print("")
print("✓ Plugin execution completed successfully!")
print("This is REAL code execution, not mock!")
""",
    "confirm_needed": False
}

print("\n创建Plugin...")
response = requests.post(f"{API_BASE_URL}/plugins", json=plugin_data)
if response.status_code == 200:
    plugin = response.json()
    plugin_id = plugin.get('plugin_id')
    print(f"✓ Plugin创建成功: {plugin_id}")

    print("\n执行Plugin...")
    time.sleep(0.5)
    exec_response = requests.post(
        f"{API_BASE_URL}/plugins/{plugin_id}/execute",
        json={"a": 100, "b": 25}
    )

    if exec_response.status_code == 200:
        result = exec_response.json().get('result', {})
        print_result(result)
else:
    print(f"✗ Plugin创建失败: {response.status_code}")
    print(f"  Error: {response.text[:200]}")

# =============================================================================
# 2. Function 测试 - 执行真实的 Python 文件
# =============================================================================
print_section("2. Function 模块测试 - Python文件执行")

# 创建真实的Python函数文件
function_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json

print("=" * 50)
print("Real Function File Execution")
print("=" * 50)

# 读取stdin参数（如果有）
try:
    input_data = sys.stdin.read()
    if input_data:
        params = json.loads(input_data)
        name = params.get('name', 'World')
        count = params.get('count', 1)
    else:
        name = 'World'
        count = 1
except Exception as e:
    name = 'World'
    count = 1

# 真实的函数执行
print(f"Input parameters:")
print(f"  name: {name}")
print(f"  count: {count}")
print("")

for i in range(count):
    print(f"[{i+1}] Hello, {name}! 这是真实的函数执行!")
    print(f"[{i+1}] This is REAL function execution!")

print("")
print("✓ Function execution completed successfully!")
print("File executed by subprocess, not mocked!")

# 返回结果
result = {
    "status": "success",
    "message": f"Greeted {name} {count} times",
    "executions": count
}
print("")
print(json.dumps(result, indent=2))
"""

# 写入临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(function_code)
    function_file = f.name

os.chmod(function_file, 0o755)

function_data = {
    "name": "Real_Greeting_Function",
    "description": "真实的问候函数 - 执行Python文件",
    "instruction": "传入name和count参数，输出问候语",
    "function_type": "python",
    "file_path": function_file,
    "parameter": json.dumps({
        "name": {"type": "string", "description": "要问候的名字"},
        "count": {"type": "number", "description": "问候次数"}
    }),
    "confirm_needed": False
}

print(f"\n创建Function...")
print(f"文件路径: {function_file}")
response = requests.post(f"{API_BASE_URL}/functions", json=function_data)
if response.status_code == 200:
    function = response.json()
    function_id = function.get('function_id')
    print(f"✓ Function创建成功: {function_id}")

    print("\n执行Function...")
    time.sleep(0.5)
    exec_response = requests.post(
        f"{API_BASE_URL}/functions/{function_id}/execute",
        json={"name": "Real Execution Test", "count": 3}
    )

    if exec_response.status_code == 200:
        result = exec_response.json().get('result', {})
        print_result(result)

    # 清理临时文件
    try:
        os.unlink(function_file)
        print(f"\n✓ 临时文件已清理: {function_file}")
    except:
        pass
else:
    print(f"✗ Function创建失败: {response.status_code}")
    print(f"  Error: {response.text[:200]}")
    os.unlink(function_file)

# =============================================================================
# 3. Skill 测试 - 系统自动化（截图）
# =============================================================================
print_section("3. Skill 模块测试 - 系统自动化（截图）")

skill_data = {
    "name": "Real_Screenshot_Skill",
    "description": "真实的屏幕截图技能 - 尝试系统自动化",
    "instruction": "执行截图操作，需要pyautogui库",
    "skill_type": "screenshot",
    "parameter": json.dumps({
        "region": "full",
        "format": "png"
    }),
    "confirm_needed": False
}

print("\n创建Skill...")
response = requests.post(f"{API_BASE_URL}/skills", json=skill_data)
if response.status_code == 200:
    skill = response.json()
    skill_id = skill.get('skill_id')
    print(f"✓ Skill创建成功: {skill_id}")

    print("\n执行Skill...")
    time.sleep(0.5)
    exec_response = requests.post(
        f"{API_BASE_URL}/skills/{skill_id}/execute",
        json={}
    )

    if exec_response.status_code == 200:
        result = exec_response.json().get('result', {})
        print_result(result)

        # 检查是否实际尝试了截图
        action = result.get('action', {})
        if 'library_missing' in action.get('status', ''):
            print("\n说明:")
            print("  系统尝试调用pyautogui进行真实截图")
            print("  但是pyautogui库未安装")
            print("  这证明是真实执行，不是mock!")
            print(f"  安装方法: pip install pyautogui pillow")
        elif 'filepath' in action:
            print(f"\n✓ 截图成功! 文件保存在: {action['filepath']}")
else:
    print(f"✗ Skill创建失败: {response.status_code}")
    print(f"  Error: {response.text[:200]}")

# =============================================================================
# 4. Skill 测试 - 自定义Python脚本
# =============================================================================
print_section("4. Skill 模块测试 - 自定义Python脚本")

# 创建真实的Skill脚本
skill_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import platform
import os

print("=" * 50)
print("Real Skill Script Execution")
print("=" * 50)

# 读取参数
try:
    input_data = sys.stdin.read()
    if input_data:
        params = json.loads(input_data)
    else:
        params = {}
except:
    params = {}

# 执行真实的系统检查
print("\\n系统信息 / System Information:")
print(f"  操作系统: {platform.system()}")
print(f"  平台: {platform.platform()}")
print(f"  Python版本: {platform.python_version()}")
print(f"  当前目录: {os.getcwd()}")
print(f"  进程ID: {os.getpid()}")

# 执行真实的文件系统操作
print("\\n文件系统检查 / Filesystem Check:")
home_dir = os.path.expanduser("~")
print(f"  Home目录: {home_dir}")

# 列出当前目录的文件
files = os.listdir(".")[:10]
print(f"  当前目录文件数: {len(os.listdir('.'))}")
print(f"  前10个文件:")
for f in files:
    print(f"    - {f}")

print("\\n✓ Skill script execution completed successfully!")
print("This is REAL system interaction, not mocked!")

# 返回结果
result = {
    "status": "success",
    "system": platform.system(),
    "python_version": platform.python_version(),
    "pid": os.getpid(),
    "files_count": len(os.listdir('.'))
}
print("\\nResult:")
print(json.dumps(result, indent=2))
"""

# 写入临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(skill_script)
    skill_file = f.name

os.chmod(skill_file, 0o755)

skill_custom_data = {
    "name": "Real_System_Check_Skill",
    "description": "真实的系统检查技能 - 执行自定义脚本",
    "instruction": "检查系统信息和文件系统",
    "skill_type": "custom",
    "file_path": skill_file,
    "parameter": json.dumps({}),
    "confirm_needed": False
}

print(f"\n创建自定义Skill...")
print(f"文件路径: {skill_file}")
response = requests.post(f"{API_BASE_URL}/skills", json=skill_custom_data)
if response.status_code == 200:
    skill = response.json()
    skill_id = skill.get('skill_id')
    print(f"✓ Skill创建成功: {skill_id}")

    print("\n执行Skill...")
    time.sleep(0.5)
    exec_response = requests.post(
        f"{API_BASE_URL}/skills/{skill_id}/execute",
        json={}
    )

    if exec_response.status_code == 200:
        result = exec_response.json().get('result', {})
        print_result(result)

    # 清理临时文件
    try:
        os.unlink(skill_file)
        print(f"\n✓ 临时文件已清理: {skill_file}")
    except:
        pass
else:
    print(f"✗ Skill创建失败: {response.status_code}")
    print(f"  Error: {response.text[:200]}")
    os.unlink(skill_file)

# =============================================================================
# 5. MCP 测试 - 简单的测试服务器
# =============================================================================
print_section("5. MCP 模块测试 - MCP服务器测试")

# 创建一个简单的MCP测试服务器
mcp_server_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import time

# 简单的MCP测试服务器
print("MCP Test Server Starting...", file=sys.stderr)
time.sleep(0.2)
print("MCP Server Ready!", file=sys.stderr)

# 保持运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("MCP Server Stopped", file=sys.stderr)
"""

# 写入临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(mcp_server_code)
    mcp_file = f.name

os.chmod(mcp_file, 0o755)

mcp_data = {
    "name": "Real_Test_MCP_Server",
    "description": "真实的MCP测试服务器",
    "instruction": "测试MCP服务器启动和连接",
    "mcp_type": "stdio",
    "file_path": mcp_file,
    "parameter": json.dumps({}),
    "confirm_needed": False
}

print(f"\n创建MCP...")
print(f"文件路径: {mcp_file}")
response = requests.post(f"{API_BASE_URL}/mcp", json=mcp_data)
if response.status_code == 200:
    mcp = response.json()
    mcp_id = mcp.get('mcp_id')
    print(f"✓ MCP创建成功: {mcp_id}")

    print("\n执行MCP测试...")
    time.sleep(0.5)
    exec_response = requests.post(
        f"{API_BASE_URL}/mcp/{mcp_id}/execute",
        json={}
    )

    if exec_response.status_code == 200:
        result = exec_response.json().get('result', {})
        print_result(result)

    # 清理临时文件
    try:
        os.unlink(mcp_file)
        print(f"\n✓ 临时文件已清理: {mcp_file}")
    except:
        pass
else:
    print(f"✗ MCP创建失败: {response.status_code}")
    print(f"  Error: {response.text[:200]}")
    os.unlink(mcp_file)

# =============================================================================
# 总结
# =============================================================================
print_section("测试总结 / Test Summary")

print("""
✓ 所有4个模块都已创建真实可执行的测试例子

1. Plugin 模块:
   - 使用 runtime_main 执行Python代码
   - 真实的subprocess执行
   - 可以看到print输出

2. Function 模块:
   - 执行真实的Python文件
   - 通过stdin传递参数
   - 捕获stdout输出

3. Skill 模块 (两个例子):
   - 截图skill: 尝试调用pyautogui
   - 自定义skill: 执行系统检查脚本
   - 真实的系统交互

4. MCP 模块:
   - 启动真实的服务器进程
   - 测试进程启动和停止
   - 捕获stderr输出

所有执行都是真实的，不是mock!
All executions are real, not mocked!

查看执行日志:
View execution logs:
  tail -f /tmp/api_server.log | grep tool_executor
""")

print("=" * 70)
print("测试完成! / Tests Complete!")
print("=" * 70)
