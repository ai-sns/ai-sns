#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用直接SQL添加真实执行例子到数据库副本
"""

import sqlite3
import os
import json
from datetime import datetime
import uuid

# 数据库路径
DB_PATH = "/root/sharedata3/ai-sns-el/db/test_examples.db"

# 创建测试文件目录
TEST_FILES_DIR = "/root/sharedata3/ai-sns-el/test_examples"
os.makedirs(TEST_FILES_DIR, exist_ok=True)

def generate_id(prefix):
    """生成ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = str(uuid.uuid4().int)[:5]
    return f"{prefix}{timestamp}{random_part}"

print("=" * 70)
print("使用直接SQL添加真实执行例子")
print(f"数据库: {DB_PATH}")
print("=" * 70)

# 连接数据库，设置超时
conn = sqlite3.connect(DB_PATH, timeout=30.0)
cursor = conn.cursor()

try:
    # 1. Plugin 例子
    print("\n1. 添加 Plugin 例子 - 真实计算器")
    plugin_id = generate_id("PL")
    cursor.execute("""
        INSERT INTO pluginmng (
            plugin_id, name, description, instruction, plugin_type,
            runtime_main, confirm_needed, is_delete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plugin_id,
        "✓ Real Calculator Plugin",
        "真实的计算器插件 - 演示Python代码执行。点击测试按钮查看真实的subprocess执行结果！",
        "执行加减乘除计算，展示真实的Python代码执行，不是mock！",
        "Tool_Code",
        """import sys

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
""",
        0,  # confirm_needed
        0   # is_delete
    ))
    conn.commit()
    print(f"✓ Plugin创建成功! ID: {plugin_id}")

    # 2. Function 例子
    print("\n2. 添加 Function 例子 - 真实问候函数")
    function_file = os.path.join(TEST_FILES_DIR, "greeting_function.py")
    with open(function_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import platform

print("=" * 50)
print("真实Function执行 / Real Function Execution")
print("=" * 50)

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

print(f"\\n参数: name={name}, count={count}")
print(f"\\n问候:")
for i in range(count):
    print(f"  [{i+1}] Hello, {name}!")

print(f"\\n系统: {platform.system()} Python {platform.python_version()}")
print(f"✓ Function执行成功!")
""")
    os.chmod(function_file, 0o755)

    function_id = generate_id("FN")
    cursor.execute("""
        INSERT INTO function_mng (
            function_id, name, description, instruction, function_type,
            file_path, parameter, confirm_needed, is_delete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        function_id,
        "✓ Real Greeting Function",
        "真实的问候函数 - 演示Python文件执行！",
        "点击测试按钮，执行真实的Python文件",
        "python",
        function_file,
        json.dumps({"name": {"type": "string"}, "count": {"type": "number"}}),
        0, 0
    ))
    conn.commit()
    print(f"✓ Function创建成功! ID: {function_id}")
    print(f"  文件: {function_file}")

    # 3. Skill 例子1 - 截图
    print("\n3. 添加 Skill 例子1 - 真实截图")
    skill_screenshot_id = generate_id("SK")
    cursor.execute("""
        INSERT INTO skill_mng (
            skill_id, name, description, instruction, skill_type,
            parameter, confirm_needed, is_delete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        skill_screenshot_id,
        "✓ Real Screenshot Skill",
        "真实的截图技能 - 尝试真实的pyautogui调用！",
        "点击测试按钮，真实尝试截图",
        "screenshot",
        json.dumps({"region": "full", "format": "png"}),
        0, 0
    ))
    conn.commit()
    print(f"✓ Skill创建成功! ID: {skill_screenshot_id}")

    # 4. Skill 例子2 - 系统检查
    print("\n4. 添加 Skill 例子2 - 真实系统检查")
    skill_file = os.path.join(TEST_FILES_DIR, "system_check_skill.py")
    with open(skill_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import platform, os

print("=" * 50)
print("真实Skill脚本执行")
print("=" * 50)
print(f"\\n系统: {platform.system()} {platform.platform()}")
print(f"Python: {platform.python_version()}")
print(f"进程ID: {os.getpid()}")
print(f"当前目录: {os.getcwd()}")
print(f"文件数: {len(os.listdir('.'))}")
print("\\n✓ Skill执行成功!")
""")
    os.chmod(skill_file, 0o755)

    skill_custom_id = generate_id("SK")
    cursor.execute("""
        INSERT INTO skill_mng (
            skill_id, name, description, instruction, skill_type,
            file_path, parameter, confirm_needed, is_delete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        skill_custom_id,
        "✓ Real System Check Skill",
        "真实的系统检查 - 执行真实Python脚本！",
        "点击测试按钮，获取真实系统信息",
        "custom",
        skill_file,
        json.dumps({}),
        0, 0
    ))
    conn.commit()
    print(f"✓ Skill创建成功! ID: {skill_custom_id}")
    print(f"  文件: {skill_file}")

    # 5. MCP 例子
    print("\n5. 添加 MCP 例子 - 真实测试服务器")
    mcp_file = os.path.join(TEST_FILES_DIR, "test_mcp_server.py")
    with open(mcp_file, 'w') as f:
        f.write("""#!/usr/bin/env python3
import sys, time, json

print("MCP Server Starting...", file=sys.stderr)
time.sleep(0.2)
print("MCP Server Ready!", file=sys.stderr)
print(json.dumps({"status": "running", "type": "stdio"}))
sys.stdout.flush()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped", file=sys.stderr)
""")
    os.chmod(mcp_file, 0o755)

    mcp_id = generate_id("MC")
    cursor.execute("""
        INSERT INTO mcp_mng (
            mcp_id, name, description, instruction, mcp_type,
            file_path, parameter, requirement, confirm_needed, is_delete
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mcp_id,
        "✓ Real Test MCP Server",
        "真实的MCP测试服务器 - 启动真实进程！",
        "点击测试按钮，启动并测试MCP服务器",
        "stdio",
        mcp_file,
        json.dumps({}),
        "python>=3.7",
        0, 0
    ))
    conn.commit()
    print(f"✓ MCP创建成功! ID: {mcp_id}")
    print(f"  文件: {mcp_file}")

    print("\n" + "=" * 70)
    print("✓ 所有例子添加成功！")
    print("=" * 70)

    print(f"""
数据库: {DB_PATH}

已添加5个真实执行例子：
1. Plugin: {plugin_id} - 真实计算器
2. Function: {function_id} - 真实问候函数 ({function_file})
3. Skill: {skill_screenshot_id} - 真实截图
4. Skill: {skill_custom_id} - 真实系统检查 ({skill_file})
5. MCP: {mcp_id} - 真实测试服务器 ({mcp_file})

下一步：
1. 替换数据库：
   mv db/db.sqlite db/db.sqlite.backup
   mv db/db_with_examples.sqlite db/db.sqlite

2. 重启API服务器：
   nohup python3 api_server.py > /tmp/api_server.log 2>&1 &

3. 刷新前端，在Tools的4个模块中查看新例子（名称以✓开头）

4. 点击"测试"按钮，查看真实执行结果！
""")

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()

print("=" * 70)
