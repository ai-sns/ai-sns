#!/bin/bash
# Create test data using sqlite3 directly

DB_PATH="data/db.sqlite"

echo "Creating test scripts..."
mkdir -p /tmp/ai_sns_test_tools

# Plugin script
cat > /tmp/ai_sns_test_tools/test_plugin.py << 'SCRIPT_END'
#!/usr/bin/env python3
import sys, json
result = {"status": "success", "message": "Hello from Test Plugin!", "timestamp": str(__import__('datetime').datetime.now())}
print(json.dumps(result))
SCRIPT_END
chmod +x /tmp/ai_sns_test_tools/test_plugin.py

# Function script
cat > /tmp/ai_sns_test_tools/test_function.py << 'SCRIPT_END'
#!/usr/bin/env python3
import sys, json
result = {"function": "calculate_sum", "output": sum([1, 2, 3, 4, 5])}
print(json.dumps(result))
SCRIPT_END
chmod +x /tmp/ai_sns_test_tools/test_function.py

# MCP script
cat > /tmp/ai_sns_test_tools/test_mcp_server.py << 'SCRIPT_END'
#!/usr/bin/env python3
import sys, json
result = {"protocol_version": "1.0", "server_info": {"name": "Test MCP Server", "version": "1.0.0"}}
print(json.dumps(result))
SCRIPT_END
chmod +x /tmp/ai_sns_test_tools/test_mcp_server.py

# Skill script
cat > /tmp/ai_sns_test_tools/test_skill.py << 'SCRIPT_END'
#!/usr/bin/env python3
import sys, json
result = {"skill": "custom_test_skill", "result": "Skill executed successfully"}
print(json.dumps(result))
SCRIPT_END
chmod +x /tmp/ai_sns_test_tools/test_skill.py

echo "✓ Created test scripts"

echo "Inserting test data into database..."

# Generate UUIDs
PLUGIN1_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
PLUGIN2_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
MCP_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
FUNCTION_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
SKILL1_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
SKILL2_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
SKILL3_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")
SKILL4_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8].upper())")

# Insert plugins
sqlite3 "$DB_PATH" << SQL_END
-- Plugin 1: File execution
INSERT INTO pluginmng (plugin_id, name, description, instruction, plugin_type, filename, detail, confirm_needed, is_delete, create_time)
VALUES ('$PLUGIN1_ID', 'Test Plugin - File Execution', 'A test plugin that executes from file path', 'Use this plugin to test file-based execution. It accepts any parameters and returns a JSON response.', 'tool', '/tmp/ai_sns_test_tools/test_plugin.py', '{"test_mode": true}', 0, 0, datetime('now'));

-- Plugin 2: Inline code
INSERT INTO pluginmng (plugin_id, name, description, instruction, plugin_type, runtime_main, detail, confirm_needed, is_delete, create_time)
VALUES ('$PLUGIN2_ID', 'Test Plugin - Inline Code', 'A test plugin that executes inline Python code', 'Use this plugin to test inline code execution. No file needed.', 'custom', 'import sys
import json

result = {
    "status": "success",
    "message": "Hello from inline code!",
    "execution_type": "runtime_main"
}

print(json.dumps(result))', '{}', 0, 0, datetime('now'));

-- MCP
INSERT INTO mcp_mng (mcp_id, name, description, instruction, mcp_type, file_path, parameter, requirement, confirm_needed, is_delete, create_time)
VALUES ('$MCP_ID', 'Test MCP Server', 'A test MCP server for testing connection', 'Use this MCP server for testing. It provides basic server info.', 'stdio', '/tmp/ai_sns_test_tools/test_mcp_server.py', '{"timeout": 10}', '', 0, 0, datetime('now'));

-- Function
INSERT INTO function_mng (function_id, name, description, instruction, function_type, file_path, parameter, confirm_needed, is_delete, create_time)
VALUES ('$FUNCTION_ID', 'Calculate Sum Function', 'Calculates the sum of a list of numbers', 'Use this function to calculate sum. Pass an array of numbers in ''numbers'' parameter.', 'python', '/tmp/ai_sns_test_tools/test_function.py', '{"numbers": {"type": "array", "description": "Array of numbers to sum", "default": [1, 2, 3, 4, 5]}}', 0, 0, datetime('now'));

-- Skills
INSERT INTO skill_mng (skill_id, name, description, instruction, skill_type, parameter, confirm_needed, is_delete, create_time)
VALUES
('$SKILL1_ID', 'Screenshot Capture', 'Captures a screenshot of the entire screen', 'Use this skill to take a screenshot. No parameters needed.', 'screenshot', '{}', 1, 0, datetime('now')),
('$SKILL2_ID', 'Mouse Click', 'Simulates a mouse click at specified coordinates', 'Use this skill to click at specific screen coordinates. Provide x and y parameters.', 'mouse_click', '{"x": {"type": "int", "description": "X coordinate", "default": 100}, "y": {"type": "int", "description": "Y coordinate", "default": 100}}', 1, 0, datetime('now')),
('$SKILL3_ID', 'Keyboard Input', 'Types text using keyboard simulation', 'Use this skill to type text. Provide ''text'' parameter with the string to type.', 'keyboard_input', '{"text": {"type": "string", "description": "Text to type", "default": "Hello World"}}', 1, 0, datetime('now')),
('$SKILL4_ID', 'Custom Test Skill', 'A custom skill that executes a Python script', 'Use this custom skill for testing script execution.', 'custom', '{"action": "test"}', 0, 0, datetime('now'));

-- Update custom skill with file path
UPDATE skill_mng SET file_path = '/tmp/ai_sns_test_tools/test_skill.py' WHERE skill_id = '$SKILL4_ID';
SQL_END

if [ $? -eq 0 ]; then
    echo "✓ Successfully created test data:"
    echo "  - 2 Plugins (file + inline code)"
    echo "  - 1 MCP"
    echo "  - 1 Function"
    echo "  - 4 Skills"
    echo ""
    echo "All test tools can be executed!"
else
    echo "✗ Failed to insert test data"
    exit 1
fi
