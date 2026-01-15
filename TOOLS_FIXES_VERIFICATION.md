# Tools Module - Fixes Verification Guide

## 修复内容总结

### Issue 1: 侧边栏点击无响应
**问题**: 侧边栏4个模块点击后界面没有任何反应

**修复内容**:
1. ✅ 在 `renderer/js/pages.js` 中添加了事件绑定 `bindToolsEvents()`
2. ✅ 为侧边栏项目添加了 `data-tab` 属性
3. ✅ 添加了active状态切换逻辑
4. ✅ 在 `renderer/css/tools.css` 中添加了hover和active样式
5. ✅ 添加了控制台调试日志

### Issue 2: get_db() 错误
**问题**: 出现 `get_db` 函数不存在的错误

**修复内容**:
1. ✅ 重构 `backend/modules/tools/service.py`:
   - 移除了 `__init__(self, db: Session)` 中的db参数
   - 添加了 `_get_db()` 方法来创建数据库会话
   - 所有CRUD方法现在自行管理数据库会话的生命周期

2. ✅ 简化 `backend/modules/tools/router.py`:
   - 移除了对不存在的 `get_db` 的导入
   - 简化了 `get_tools_service()` 函数

3. ✅ 简化 `backend/modules/tools/dependencies.py`:
   - 移除了数据库会话依赖
   - 服务现在自行管理会话

## 修改的文件列表

### 后端文件 (3个)
1. `backend/modules/tools/service.py` - 主要修改
2. `backend/modules/tools/router.py` - 移除无效导入
3. `backend/modules/tools/dependencies.py` - 简化依赖

### 前端文件 (2个)
1. `renderer/js/pages.js` - 添加事件绑定和调试日志
2. `renderer/css/tools.css` - 添加交互样式

## 测试步骤

### 1. 停止现有服务

如果服务正在运行，请先停止它们：

```bash
# 按 Ctrl+C 停止 API 服务器
# 关闭 Electron 应用窗口
```

### 2. 启动 API 服务器

```bash
cd /root/sharedata3/ai-sns-el
python api_server.py
```

**期望输出**:
```
DBPath /root/sharedata3/ai-sns-el/db/db.sqlite
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8788 (Press CTRL+C to quit)
```

如果看到任何错误，请立即报告。

### 3. 测试 API 端点

在另一个终端中测试API是否正常工作：

```bash
# 测试健康检查
curl http://127.0.0.1:8788/health

# 测试 Tools API - Plugins
curl http://127.0.0.1:8788/api/tools/plugins

# 测试 Tools API - MCP
curl http://127.0.0.1:8788/api/tools/mcp

# 测试 Tools API - Functions
curl http://127.0.0.1:8788/api/tools/functions

# 测试 Tools API - Skills
curl http://127.0.0.1:8788/api/tools/skills
```

**期望结果**:
- 所有请求都应该返回 200 状态码
- 返回空列表 `[]` 或包含数据的列表
- **不应该有任何错误**

### 4. 启动 Electron 应用

```bash
cd /root/sharedata3/ai-sns-el
npm start
# 或者
electron electron/main.js
```

### 5. 测试侧边栏点击功能

1. **打开Tools页面**:
   - 点击左侧导航栏的 "Tools" 图标（扳手图标）

2. **打开浏览器开发者工具**:
   - 按 F12 或 Ctrl+Shift+I
   - 切换到 Console 标签

3. **测试侧边栏点击**:
   依次点击侧边栏的4个选项：

   a. **Tools Plugin**
   - ✅ 该项应该高亮显示（蓝色背景，左边蓝色边框）
   - ✅ 控制台应该显示: `Switching to tab: plugins`
   - ✅ 主内容区应该显示 "Loading tools..." 然后显示插件列表或空状态

   b. **MCP**
   - ✅ 该项应该高亮显示
   - ✅ 控制台应该显示: `Switching to tab: mcp`
   - ✅ 主内容区应该切换到MCP列表

   c. **Function**
   - ✅ 该项应该高亮显示
   - ✅ 控制台应该显示: `Switching to tab: functions`
   - ✅ 主内容区应该切换到函数列表

   d. **Computer Use**
   - ✅ 该项应该高亮显示
   - ✅ 控制台应该显示: `Switching to tab: skills`
   - ✅ 主内容区应该切换到技能列表

### 6. 检查控制台输出

在浏览器控制台中，你应该看到类似这样的日志：

```
Tools Manager initialized with API: http://127.0.0.1:8788
Loading tools data for tab: plugins
Loaded items: []
Switching to tab: mcp
Loading tools data for tab: mcp
Loaded items: []
Tab switched successfully
```

