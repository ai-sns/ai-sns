# Tools Module - Complete Implementation

## Overview

Tools模块是AI-SNS系统的重要组成部分，用于管理可被AI大模型调用的各类工具。该模块包含4个子模块：

1. **Tools Plugin** - 插件工具管理
2. **MCP** - Model Context Protocol 管理
3. **Function** - 函数工具管理
4. **Computer Use** - 计算机使用工具管理

## Architecture

### Backend Structure

```
backend/modules/tools/
├── __init__.py          # 模块初始化
├── schemas.py           # Pydantic数据模型
├── service.py           # 业务逻辑层
├── router.py            # FastAPI路由
└── dependencies.py      # 依赖注入
```

### Frontend Structure

```
renderer/
├── js/
│   └── tools-manager.js  # Tools管理器
├── css/
│   └── tools.css         # Tools样式
└── index.html            # 引入Tools资源
```

### Database Models

数据库模型定义在 `backend/database/models/system.py`:

- `PluginMng` - 插件管理表
- `McpMng` - MCP管理表
- `FunctionMng` - 函数管理表
- `SkillMng` - 技能/Computer Use管理表

## API Endpoints

### Plugins

- `GET /api/tools/plugins` - 获取所有插件
- `GET /api/tools/plugins/{plugin_id}` - 获取单个插件
- `POST /api/tools/plugins` - 创建插件
- `PUT /api/tools/plugins/{plugin_id}` - 更新插件
- `DELETE /api/tools/plugins/{plugin_id}` - 删除插件

### MCP

- `GET /api/tools/mcp` - 获取所有MCP
- `GET /api/tools/mcp/{mcp_id}` - 获取单个MCP
- `POST /api/tools/mcp` - 创建MCP
- `PUT /api/tools/mcp/{mcp_id}` - 更新MCP
- `DELETE /api/tools/mcp/{mcp_id}` - 删除MCP

### Functions

- `GET /api/tools/functions` - 获取所有函数
- `GET /api/tools/functions/{function_id}` - 获取单个函数
- `POST /api/tools/functions` - 创建函数
- `PUT /api/tools/functions/{function_id}` - 更新函数
- `DELETE /api/tools/functions/{function_id}` - 删除函数

### Skills (Computer Use)

- `GET /api/tools/skills` - 获取所有技能
- `GET /api/tools/skills/{skill_id}` - 获取单个技能
- `POST /api/tools/skills` - 创建技能
- `PUT /api/tools/skills/{skill_id}` - 更新技能
- `DELETE /api/tools/skills/{skill_id}` - 删除技能

## Usage Examples

### Creating a Plugin

```python
import requests

plugin_data = {
    "name": "Weather API Plugin",
    "description": "Get weather information",
    "instruction": "Use this to get current weather data",
    "plugin_type": "api",
    "confirm_needed": True,
    "used_in_sns": False
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/plugins",
    json=plugin_data
)
plugin = response.json()
print(f"Created plugin: {plugin['plugin_id']}")
```

### Creating an MCP Server

```python
mcp_data = {
    "name": "Local File System MCP",
    "description": "Access local file system",
    "mcp_type": "stdio",
    "instruction": "Use for file operations",
    "file_path": "/path/to/mcp/server",
    "parameter": json.dumps({"root_dir": "/home/user"})
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/mcp",
    json=mcp_data
)
```

### Creating a Function

```python
function_data = {
    "name": "calculate_distance",
    "description": "Calculate distance between two points",
    "function_type": "python",
    "instruction": "Use to calculate Euclidean distance",
    "file_path": "/path/to/function.py",
    "parameter": json.dumps({
        "x1": "number",
        "y1": "number",
        "x2": "number",
        "y2": "number"
    })
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/functions",
    json=function_data
)
```

### Creating a Computer Use Tool

```python
skill_data = {
    "name": "file_browser",
    "description": "Browse and search files",
    "skill_type": "computer_use",
    "instruction": "Use to browse file system",
    "confirm_needed": True
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/skills",
    json=skill_data
)
```

## Frontend Usage

### JavaScript API

```javascript
// Initialize Tools Manager
const toolsManager = new ToolsManager();

// Get all plugins
const plugins = await toolsManager.getAllPlugins();

// Create a new plugin
const newPlugin = await toolsManager.createPlugin({
    name: "My Plugin",
    description: "Plugin description",
    confirm_needed: true
});

// Update plugin
await toolsManager.updatePlugin(pluginId, {
    description: "Updated description"
});

// Delete plugin
await toolsManager.deletePlugin(pluginId);

// Switch between tool types
toolsManager.switchTab('mcp'); // or 'functions', 'skills'
```

## Testing

Run the test script to verify all API endpoints:

```bash
# Start the API server first
python api_server.py

# In another terminal, run tests
python test_tools_api.py
```

Expected output:
```
==================================================
Tools API Test Suite
==================================================
Testing API at: http://127.0.0.1:8788/api/tools
✓ API server is running

==================================================
Testing Plugin CRUD Operations
==================================================
1. Creating a plugin...
✓ Plugin created successfully: PL20260114...
...

==================================================
Test Summary
==================================================
Plugin: ✓ PASS
MCP: ✓ PASS
Function: ✓ PASS
Skill: ✓ PASS

✓ All tests passed!
```

## Data Persistence

All tool data is persisted in SQLite database (`db/db.sqlite`):

- Plugins stored in `pluginmng` table
- MCPs stored in `mcp_mng` table
- Functions stored in `function_mng` table
- Skills stored in `skill_mng` table

All operations use soft delete (`is_delete` flag) for data safety.

## Frontend UI Features

1. **Tab Navigation** - Switch between 4 tool types
2. **Tool Cards** - Visual display of each tool
3. **CRUD Operations** - Create, read, update, delete tools
4. **Search & Filter** - Find specific tools
5. **Real-time Updates** - Immediate UI refresh after operations
6. **Responsive Design** - Works on different screen sizes
7. **Dark Theme Support** - Follows system theme

## Configuration

No additional configuration required. The module uses the existing database connection from `backend/database/base.py`.

## Integration with AI Agents

Tools can be called by AI agents through the Agent module:

```python
# Example: Agent using a tool
from backend.modules.agent.tool_executor import ToolExecutor

executor = ToolExecutor()
result = await executor.execute_tool(
    tool_id="PL20260114...",
    tool_type="plugin",
    parameters={"location": "Beijing"}
)
```

## Security Considerations

1. **Input Validation** - All inputs validated using Pydantic schemas
2. **SQL Injection Protection** - Using SQLAlchemy ORM
3. **Soft Delete** - Data never permanently deleted
4. **Confirm Needed Flag** - Tools can require user confirmation
5. **CORS Protection** - Configured in main API server

## Troubleshooting

### API not responding
```bash
# Check if API server is running
curl http://127.0.0.1:8788/health

# Start API server
python api_server.py
```

### Frontend not loading tools
1. Check browser console for errors
2. Verify API_BASE_URL in tools-manager.js
3. Ensure tools-manager.js is loaded in index.html

### Database errors
```bash
# Check database file permissions
ls -la db/db.sqlite

# Recreate database if needed
python backend/database/base.py
```

## Future Enhancements

1. Tool versioning and rollback
2. Tool marketplace integration
3. Tool execution logs and monitoring
4. Tool performance metrics
5. Tool dependency management
6. Batch tool operations
7. Tool import/export functionality
8. Tool testing framework

## Support

For issues and questions:
- Check the main AI-SNS documentation
- Review backend/modules/tools/router.py for API details
- Examine renderer/js/tools-manager.js for frontend logic

## License

Same as AI-SNS project license.
