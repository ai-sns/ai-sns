#!/bin/bash
# 直接使用sqlite3命令添加真实执行例子

DB_PATH="/tmp/test_tools.db"
TEST_DIR="/root/sharedata3/ai-sns-el/test_examples"

mkdir -p "$TEST_DIR"

echo "======================================================================"
echo "使用sqlite3命令添加真实执行例子"
echo "数据库: $DB_PATH"
echo "======================================================================"

# 生成ID函数
generate_id() {
    prefix=$1
    timestamp=$(date +"%Y%m%d%H%M%S")
    random=$((RANDOM % 100000))
    echo "${prefix}${timestamp}${random}"
}

# 1. 添加Plugin
echo ""
echo "1. 添加 Plugin 例子 - 真实计算器"
PLUGIN_ID=$(generate_id "PL")
sqlite3 "$DB_PATH" "INSERT INTO pluginmng (plugin_id, name, description, instruction, plugin_type, runtime_main, confirm_needed, is_delete) VALUES ('$PLUGIN_ID', '✓ Real Calculator Plugin', '真实的计算器插件', '执行加减乘除计算', 'Tool_Code', 'import sys
print(\"=\" * 50)
print(\"真实Plugin执行\")
print(\"=\" * 50)
a = 100
b = 25
print(f\"\\n计算: {a} + {b} = {a + b}\")
print(f\"计算: {a} - {b} = {a - b}\")
print(f\"计算: {a} × {b} = {a * b}\")
print(f\"计算: {a} ÷ {b} = {a / b}\")
print(\"\\n✓ Plugin执行成功!\")
', 0, 0);"

if [ $? -eq 0 ]; then
    echo "✓ Plugin创建成功! ID: $PLUGIN_ID"
else
    echo "✗ Plugin创建失败"
    exit 1
fi

# 2. 添加Function
echo ""
echo "2. 添加 Function 例子 - 真实问候函数"
FUNCTION_FILE="$TEST_DIR/greeting_function.py"
cat > "$FUNCTION_FILE" << 'PYEOF'
#!/usr/bin/env python3
import sys, json, platform
print("=" * 50)
print("真实Function执行")
print("=" * 50)
try:
    params = json.loads(sys.stdin.read()) if sys.stdin.read() else {}
    name = params.get('name', 'World')
    count = params.get('count', 3)
except:
    name, count = 'World', 3
print(f"\n参数: name={name}, count={count}")
for i in range(count):
    print(f"  [{i+1}] Hello, {name}!")
print(f"\n系统: {platform.system()} Python {platform.python_version()}")
print("✓ Function执行成功!")
PYEOF
chmod +x "$FUNCTION_FILE"

FUNCTION_ID=$(generate_id "FN")
sqlite3 "$DB_PATH" "INSERT INTO function_mng (function_id, name, description, instruction, function_type, file_path, parameter, confirm_needed, is_delete) VALUES ('$FUNCTION_ID', '✓ Real Greeting Function', '真实的问候函数', '执行真实Python文件', 'python', '$FUNCTION_FILE', '{\"name\":{\"type\":\"string\"},\"count\":{\"type\":\"number\"}}', 0, 0);"

if [ $? -eq 0 ]; then
    echo "✓ Function创建成功! ID: $FUNCTION_ID"
    echo "  文件: $FUNCTION_FILE"
else
    echo "✗ Function创建失败"
fi

# 3. 添加Skill截图
echo ""
echo "3. 添加 Skill 例子1 - 真实截图"
SKILL1_ID=$(generate_id "SK")
sqlite3 "$DB_PATH" "INSERT INTO skill_mng (skill_id, name, description, instruction, skill_type, parameter, confirm_needed, is_delete) VALUES ('$SKILL1_ID', '✓ Real Screenshot Skill', '真实的截图技能', '尝试真实截图', 'screenshot', '{\"region\":\"full\",\"format\":\"png\"}', 0, 0);"

if [ $? -eq 0 ]; then
    echo "✓ Skill创建成功! ID: $SKILL1_ID"
else
    echo "✗ Skill创建失败"
fi

# 4. 添加Skill系统检查
echo ""
echo "4. 添加 Skill 例子2 - 真实系统检查"
SKILL_FILE="$TEST_DIR/system_check_skill.py"
cat > "$SKILL_FILE" << 'PYEOF'
#!/usr/bin/env python3
import platform, os
print("=" * 50)
print("真实Skill脚本执行")
print("=" * 50)
print(f"\n系统: {platform.system()} {platform.platform()}")
print(f"Python: {platform.python_version()}")
print(f"进程ID: {os.getpid()}")
print(f"当前目录: {os.getcwd()}")
print(f"文件数: {len(os.listdir('.'))}")
print("\n✓ Skill执行成功!")
PYEOF
chmod +x "$SKILL_FILE"

SKILL2_ID=$(generate_id "SK")
sqlite3 "$DB_PATH" "INSERT INTO skill_mng (skill_id, name, description, instruction, skill_type, file_path, parameter, confirm_needed, is_delete) VALUES ('$SKILL2_ID', '✓ Real System Check Skill', '真实的系统检查', '获取真实系统信息', 'custom', '$SKILL_FILE', '{}', 0, 0);"

if [ $? -eq 0 ]; then
    echo "✓ Skill创建成功! ID: $SKILL2_ID"
    echo "  文件: $SKILL_FILE"
else
    echo "✗ Skill创建失败"
fi

# 5. 添加MCP
echo ""
echo "5. 添加 MCP 例子 - 真实测试服务器"
MCP_FILE="$TEST_DIR/test_mcp_server.py"
cat > "$MCP_FILE" << 'PYEOF'
#!/usr/bin/env python3
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
PYEOF
chmod +x "$MCP_FILE"

MCP_ID=$(generate_id "MC")
sqlite3 "$DB_PATH" "INSERT INTO mcp_mng (mcp_id, name, description, instruction, mcp_type, file_path, parameter, requirement, confirm_needed, is_delete) VALUES ('$MCP_ID', '✓ Real Test MCP Server', '真实的MCP测试服务器', '启动并测试MCP服务器', 'stdio', '$MCP_FILE', '{}', 'python>=3.7', 0, 0);"

if [ $? -eq 0 ]; then
    echo "✓ MCP创建成功! ID: $MCP_ID"
    echo "  文件: $MCP_FILE"
else
    echo "✗ MCP创建失败"
fi

echo ""
echo "======================================================================"
echo "✓ 所有例子添加成功！"
echo "======================================================================"
echo ""
echo "数据库: $DB_PATH"
echo ""
echo "已添加5个真实执行例子："
echo "1. Plugin: $PLUGIN_ID - 真实计算器"
echo "2. Function: $FUNCTION_ID - 真实问候函数"
echo "3. Skill: $SKILL1_ID - 真实截图"
echo "4. Skill: $SKILL2_ID - 真实系统检查"
echo "5. MCP: $MCP_ID - 真实测试服务器"
echo ""
echo "下一步："
echo "1. 备份并替换数据库："
echo "   mv db/db.sqlite db/db.sqlite.backup"
echo "   cp db/test_examples.db db/db.sqlite"
echo ""
echo "2. 重启API服务器："
echo "   ps aux | grep api_server.py | grep -v grep | awk '{print \$2}' | xargs kill"
echo "   nohup python3 api_server.py > /tmp/api_server.log 2>&1 &"
echo ""
echo "3. 刷新前端，查看新例子（名称以✓开头）"
echo ""
echo "======================================================================"
