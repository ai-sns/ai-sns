# 前端栏目切换状态保持修复说明

## 问题描述

之前在切换栏目（sns、agent、km、tools、web、home）时，每次都会重新加载内容，导致：
- 侧边栏状态丢失（如agent列表、选中项等）
- 主内容区部分状态丢失
- 用户体验不佳

## 根本原因

在 `renderer/js/core/router.js` 的 `renderSidebar` 方法中，每次切换都执行：
```javascript
sidebar.innerHTML = sidebarContent;  // 完全销毁并重新创建DOM
```

而主内容区已经正确实现了状态保持（通过隐藏/显示），但侧边栏没有。

## 解决方案

采用**容器复用 + 显示/隐藏**策略：

### 1. 修改 `router.js` 的 `renderSidebar` 方法

**修改前：** 每次都重新设置 `innerHTML`
**修改后：**
- 为每个页面创建独立的侧边栏容器（`sidebar-{page}`）
- 首次访问：创建容器并渲染内容
- 再次访问：只是移除 `hidden` 类显示容器
- 切换页面：隐藏旧容器，显示新容器

**核心代码：**
```javascript
async renderSidebar(page) {
    const sidebarContainer = document.getElementById('secondarySidebar');

    // 隐藏所有侧边栏容器
    const allSidebars = sidebarContainer.querySelectorAll('.sidebar-page-container');
    allSidebars.forEach(sb => sb.classList.add('hidden'));

    // 检查该页面的侧边栏容器是否已存在
    let pageSidebar = sidebarContainer.querySelector(`#sidebar-${page}`);

    if (!pageSidebar) {
        // 首次渲染：创建新容器
        pageSidebar = document.createElement('div');
        pageSidebar.id = `sidebar-${page}`;
        pageSidebar.className = 'sidebar-page-container';
        pageSidebar.innerHTML = module.renderSidebar();
        sidebarContainer.appendChild(pageSidebar);

        // Agent页面需要特殊初始化
        if (page === 'agent') {
            await window.AgentSidebar.init();
        }
    } else {
        // 已存在：直接显示（保持状态）
        pageSidebar.classList.remove('hidden');
    }
}
```

### 2. 添加CSS样式

在 `renderer/css/main.css` 中添加：
```css
.sidebar-page-container {
    width: 100%;
    height: 100%;
    display: block;
    overflow: hidden;
}

