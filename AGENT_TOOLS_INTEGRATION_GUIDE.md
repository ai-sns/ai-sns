# Agent Tools Integration Guide - Agent工具集成指南

## 概述
本指南说明如何让Electron的Agent栏目调用Tools栏目中的各种工具。

##已完成的工作

### 1. 数据库配置 ✅
- 创建了`agent_tools`表用于存储Agent和Tool的关联关系
- 为Agent 1 (Altman)关联了5个指定工具：
  - ✓ Real Calculator Plugin (PL2026011510474128484)
  - ✓ Real Weather MCP Server (MC202601158934785372)
  - ✓ Real Greeting Function (FN2026011510474121480)
  - ✓ Real Screenshot Skill (SK2026011510474112028)
  - ✓ Real System Check Skill (SK2026011510474127797)

### 2. 后端架构 ✅
- `AgentInstance`类已实现工具调用机制 (`backend/modules/agent/agent_instance.py`)
- `ToolConverter`将不同类型工具转换为OpenAI Function Calling格式
- `ToolRouter`路由工具调用到对应执行器
- `ToolExecutor`真实执行工具代码
- API接口已完善：
  - `GET /api/agent/{agent_id}/tools` - 获取Agent的工具
  - `POST /api/agent/{agent_id}/tools` - 更新Agent的工具
  - `GET /api/agent/{agent_id}/available-tools` - 获取所有可用工具

### 3. 前端API ✅
- 在`agentApi.js`中添加了3个工具管理API方法：
  - `getAgentTools(agentId)` - 获取Agent工具
  - `updateAgentTools(agentId, tools)` - 更新Agent工具
  - `getAvailableTools(agentId)` - 获取可用工具

## 需要完成的前端UI集成

### 1. 在Agent右侧面板添加Tools页签

修改文件: `renderer/js/modules/agent/AgentPage.js`

在第282行附近（File页签按钮之后）添加Tools页签按钮：

```javascript
<button class="settings-tab" data-tab="tools" data-agent-id="${agent.id}">
    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
        <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
    </svg>
    <span>Tools</span>
</button>
```

在第241行附近（File页签内容之后）添加Tools页签内容：

```javascript
<!-- Tools 页签内容 -->
<div class="tab-pane" data-tab="tools">
    <div class="settings-section">
        <div class="settings-section-title">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="#1a73e8">
                <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
            </svg>
            <span>已关联工具</span>
        </div>
        <div class="tools-list" id="toolsList-${agent.id}" data-agent-id="${agent.id}">
            <!-- 工具列表将通过JavaScript动态加载 -->
            <div class="loading-tools">加载工具中...</div>
        </div>
    </div>
</div>
```

### 2. 添加工具加载和显示逻辑

修改文件: `renderer/js/modules/agent/agentHandlers.js`

在`initPluginEvents()`方法之后添加：

```javascript
/**
 * 初始化Tools相关事件
 */
initToolsEvents() {
    // 监听页签切换到Tools时加载工具列表
    document.addEventListener('click', async (e) => {
        const tab = e.target.closest('.settings-tab[data-tab="tools"]');
        if (tab) {
            const agentId = tab.dataset.agentId;
            await this.loadAgentTools(agentId);
        }
    });
},

/**
 * 加载Agent的工具列表
 */
async loadAgentTools(agentId) {
    const toolsList = document.getElementById(`toolsList-${agentId}`);
    if (!toolsList) return;

    try {
        // 显示加载状态
        toolsList.innerHTML = '<div class="loading-tools">加载工具中...</div>';

        // 获取Agent的工具
        const result = await agentApi.getAgentTools(agentId);

        if (result.success && result.data && result.data.tools) {
            const tools = result.data.tools;

            if (tools.length === 0) {
                toolsList.innerHTML = '<div class="no-tools">暂无关联工具</div>';
                return;
            }

            // 渲染工具列表
            const toolsHTML = tools.map(tool => this.renderToolItem(tool)).join('');
            toolsList.innerHTML = toolsHTML;
        } else {
            toolsList.innerHTML = '<div class="error-tools">加载工具失败</div>';
        }
    } catch (error) {
        console.error('加载Agent工具失败:', error);
        toolsList.innerHTML = '<div class="error-tools">加载工具失败</div>';
    }
},

/**
 * 渲染单个工具项
 */
renderToolItem(tool) {
    const typeIcon = {
        'plugin': '🔌',
        'mcp': '🌐',
        'function': '⚙️',
        'skill': '🎯'
    }[tool.tool_type] || '📦';

    const typeName = {
        'plugin': 'Plugin',
        'mcp': 'MCP',
        'function': 'Function',
        'skill': 'Skill'
    }[tool.tool_type] || tool.tool_type;

    return `
        <div class="tool-item" data-tool-type="${tool.tool_type}" data-tool-id="${tool.tool_id || tool.plugin_id || tool.mcp_id || tool.function_id || tool.skill_id}">
            <div class="tool-icon">${typeIcon}</div>
            <div class="tool-info">
                <div class="tool-name">${tool.name || 'Unnamed Tool'}</div>
                <div class="tool-meta">
                    <span class="tool-type-badge">${typeName}</span>
                    <span class="tool-priority">优先级: ${tool.priority || 0}</span>
                </div>
            </div>
            <div class="tool-status ${tool.enabled ? 'enabled' : 'disabled'}">
                ${tool.enabled ? '✓ 启用' : '✗ 禁用'}
            </div>
        </div>
    `;
}
```

