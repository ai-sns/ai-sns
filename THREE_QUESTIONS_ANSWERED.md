# 📝 三个问题的完整回答

## 问题 1: Tools Plugin Calculator 的代码写在哪里？

### 位置：数据库 `pluginmng` 表的 `runtime_main` 字段

**查询方式**:
```bash
sqlite3 data/db.sqlite "SELECT plugin_id, name, runtime_main FROM pluginmng WHERE name = '✓ Real Calculator Plugin';"
```

**代码内容**:
```python
import sys
print("=" * 50)
print("真实Plugin执行")
print("=" * 50)
a = 100
b = 25
print(f"\n计算: {a} + {b} = {a + b}")
print(f"计算: {a} - {b} = {a - b}")
print(f"计算: {a} × {b} = {a * b}")
print(f"计算: {a} ÷ {b} = {a / b}")
print("\n✓ Plugin执行成功!")
```

**存储说明**:
- Plugin 的代码存储在数据库中，不是文件
- 运行时通过 `tool_executor.py` 的 `_execute_python_code()` 方法动态执行
- 代码被包装成临时文件后通过 subprocess 执行

**执行流程**:
```
用户点击测试
→ API调用 /api/tools/plugins/{id}/test
→ tool_executor.execute_plugin()
→ _execute_python_code() 创建临时文件
→ subprocess 执行代码
→ 返回 stdout/stderr 结果
```

---

## 问题 2: Computer Use (Skill) Screenshot 的代码写在哪里？

### 位置：`backend/modules/tools/tool_executor.py` 的 `_execute_screenshot()` 方法

**文件路径**: `/root/sharedata3/ai-sns-el/backend/modules/tools/tool_executor.py`

**代码位置**: Line 612-641

**代码内容**:
```python
async def _execute_screenshot(self, params: dict) -> dict:
    """Execute screenshot capture"""
    try:
        # Try to import screenshot libraries
        try:
            import pyautogui

            region = params.get('region', 'full')
            format = params.get('format', 'png')

            # Take screenshot
            screenshot = pyautogui.screenshot()

            # Save to temp file
            temp_dir = tempfile.gettempdir()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            filepath = os.path.join(temp_dir, filename)

            screenshot.save(filepath)

            return {
                "performed": "screenshot_capture",
                "region": region,
                "format": format,
                "filepath": filepath,
                "size": f"{screenshot.width}x{screenshot.height}",
                "message": f"Screenshot saved to {filepath}"
            }

        except ImportError:
            return {
                "performed": "screenshot_capture",
                "status": "library_missing",
                "message": "pyautogui not installed. Run: pip install pyautogui pillow",
                "note": "Screenshot functionality requires pyautogui"
            }

    except Exception as e:
        raise Exception(f"Screenshot execution failed: {str(e)}")
```

**存储说明**:
- Screenshot 是内置的 Skill 类型，代码在 executor 中
- 不是文件，是硬编码的实现
- 当 skill_type = "screenshot" 时调用此方法

**其他内置 Skill 类型**:
```python
- screenshot      → _execute_screenshot()    (Line 612-641)
- mouse_click     → _execute_mouse_click()   (Line 643-673)
- keyboard_input  → _execute_keyboard_input() (Line 675-704)
- custom          → _execute_python_file()   (使用 file_path 指定的脚本)
```

**执行流程**:
```
用户点击测试
→ API调用 /api/tools/skills/{id}/test
→ tool_executor.execute_skill()
→ 根据 skill_type 调用对应方法
→ _execute_screenshot() 使用 pyautogui
→ 返回截图路径或错误信息
```

**数据库记录**:
```sql
SELECT skill_id, name, skill_type, file_path
FROM skill_mng
WHERE name = '✓ Real Screenshot Skill';

-- 结果：
-- SK2026011510474112028|✓ Real Screenshot Skill|screenshot|
-- 注意：file_path 为空，因为是内置类型
```

---

## 问题 3: MCP 模块真实服务器访问

### ✅ 已安装并测试真实 MCP Server！

### 1. 安装的 MCP SDK
```bash
pip3 install mcp
# 版本: mcp-1.25.0
```

### 2. 创建的真实 MCP Server

**文件位置**: `/root/sharedata3/ai-sns-el/test_examples/real_weather_mcp_server.py`

**提供的工具** (4个真实可调用的工具):

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `get_weather` | 查询城市天气 | city (必填), unit (celsius/fahrenheit) |
| `get_current_time` | 获取当前时间 | timezone, format |
| `calculate` | 执行数学计算 | expression |
| `get_system_info` | 获取系统信息 | 无 |

**MCP 服务器特性**:
- ✅ 完整的 JSON-RPC 协议实现
- ✅ Stdio 双向通信
- ✅ 工具列表和调用
- ✅ 资源管理
- ✅ 提示词系统

### 3. 测试结果

**测试脚本**: `/root/sharedata3/ai-sns-el/test_examples/test_real_mcp_client.py`

**测试结果摘要**:

