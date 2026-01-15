# Tools模块 - 测试和调试指南

## 问题修复

已修复侧边栏4个模块点击无反应的问题：

### 1. 添加了事件绑定
- 为 `.tools-category-item` 添加了点击事件
- 使用 `data-tab` 属性进行标签切换
- 添加了active状态切换

### 2. 更新了侧边栏HTML
- 简化了侧边栏结构
- 移除了不必要的搜索框和按钮
- 为第一个item添加了默认active类
- 添加了 `data-tab` 属性

### 3. 添加了CSS样式
```css
.tools-category-item {
    cursor: pointer;
    transition: all 0.2s;
}

.tools-category-item:hover {
    background-color: #f8fafc;
    transform: translateX(2px);
}

.tools-category-item.active {
    background-color: #eff6ff;
    border-left: 3px solid #3b82f6;
}
```

### 4. 添加了调试日志
- 点击侧边栏项时会输出日志
- 数据加载时会输出日志
- 可以在浏览器控制台查看

## 如何测试

### 1. 启动服务

```bash
# 启动API服务器
cd /root/sharedata3/ai-sns-el
python api_server.py
```

在另一个终端：
```bash
# 启动Electron应用
npm start
# 或
electron electron/main.js
```

### 2. 打开工具页面

1. 打开Electron应用
2. 点击左侧导航栏的 "Tools" 图标（扳手图标）
3. 页面应该显示Tools Management界面

### 3. 测试侧边栏点击

点击侧边栏的4个选项：
1. **Tools Plugin** - 应该切换到插件列表
2. **MCP** - 应该切换到MCP列表
3. **Function** - 应该切换到函数列表
4. **Computer Use** - 应该切换到计算机使用工具列表

**期望结果**：
- 点击后，该项会高亮显示（蓝色背景，左边蓝色边框）
- 主内容区会显示 "Loading tools..." 然后显示工具列表或 "No Tools Found"
- 顶部标签页也会相应切换

### 4. 查看控制台日志

打开浏览器控制台（F12），应该看到类似的日志：

```
Tools Manager initialized with API: http://127.0.0.1:8788
Loading tools data for tab: plugins
Switching to tab: mcp
Loading tools data for tab: mcp
Loaded items: []
Tab switched successfully
```

### 5. 测试标签页点击

点击主内容区顶部的4个标签：
1. **Tools Plugin**
2. **MCP**
3. **Function**
4. **Computer Use**

这些标签也应该能切换内容。

## 调试步骤

如果仍然没有反应：

### 1. 检查API服务器

```bash
# 测试API是否运行
curl http://127.0.0.1:8788/health

# 应该返回：
# {"status":"healthy","version":"2.0.0","architecture":"modular"}

# 测试Tools API
curl http://127.0.0.1:8788/api/tools/plugins
```

### 2. 检查浏览器控制台

打开控制台（F12），查看：
- 是否有JavaScript错误
- 是否有网络请求失败
- 是否有我们的调试日志

### 3. 检查网络请求

在控制台的 Network 标签中：
- 查看是否有对 `/api/tools/plugins` 等的请求
- 查看请求的响应状态
- 查看响应内容

### 4. 手动测试API

在浏览器控制台中运行：

```javascript
// 测试ToolsManager
const manager = new ToolsManager();

// 测试获取插件
manager.getAllPlugins().then(plugins => {
    console.log('Plugins:', plugins);
});

// 测试获取MCP
manager.getAllMCPs().then(mcps => {
    console.log('MCPs:', mcps);
});
```

## 常见问题

### Q1: 点击后没有任何反应

**解决方案**：
1. 打开控制台查看是否有错误
2. 确认tools-manager.js已加载
3. 确认API服务器正在运行

### Q2: 显示 "Error Loading Tools"

**解决方案**：
1. 检查API服务器是否运行
2. 检查控制台错误信息
3. 检查网络请求是否成功

### Q3: 显示 "Loading tools..." 一直不变

**解决方案**：
1. API请求可能超时
2. 检查网络连接
3. 查看控制台是否有CORS错误

### Q4: 侧边栏点击有反应但内容不变

**解决方案**：
1. 检查 `toolsContentArea` 元素是否存在
2. 查看控制台日志中的 "Loaded items"
3. 确认数据加载成功

## 创建测试数据

使用API创建一些测试数据：

```bash
# 创建一个测试插件
curl -X POST http://127.0.0.1:8788/api/tools/plugins \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Weather Plugin",
    "description": "A test plugin for weather",
    "plugin_type": "weather",
    "instruction": "Use this to get weather data"
  }'

# 创建一个测试MCP
curl -X POST http://127.0.0.1:8788/api/tools/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test MCP Server",
    "description": "A test MCP server",
    "mcp_type": "stdio"
  }'

# 创建一个测试函数
curl -X POST http://127.0.0.1:8788/api/tools/functions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_function",
    "description": "A test function",
    "function_type": "python"
  }'

# 创建一个测试技能
curl -X POST http://127.0.0.1:8788/api/tools/skills \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_skill",
    "description": "A test computer use skill",
    "skill_type": "computer_use"
  }'
```

创建后，刷新页面，应该能看到这些工具。

## 成功标志

功能正常工作时，您应该看到：

1. ✅ 侧边栏项可以点击
2. ✅ 点击后该项高亮显示（蓝色背景）
3. ✅ 主内容区显示加载状态
4. ✅ 主内容区显示工具列表或空状态
5. ✅ 控制台有调试日志
6. ✅ 网络请求成功（200状态）
7. ✅ 顶部标签页也能切换

## 需要帮助？

如果问题仍然存在，请提供：
1. 浏览器控制台的完整输出
2. 网络请求的详细信息
3. API服务器的日志输出
4. 具体的错误信息

这样我可以更好地帮您诊断问题。