在`bindEvents()`方法中添加初始化调用：

```javascript
// Tools 相关事件
this.initToolsEvents();
```

### 3. 添加CSS样式

在对应的CSS文件中添加工具列表样式：

```css
/* Tools列表样式 */
.tools-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 500px;
    overflow-y: auto;
}

.tool-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.tool-icon {
    font-size: 24px;
    flex-shrink: 0;
}

.tool-info {
    flex: 1;
    min-width: 0;
}

.tool-name {
    font-weight: 500;
    color: #202124;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.tool-meta {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: #5f6368;
}

.tool-type-badge {
    padding: 2px 6px;
    background: #e8f0fe;
    color: #1967d2;
    border-radius: 4px;
}

.tool-priority {
    padding: 2px 6px;
    background: #fef7e0;
    color: #ea8600;
    border-radius: 4px;
}

.tool-status {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 4px;
    flex-shrink: 0;
}

.tool-status.enabled {
    background: #e6f4ea;
    color: #1e8e3e;
}

.tool-status.disabled {
    background: #fce8e6;
    color: #d93025;
}

.loading-tools, .no-tools, .error-tools {
    padding: 20px;
    text-align: center;
    color: #5f6368;
}

.error-tools {
    color: #d93025;
}
```

## 测试Agent工具调用

### 1. 启动后端服务器

```bash
cd /mnt/c/dev/agi-ev/ai-sns-el
python3 api_server.py
```

### 2. 启动Electron前端

```bash
npm start
```

### 3. 测试工具调用

在Agent聊天窗口中发送以下测试消息：

1. **测试Calculator Plugin**:
   ```
   帮我计算: 123 * 456 + 789
   ```

2. **测试Weather MCP**:
   ```
   查询北京的天气
   ```

3. **测试Greeting Function**:
   ```
   向我问好
   ```

4. **测试Screenshot Skill**:
   ```
   帮我截个屏
   ```

5. **测试System Check Skill**:
   ```
   检查系统状态
   ```

## 工作原理

1. **用户发送消息** → Agent聊天输入框
2. **前端调用** → `agentApi.agentChatStream(agentId, message)`
3. **后端处理**:
   - `AgentInstance.chat_stream()` 接收消息
   - `load_tools_from_db()` 加载Agent的关联工具
   - `_prepare_tools_schema()` 将工具转换为OpenAI格式
   - LLM根据工具描述决定是否调用工具
   - 如果需要调用工具，LLM返回`tool_calls`
4. **工具执行**:
   - `_execute_tool()` 解析工具名称和参数
   - `ToolRouter.execute_tool()` 路由到对应执行器
   - `ToolExecutor` 真实执行工具代码
   - 返回执行结果
5. **结果返回** → 再次调用LLM，将工具结果转化为自然语言回复
6. **流式输出** → 前端接收并显示回复

## 验证工具是否成功关联

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('db/db.sqlite')
cursor = conn.cursor()

# 查询Agent 1的工具
cursor.execute('''
    SELECT
        at.tool_type,
        CASE at.tool_type
            WHEN 'plugin' THEN (SELECT name FROM pluginmng WHERE plugin_id = at.tool_id)
            WHEN 'mcp' THEN (SELECT name FROM mcp_mng WHERE mcp_id = at.tool_id)
            WHEN 'function' THEN (SELECT name FROM function_mng WHERE function_id = at.tool_id)
            WHEN 'skill' THEN (SELECT name FROM skill_mng WHERE skill_id = at.tool_id)
        END as tool_name,
        at.enabled,
        at.priority
    FROM agent_tools at
    WHERE at.agent_id = 1
    ORDER BY at.priority DESC
''')

print('Agent 1 (Altman) 的关联工具:')
for row in cursor.fetchall():
    print(f'  [{row[0]}] {row[1]} - 优先级: {row[3]} - {\"启用\" if row[2] else \"禁用\"}')

conn.close()
"
```

## 故障排查

### 工具未被调用
1. 检查Agent是否正确关联了工具（运行上面的验证脚本）
2. 检查后端日志，确认工具已加载：`[AgentInstance] 已加载 5 个工具`
3. 检查LLM返回的是否包含`tool_calls`

### 工具执行失败
1. 检查后端日志中的错误信息
2. 确认工具的文件路径或代码是否正确
3. 对于MCP工具，确认MCP服务器是否可以正常启动

### 前端UI不显示工具
1. 检查浏览器控制台是否有JavaScript错误
2. 确认API请求是否成功返回数据
3. 检查CSS样式是否正确加载

## 下一步扩展

1. **添加工具管理界面** - 允许用户在前端选择和配置Agent的工具
2. **工具调用历史** - 记录和展示工具的调用历史
3. **工具性能监控** - 监控工具的执行时间和成功率
4. **工具参数验证** - 在前端添加工具参数的验证和提示
5. **批量工具管理** - 支持为多个Agent批量配置工具

## 总结

Agent与Tools的集成已经在后端完全实现，前端只需添加UI展示即可。核心机制是：
- Agent从数据库加载关联的工具
- 将工具转换为LLM可理解的Function Calling格式
- LLM根据用户问题决定是否调用工具
- 工具执行后，结果返回给LLM进行总结
- 用户看到最终的自然语言回复

整个过程对用户是透明的，用户只需要正常对话，AI会自动判断何时需要使用工具。