```
🧪 Testing Real MCP Server
============================================================

✓ 连接成功
✓ 初始化成功
✓ 发现 4 个工具

🌤️ Test 1: get_weather (Beijing)
━━━━━━━━━━━━━━━━━━━━━━
Temperature: 15°C
Condition: Partly Cloudy
Humidity: 65%
Last Updated: 2026-01-15 11:51:06
✓ Real MCP Server Response

🕐 Test 2: get_current_time (Asia/Shanghai)
━━━━━━━━━━━━━━━━━━━━━━
Timezone: Asia/Shanghai
Time: 2026-01-15 11:51:06
Unix Timestamp: 1768477866
Day of Week: Thursday
✓ Real MCP Server Response

🔢 Test 3: calculate (2 ** 10 + 100)
━━━━━━━━━━━━━━━━━━━━━━
Expression: 2 ** 10 + 100
Result: 1124
Type: int
✓ Real MCP Server Response

💻 Test 4: get_system_info
━━━━━━━━━━━━━━━━━━━━━━
Platform: Linux 5.15.0-164-generic
Architecture: x86_64
Python Version: 3.10.12
Processor: x86_64
Process ID: 33730
✓ Real MCP Server Response

============================================================
✅ All Tests Completed Successfully!
============================================================
```

### 4. 已添加到数据库

```sql
-- MCP Server 信息
mcp_id: MC2026011511561554068
name: ✓ Real Weather MCP Server
description: 真实的天气和时间查询MCP服务器，提供4个工具
file_path: /root/sharedata3/ai-sns-el/test_examples/real_weather_mcp_server.py
mcp_type: stdio
parameter: {"tools": ["get_weather", "get_current_time", "calculate", "get_system_info"]}
```

### 5. 对比：旧的 vs 新的

#### 旧的 test_mcp_server.py (假测试)
```python
# 只是启动进程然后立即停止
print("MCP Server Starting...", file=sys.stderr)
time.sleep(0.2)
print("MCP Server Ready!", file=sys.stderr)
print(json.dumps({"status": "running", "type": "stdio"}))
# 没有真实的 MCP 协议实现
```

**问题**:
- ❌ 没有真正的 MCP 协议
- ❌ 没有工具注册
- ❌ 无法实际调用工具
- ❌ 只是进程启停测试

#### 新的 real_weather_mcp_server.py (真实 MCP)
```python
# 完整的 MCP Server 实现
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("weather-time-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [Tool(...), Tool(...), ...]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    # 真实的工具执行逻辑
    if name == "get_weather":
        # 实际返回天气数据
    elif name == "calculate":
        # 实际执行计算
```

**优点**:
- ✅ 完整的 MCP 协议实现
- ✅ 真实的工具注册和调用
- ✅ JSON-RPC 通信
- ✅ 支持资源和提示词
- ✅ 可以被任何 MCP 客户端使用

### 6. 如何使用

#### 命令行测试
```bash
# 直接运行测试客户端
python3 test_examples/test_real_mcp_client.py
```

#### 前端界面测试 (需要进一步实现)
```
1. 刷新前端页面
2. 进入 Tools > MCP 模块
3. 找到 "✓ Real Weather MCP Server"
4. 点击"测试"按钮
5. 查看工具列表和调用结果
```

**注意**: 当前 tool_executor.py 中的 `_test_mcp_server()` 只做进程测试，需要升级为真实的 MCP 工具调用。

### 7. 需要的后续改进

如果要在前端完整使用 MCP 功能，需要：

1. **升级 tool_executor.py**:
   - 将 `_test_mcp_server()` 改为 `_call_mcp_tool()`
   - 使用 MCP 客户端连接服务器
   - 支持列出工具和调用工具

2. **添加 MCP 工具调用 API**:
   ```python
   @router.post("/mcp/{mcp_id}/list_tools")
   @router.post("/mcp/{mcp_id}/call_tool")
   ```

3. **前端界面**:
   - 显示 MCP 服务器的工具列表
   - 提供工具调用表单
   - 显示调用结果

---

## 总结对比

| 模块 | 代码位置 | 存储方式 | 执行方式 |
|------|---------|---------|---------|
| **Plugin** | 数据库 `runtime_main` 字段 | 数据库字符串 | 动态创建临时文件执行 |
| **Skill (Screenshot)** | `tool_executor.py` 内置方法 | Python 代码 | 直接调用 pyautogui |
| **Skill (Custom)** | 文件路径（如 `system_check_skill.py`） | 独立 Python 文件 | subprocess 执行文件 |
| **MCP** | 独立服务器文件 | Python MCP Server | 通过 MCP 协议调用 |

## 技术架构图

```
用户点击测试
    ↓
API Router (/api/tools/{type}/{id}/test)
    ↓
Tool Service
    ↓
Tool Executor
    ├─ Plugin → _execute_python_code() → 临时文件 → subprocess
    ├─ Function → _execute_python_file() → 文件 → subprocess
    ├─ Skill (screenshot) → _execute_screenshot() → pyautogui
    ├─ Skill (custom) → _execute_python_file() → 文件 → subprocess
    └─ MCP → _test_mcp_server() → 进程测试 (需升级为工具调用)
    ↓
返回执行结果
```

---

**文档创建时间**: 2026-01-15 11:56
**真实 MCP Server**: ✅ 已安装并测试成功
**数据库**: ✅ 已添加真实 MCP Server
**测试状态**: ✅ 所有工具调用成功