.sidebar-page-container.hidden {
    display: none !important;
}
```

### 3. 清理不必要的代码

移除了 Router 类中的特殊状态跟踪变量：
- `agentSidebarInitialized`
- `agentPageInitialized`

简化了主内容区的渲染逻辑。

## 修改文件列表

1. ✅ `renderer/js/core/router.js` - 路由系统核心修改
   - 侧边栏容器复用逻辑
   - 移除destroy调用（保持模块状态）
   - Agent页面状态恢复逻辑
2. ✅ `renderer/css/main.css` - 添加侧边栏容器样式

## 测试步骤

### 基础测试

1. **启动应用**
   ```bash
   npm run start:electron
   ```

2. **测试Agent页面状态保持**
   - 点击左侧导航栏 "Agent"
   - 在侧边栏选择一个agent（如果有的话）
   - 在聊天框输入一些文字（不要发送）
   - 切换到其他栏目（如 SNS）
   - 再切换回 Agent
   - ✅ 验证：侧边栏选中的agent应该保持，聊天框内容应该保持

3. **测试SNS页面状态保持**
   - 点击左侧导航栏 "SNS"
   - 在侧边栏进行一些操作（如展开/折叠某些项）
   - 切换到其他栏目
   - 再切换回 SNS
   - ✅ 验证：侧边栏状态应该保持

4. **测试所有栏目**
   按以下顺序切换并验证：
   - SNS → Agent → KM → Tools → Web → Home
   - Home → Web → Tools → KM → Agent → SNS
   - ✅ 验证：每次切换回已访问过的页面，状态都应该保持

### 性能测试

5. **快速连续切换**
   - 快速点击各个栏目图标（每秒1-2次）
   - ✅ 验证：切换应该流畅，不应该有卡顿
   - ✅ 验证：控制台没有错误

6. **内存检查**
   - 打开浏览器开发者工具
   - 切换所有栏目一遍
   - 再次切换所有栏目
   - ✅ 验证：控制台日志显示 "侧边栏恢复显示（保持状态）" 而不是 "侧边栏首次渲染"

### 边界测试

7. **首次访问**
   - 清除缓存或重启应用
   - 第一次访问每个栏目
   - ✅ 验证：控制台日志显示 "侧边栏首次渲染"
   - ✅ 验证：侧边栏内容正确显示

8. **错误处理**
   - 检查是否有模块加载失败的情况
   - ✅ 验证：即使某个模块失败，应显示友好的错误提示

## 预期控制台日志

**首次访问 Agent：**
```
[Router] 侧边栏首次渲染: agent
[Router] 初始化Agent侧边栏...
```

**再次访问 Agent：**
```
[Router] 侧边栏恢复显示（保持状态）: agent
[Router] 页面恢复显示（保持状态）: agent
```

## 优势

1. ✅ **状态保持** - 所有页面的侧边栏和主内容区状态完全保持
2. ✅ **性能优化** - 避免重复渲染，只在首次访问时创建DOM
3. ✅ **统一策略** - 侧边栏和主内容区使用相同的状态管理策略
4. ✅ **代码简化** - 移除了特殊处理逻辑，代码更清晰
5. ✅ **易于维护** - 所有模块都遵循相同的生命周期

## 技术原理

采用**单页应用(SPA)标准模式**：
- 所有页面DOM在首次访问时创建并保留在内存中
- 切换时通过CSS的 `display: none/block` 控制显示
- 每个模块的 `init()` 方法只在首次渲染时调用一次
- 所有事件监听器、状态数据都保留在DOM中

## 关键修复：Agent状态保持

### 问题2：Agent选中状态丢失

**现象：** 从其他栏目切换回agent栏目后，发送消息提示"请先选择一个Agent"

**原因：**
1. 切换页面时调用 `module.destroy()`
2. Agent模块的destroy会调用 `agentState.reset()`
3. 重置后 `agentState.agents` 数组和 `currentAgentId` 都被清空
4. 发送消息时 `getCurrentAgent()` 返回null

**解决方案：**

1. **移除destroy调用** (`router.js:44-53`)
   ```javascript
   // 隐藏当前页面（保持状态，不调用destroy）
   if (this.currentPage) {
       const currentPageElement = document.getElementById(`page-${this.currentPage}`);
       if (currentPageElement) {
           currentPageElement.classList.add('hidden');
       }
       // 不再调用 destroy() 方法，以保持模块状态
   }
   ```

2. **添加状态恢复逻辑** (`router.js:116-139`)
   ```javascript
   // 特殊处理：Agent页面恢复时，确保UI状态与agentState同步
   if (page === 'agent' && window.agentState && window.AgentSidebar) {
       const currentAgentId = window.agentState.currentAgentId;
       if (currentAgentId) {
           // 恢复UI的选中状态和展开状态
           setTimeout(() => {
               document.querySelectorAll('.agent-item').forEach(item => {
                   item.classList.remove('active');
               });
               const currentAgentItem = document.querySelector(`.agent-item[data-agent-id="${currentAgentId}"]`);
               if (currentAgentItem) {
                   currentAgentItem.classList.add('active');
               }
               const currentAgentSection = document.querySelector(`.agent-section-container[data-agent-id="${currentAgentId}"]`);
               if (currentAgentSection) {
                   currentAgentSection.style.display = 'block';
               }
           }, 50);
       }
   }
   ```

## 注意事项

1. **不再调用destroy** - 模块的 `destroy()` 方法现在只在应用退出时调用，不在页面切换时调用

2. 如果某个页面需要在每次访问时刷新数据，应该：
   - 监听 `page:changed` 事件
   - 在事件处理器中更新数据
   - 不要在 `init()` 中获取数据

3. 如果需要强制重新加载某个页面：
   ```javascript
   const pageElement = document.getElementById('page-agent');
   const sidebarElement = document.getElementById('sidebar-agent');
   if (pageElement) pageElement.remove();
   if (sidebarElement) sidebarElement.remove();
   router.navigateTo('agent');
   ```

4. **Agent状态管理** - `agentState` 现在在整个应用生命周期中保持，包含：
   - `currentAgentId` - 当前选中的agent
   - `agents` - 所有agent列表
   - `agentStates` - 每个agent的独立状态（聊天历史、配置等）

## 兼容性

- ✅ 完全向后兼容现有模块
- ✅ 不影响旧版 `app.js` 的导航逻辑（如果有使用的话）
- ✅ 所有现有事件监听器继续工作

---

**修复日期：** 2026-01-16
**修复人：** Claude Code
**版本：** 1.0.0
