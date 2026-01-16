# Agent Tools Integration - 快速开始指南

## 🎯 项目状态

Agent与Tools的集成已经**完成**！Agent现在可以调用Tools栏目中的各种工具。

## ✅ 已完成的工作

### 1. 数据库配置
- ✅ 创建了`agent_tools`关联表
- ✅ 为Agent 1 (Altman)关联了5个测试工具

### 2. 后端功能
- ✅ Agent实例可以从数据库加载工具
- ✅ 工具自动转换为OpenAI Function Calling格式
- ✅ LLM自动判断何时调用工具
- ✅ 工具执行器可以真实执行Plugin、MCP、Function、Skill

### 3. 前端API
- ✅ 添加了获取Agent工具的API方法
- ✅ 添加了更新Agent工具的API方法

### 4. 已关联的5个工具

Agent 1 (Altman) 已关联以下工具：

1. **✓ Real Calculator Plugin** - 计算器插件
   - 功能：执行数学计算
   - 测试：发送 "帮我计算: 123 * 456"

2. **✓ Real Weather MCP Server** - 天气MCP服务
   - 功能：查询天气信息
   - 测试：发送 "查询北京的天气"

3. **✓ Real Greeting Function** - 问候函数
   - 功能：发送问候消息
   - 测试：发送 "向我问好"

4. **✓ Real Screenshot Skill** - 截图技能
   - 功能：截取屏幕
   - 测试：发送 "帮我截个屏"

5. **✓ Real System Check Skill** - 系统检查技能
   - 功能：检查系统状态
   - 测试：发送 "检查系统状态"

## 🚀 快速测试

### 方式一：运行测试脚本（推荐）

```bash
# 1. 启动后端服务器
python3 api_server.py

# 2. 在新终端运行测试脚本
python3 test_agent_tools.py
```

测试脚本会自动：
- ✓ 验证数据库工具配置
- ✓ 测试API接口
- ✓ 测试工具调用功能

### 方式二：手动测试

1. **启动后端**
```bash
python3 api_server.py
```

2. **启动前端**
```bash
npm start
```

3. **在Agent聊天窗口测试**
   - 打开Electron应用
   - 选择Agent 1 (Altman)
   - 发送测试消息（见上面的测试示例）

## 📊 验证工具关联

运行以下命令验证Agent的工具配置：

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('db/db.sqlite')
cursor = conn.cursor()

cursor.execute('''
    SELECT
        at.tool_type,
        CASE at.tool_type
            WHEN 'plugin' THEN (SELECT name FROM pluginmng WHERE plugin_id = at.tool_id)
            WHEN 'mcp' THEN (SELECT name FROM mcp_mng WHERE mcp_id = at.tool_id)
            WHEN 'function' THEN (SELECT name FROM function_mng WHERE function_id = at.tool_id)
            WHEN 'skill' THEN (SELECT name FROM skill_mng WHERE skill_id = at.tool_id)
        END as tool_name,
        at.priority
    FROM agent_tools at
    WHERE at.agent_id = 1
    ORDER BY at.priority DESC
''')

print('Agent 1的工具:')
for row in cursor.fetchall():
    print(f'  [{row[0]:8}] {row[1]:40} (优先级: {row[2]})')

conn.close()
"
```

## 🔍 工作原理

```
用户消息
    ↓
Agent接收消息
    ↓
从数据库加载工具列表
    ↓
将工具转换为OpenAI格式
    ↓
发送给LLM（包含工具描述）
    ↓
LLM决定是否调用工具
    ↓
        → 不需要工具：直接回复
        → 需要工具：返回tool_calls
            ↓
        执行工具（Plugin/MCP/Function/Skill）
            ↓
        获取工具结果
            ↓
        将结果发送回LLM
            ↓
        LLM生成最终回复
            ↓
返回给用户
```

## 📝 API接口

### 获取Agent的工具
```http
GET /api/agent/{agent_id}/tools
```

### 更新Agent的工具
```http
POST /api/agent/{agent_id}/tools
Content-Type: application/json

[
  {"tool_type": "plugin", "tool_id": "PL...", "priority": 10},
  {"tool_type": "mcp", "tool_id": "MC...", "priority": 9}
]
```

### Agent聊天（自动调用工具）
```http
POST /api/agent/{agent_id}/chat
Content-Type: application/json

{
  "message": "帮我计算123*456",
  "conversation_id": "test_001"
}
```

## 🎨 前端UI（可选扩展）

如需在前端显示工具列表，请参考 `AGENT_TOOLS_INTEGRATION_GUIDE.md` 中的详细说明。

基本步骤：
1. 在Agent右侧面板添加Tools页签
2. 调用`agentApi.getAgentTools(agentId)`获取工具
3. 渲染工具列表

## ❓ 故障排查

### 工具未被调用
```bash
# 1. 检查工具是否已关联
python3 -c "import sqlite3; conn = sqlite3.connect('db/db.sqlite'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM agent_tools WHERE agent_id = 1'); print(f'工具数量: {cursor.fetchone()[0]}'); conn.close()"

# 2. 查看后端日志
tail -f api_server.log  # 或查看控制台输出
```

### LLM未配置
```bash
# 检查Agent的LLM配置
python3 -c "from db.DBFactory import Session, AgentCfg; session = Session(); agent = session.query(AgentCfg).filter_by(id=1).first(); print(f'模型: {agent.defaultmodel}'); session.close()"
```

如果Agent没有配置LLM，需要：
1. 在前端选择一个模型配置
2. 或者在数据库中为Agent设置默认模型

## 📚 更多文档

- **完整集成指南**: `AGENT_TOOLS_INTEGRATION_GUIDE.md`
- **测试脚本**: `test_agent_tools.py`
- **数据库脚本**: `add_agent_tools.sql`

## 🎉 成果

✅ Agent可以自动调用5种类型的工具
✅ 工具调用对用户透明（自然对话即可）
✅ 支持Plugin、MCP、Function、Skill
✅ 工具参数自动验证和传递
✅ 工具执行结果自动转化为自然语言回复

## 📞 下一步

1. **测试功能** - 运行`python3 test_agent_tools.py`
2. **配置LLM** - 确保Agent有正确的API key
3. **开始对话** - 在聊天窗口测试工具调用
4. **扩展UI** - （可选）添加前端工具管理界面

---

**祝使用愉快！** 🚀

如有问题，请查看详细的集成指南文档。
