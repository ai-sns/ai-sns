# Tools Module - Quick Start Guide

## 快速开始

### 1. 启动API服务器

```bash
cd /root/sharedata3/ai-sns-el
python api_server.py
```

服务器将在 `http://127.0.0.1:8788` 启动

### 2. 启动Electron前端

```bash
# 如果使用npm
npm start

# 或者使用electron
electron electron/main.js
```

### 3. 访问Tools页面

在Electron应用中，点击左侧导航栏的 "Tools" 图标

### 4. 使用功能

#### 查看工具列表

1. 打开Tools页面
2. 选择标签页：Tools Plugin、MCP、Function 或 Computer Use
3. 查看当前工具列表

#### 创建新工具

1. 点击右上角 "Add New Tool" 按钮
2. 填写表单信息：
   - **Name**: 工具名称（必填）
   - **Description**: 工具描述
   - **Instruction**: AI如何使用此工具的说明
   - **Type**: 工具类型
   - **Confirm Needed**: 是否需要用户确认
3. 点击 "Create" 保存

#### 编辑工具

1. 找到要编辑的工具卡片
2. 点击编辑按钮（铅笔图标）
3. 修改信息
4. 保存更改

#### 删除工具

1. 找到要删除的工具卡片
2. 点击删除按钮（垃圾桶图标）
3. 确认删除

### 5. 使用API测试

```bash
# 运行完整的API测试
python test_tools_api.py
```

### 示例：创建天气插件

```python
import requests

plugin_data = {
    "name": "Weather Plugin",
    "description": "Get current weather information",
    "instruction": "Use this plugin to retrieve weather data for any location. Provide the city name as parameter.",
    "plugin_type": "weather_api",
    "confirm_needed": False,
    "used_in_sns": True
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/plugins",
    json=plugin_data
)

if response.status_code == 200:
    plugin = response.json()
    print(f"Plugin created with ID: {plugin['plugin_id']}")
else:
    print(f"Error: {response.text}")
```

### 示例：创建MCP服务器

```python
mcp_data = {
    "name": "File System MCP",
    "description": "Model Context Protocol server for file operations",
    "mcp_type": "stdio",
    "instruction": "Use for reading, writing, and managing files",
    "file_path": "/path/to/mcp-server",
    "confirm_needed": True
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/mcp",
    json=mcp_data
)
```

### 示例：创建函数工具

```python
import json

function_data = {
    "name": "calculate_average",
    "description": "Calculate average of numbers",
    "function_type": "python",
    "instruction": "Use to calculate the average of a list of numbers",
    "file_path": "/functions/average.py",
    "parameter": json.dumps({
        "numbers": "array of numbers"
    })
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/functions",
    json=function_data
)
```

### 示例：创建Computer Use工具

```python
skill_data = {
    "name": "Screenshot Tool",
    "description": "Take screenshots of the screen",
    "skill_type": "computer_use",
    "instruction": "Use to capture screen images",
    "confirm_needed": True,
    "used_in_sns": False
}

response = requests.post(
    "http://127.0.0.1:8788/api/tools/skills",
    json=skill_data
)
```

## 数据持久化

所有数据自动保存到 `db/db.sqlite` 数据库：

- 插件 → `pluginmng` 表
- MCP → `mcp_mng` 表
- 函数 → `function_mng` 表
- 技能 → `skill_mng` 表

## API文档

访问 `http://127.0.0.1:8788/docs` 查看完整的交互式API文档（Swagger UI）

## 常见问题

### Q: 前端显示"Loading tools..."但没有数据？

**A:** 检查以下几点：
1. API服务器是否正在运行
2. 浏览器控制台是否有错误
3. 数据库中是否有数据

### Q: 创建工具后不显示？

**A:**
1. 检查是否有错误提示
2. 刷新页面重新加载数据
3. 查看API响应状态

### Q: 如何查看已创建的工具？

**A:**
```bash
# 使用curl查看所有插件
curl http://127.0.0.1:8788/api/tools/plugins

# 使用curl查看所有MCP
curl http://127.0.0.1:8788/api/tools/mcp

# 使用curl查看所有函数
curl http://127.0.0.1:8788/api/tools/functions

# 使用curl查看所有技能
curl http://127.0.0.1:8788/api/tools/skills
```

## 架构说明

```
┌─────────────────────────────────────────┐
│         Electron Frontend               │
│  ┌──────────────────────────────────┐  │
│  │  Tools Management Page           │  │
│  │  - Plugin Tab                    │  │
│  │  - MCP Tab                       │  │
│  │  - Function Tab                  │  │
│  │  - Computer Use Tab              │  │
│  └──────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
               ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  ┌──────────────────────────────────┐  │
│  │  /api/tools Router               │  │
│  │  - PluginService                 │  │
│  │  - MCPService                    │  │
│  │  - FunctionService               │  │
│  │  - SkillService                  │  │
│  └──────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy ORM
               ▼
┌─────────────────────────────────────────┐
│         SQLite Database                 │
│  - pluginmng                            │
│  - mcp_mng                              │
│  - function_mng                         │
│  - skill_mng                            │
└─────────────────────────────────────────┘
```

## 下一步

1. 为工具添加更多元数据字段
2. 实现工具导入/导出功能
3. 添加工具使用统计
4. 实现工具版本管理
5. 集成AI Agent调用工具

## 需要帮助？

- 查看 `TOOLS_MODULE_README.md` 获取详细文档
- 运行 `python test_tools_api.py` 测试API
- 检查 `backend/modules/tools/` 目录中的源代码