### 7. 测试顶部标签页

点击主内容区顶部的4个标签，确认它们也能正常工作。

### 8. 创建测试数据（可选）

如果想看到实际的工具卡片，可以创建一些测试数据：

```bash
# 创建测试插件
curl -X POST http://127.0.0.1:8788/api/tools/plugins \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试天气插件",
    "description": "用于获取天气信息的测试插件",
    "plugin_type": "weather",
    "instruction": "使用此插件获取指定城市的天气数据"
  }'

# 创建测试MCP
curl -X POST http://127.0.0.1:8788/api/tools/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试MCP服务器",
    "description": "一个测试用的MCP服务器",
    "mcp_type": "stdio"
  }'

# 创建测试函数
curl -X POST http://127.0.0.1:8788/api/tools/functions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_function",
    "description": "一个测试函数",
    "function_type": "python"
  }'

# 创建测试技能
curl -X POST http://127.0.0.1:8788/api/tools/skills \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_skill",
    "description": "一个测试计算机使用技能",
    "skill_type": "computer_use"
  }'
```

创建后，刷新Electron应用（Ctrl+R），你应该能看到这些工具卡片。

## 成功标志

如果所有修复都成功，你应该看到：

### 后端成功标志
- ✅ API服务器启动无错误
- ✅ 所有API端点返回200状态码
- ✅ 无 `get_db` 相关错误
- ✅ 数据库操作正常工作

### 前端成功标志
- ✅ 侧边栏项可以点击
- ✅ 点击后该项高亮显示（蓝色背景，左边蓝色边框）
- ✅ 鼠标悬停时有视觉反馈（浅灰色背景，轻微右移）
- ✅ 主内容区正确切换
- ✅ 控制台有调试日志输出
- ✅ 无JavaScript错误

## 故障排除

### 如果仍然看到 get_db 错误

1. 确认你已经重启了API服务器
2. 检查是否有Python缓存文件干扰：
   ```bash
   find backend/modules/tools -name "*.pyc" -delete
   find backend/modules/tools -name "__pycache__" -type d -exec rm -rf {} +
   ```
3. 重新启动服务器

### 如果侧边栏仍然无响应

1. 打开浏览器控制台检查JavaScript错误
2. 确认 `renderer/js/pages.js` 已经保存
3. 清除缓存并刷新：Ctrl+Shift+R
4. 检查 `tools-manager.js` 是否已加载：
   ```javascript
   // 在控制台中运行
   typeof ToolsManager
   // 应该返回 "function"
   ```

### 如果看到网络错误

1. 确认API服务器正在运行
2. 测试连接：
   ```bash
   curl http://127.0.0.1:8788/health
   ```
3. 检查防火墙设置

### 如果数据不显示

1. 检查API响应：
   ```bash
   curl -v http://127.0.0.1:8788/api/tools/plugins
   ```
2. 查看浏览器Network标签的请求详情
3. 检查API服务器日志

## 报告问题

如果问题仍然存在，请提供以下信息：

1. **API服务器日志**:
   - 服务器启动时的完整输出
   - 任何错误信息

2. **浏览器控制台输出**:
   - Console标签的完整输出
   - 任何错误或警告

3. **网络请求详情**:
   - Network标签中的请求状态
   - 响应内容

4. **具体步骤**:
   - 你做了什么操作
   - 期望看到什么
   - 实际看到了什么

## 技术细节

### 数据库会话管理

之前的实现尝试使用FastAPI的依赖注入来传递数据库会话，但这与项目现有的模式不一致。

**旧模式** (有问题):
```python
def get_tools_service(db: Session = Depends(get_db)):
    return ToolsService(db)
```

**新模式** (正确):
```python
def get_tools_service():
    return ToolsService()  # Service内部管理会话
```

每个服务方法现在都遵循这个模式：
```python
def get_all_plugins(self):
    db = self._get_db()  # 创建会话
    try:
        # 数据库操作
        return results
    finally:
        db.close()  # 确保关闭
```

### 前端事件绑定

侧边栏点击通过以下方式工作：

1. HTML中的 `data-tab` 属性标识要切换到哪个标签
2. JavaScript事件监听器捕获点击
3. 从 `data-tab` 读取标签名称
4. 调用 `switchToolTab()` 切换内容
5. 更新active类以显示视觉反馈

## 下一步

修复验证通过后，可以考虑：

1. 添加工具编辑功能的完整UI
2. 实现搜索和过滤
3. 添加批量操作
4. 改进错误提示
5. 添加工具导入/导出功能

---

**修复日期**: 2026-01-14
**版本**: 1.0.1
**状态**: ✅ 所有已知问题已修复
