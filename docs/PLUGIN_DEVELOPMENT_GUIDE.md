# Agent 插件开发规范

本文档描述了如何为 AI-SNS Agent 模块开发自定义插件。

## 目录

1. [插件架构](#插件架构)
2. [插件结构](#插件结构)
3. [开发指南](#开发指南)
4. [API参考](#api参考)
5. [最佳实践](#最佳实践)
6. [示例插件](#示例插件)

## 插件架构

Agent 插件系统采用模块化设计，允许开发者创建可动态加载的功能扩展。插件可以：

- 处理和转换聊天消息
- 渲染自定义可视化内容
- 添加新的交互功能
- 扩展 AI 的输出格式

## 插件结构

### 基本结构

每个插件应该是一个独立的 JavaScript 模块，遵循以下结构：

```javascript
const YourPlugin = {
    /**
     * 插件元信息
     */
    info: {
        id: 'your-plugin-id',              // 唯一标识符
        name: '插件名称',                   // 显示名称
        version: '1.0.0',                  // 版本号
        description: '插件功能描述'         // 简短描述
    },

    /**
     * 初始化插件（可选）
     */
    init() {
        // 初始化逻辑
    },

    /**
     * 渲染插件内容到消息中
     * @param {HTMLElement} messageBody - 消息体DOM元素
     * @returns {boolean} - 是否成功渲染
     */
    renderInMessage(messageBody) {
        // 检测和渲染逻辑
        return true; // 或 false
    },

    /**
     * 清理插件资源（可选）
     */
    destroy() {
        // 清理逻辑
    }
};

// 导出插件
if (typeof window !== 'undefined') {
    window.YourPlugin = YourPlugin;
}

export default YourPlugin;
```

### 文件组织

建议的文件结构：

```
renderer/js/plugins/
├── yourPlugin.js           # 插件主文件
├── yourPlugin.css          # 插件样式（可选）
└── yourPlugin/             # 插件资源目录（可选）
    ├── utils.js            # 工具函数
    ├── renderer.js         # 渲染逻辑
    └── assets/             # 资源文件
```

## 开发指南

### 步骤 1: 创建插件文件

在 `renderer/js/plugins/` 目录下创建新的 JavaScript 文件：

```javascript
// renderer/js/plugins/myPlugin.js
const MyPlugin = {
    info: {
        id: 'my-plugin',
        name: '我的插件',
        version: '1.0.0',
        description: '这是一个示例插件'
    },

    renderInMessage(messageBody) {
        // 实现你的渲染逻辑
        return false;
    }
};

if (typeof window !== 'undefined') {
    window.MyPlugin = MyPlugin;
}

export default MyPlugin;
```

### 步骤 2: 注册插件

在 `renderer/index.html` 中引入插件：

```html
<!-- 插件系统 -->
<script type="module" src="js/plugins/myPlugin.js"></script>
```

### 步骤 3: 在插件配置中添加

在 `renderer/js/modules/agent/agentHandlers.js` 的 `initPluginEvents` 方法中添加插件配置：

```javascript
const pluginConfigs = {
    'my-plugin': {
        name: '我的插件',
        description: '这是一个示例插件'
    },
    // ...其他插件
};
```

### 步骤 4: 实现加载逻辑

在 `loadPluginContent` 方法中添加插件加载逻辑：

```javascript
loadPluginContent(pluginId) {
    const container = document.getElementById(`plugin-${pluginId}`);
    if (!container) return;

    switch (pluginId) {
        case 'my-plugin':
            this.loadMyPlugin(container);
            break;
        // ...其他插件
    }
}
```

## API 参考

### 插件接口

#### info (必需)

插件元信息对象。

```javascript
info: {
    id: string,          // 唯一标识符，使用小写字母和连字符
    name: string,        // 用户可见的插件名称
    version: string,     // 语义化版本号 (x.y.z)
    description: string  // 插件功能的简短描述
}
```

#### renderInMessage(messageBody)

在消息体中渲染插件内容的主方法。

**参数:**
- `messageBody` (HTMLElement): 消息体的 DOM 元素

**返回值:**
- `boolean`: 如果成功渲染返回 `true`，否则返回 `false`

**示例:**
```javascript
renderInMessage(messageBody) {
    // 检测特定模式
    const pattern = /```your-syntax\s*([\s\S]*?)\s*```/g;
    const matches = messageBody.innerHTML.match(pattern);

    if (!matches) return false;

    // 渲染内容
    matches.forEach(match => {
        // 你的渲染逻辑
    });

    return true;
}
```

#### init() (可选)

插件初始化方法，在插件加载时调用。

```javascript
init() {
    // 设置事件监听器
    // 加载外部资源
    // 初始化状态
}
```

#### destroy() (可选)

插件清理方法，在插件卸载时调用。

```javascript
destroy() {
    // 移除事件监听器
    // 清理资源
    // 重置状态
}
```

### 工具方法

插件可以访问以下全局工具：

- `agentHandlers`: Agent 处理器对象
- `Modal`: 模态框组件
- `Notification`: 通知组件
- `agentState`: Agent 状态管理

## 最佳实践

### 1. 命名规范

- **插件ID**: 使用小写字母和连字符，例如 `mindmap-plugin`
- **类名**: 使用驼峰命名法，例如 `MindmapPlugin`
- **CSS类名**: 使用插件ID作为前缀，例如 `.mindmap-container`

### 2. 错误处理

始终使用 try-catch 包装可能失败的操作：

```javascript
renderInMessage(messageBody) {
    try {
        // 你的逻辑
        return true;
    } catch (error) {
        console.error('插件渲染失败:', error);
        return false;
    }
}
```

### 3. 性能优化

- 避免在渲染过程中进行同步的重量级操作
- 使用 DocumentFragment 批量操作 DOM
- 对复杂计算使用 Web Workers
- 实现懒加载和按需渲染

### 4. 样式隔离

使用唯一的CSS类名前缀避免样式冲突：

```javascript
container.className = `${this.info.id}-container`;
```

### 5. 可访问性

确保插件内容对辅助技术友好：

```javascript
// 添加 ARIA 属性
element.setAttribute('role', 'region');
element.setAttribute('aria-label', '思维导图');
```

### 6. 响应式设计

确保插件内容在不同屏幕尺寸下正常显示：

```css
.my-plugin-container {
    max-width: 100%;
    overflow-x: auto;
}
```

## 示例插件

### 思维导图插件

完整的思维导图插件示例可以在 `renderer/js/plugins/mindmapPlugin.js` 中找到。

主要特点：
- 解析 Markdown mindmap 语法
- 使用 SVG 渲染可视化思维导图
- 支持节点点击和交互
- 自适应布局

### 图表插件（示例）

```javascript
const ChartPlugin = {
    info: {
        id: 'chart',
        name: '图表插件',
        version: '1.0.0',
        description: '将数据可视化为图表'
    },

    detectChart(content) {
        const chartRegex = /```chart\s*([\s\S]*?)\s*```/g;
        return content.match(chartRegex);
    },

    parseChartData(content) {
        // 解析图表数据
        return JSON.parse(content);
    },

    renderChart(data, container) {
        // 使用图表库（如 Chart.js）渲染图表
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);

        // 渲染逻辑...
    },

    renderInMessage(messageBody) {
        const charts = this.detectChart(messageBody.innerHTML);

        if (!charts) return false;

        charts.forEach(chart => {
            try {
                const data = this.parseChartData(chart);
                const container = document.createElement('div');
                container.className = 'chart-container';

                this.renderChart(data, container);

                // 替换原始内容
                messageBody.innerHTML = messageBody.innerHTML.replace(
                    chart,
                    container.outerHTML
                );
            } catch (error) {
                console.error('渲染图表失败:', error);
            }
        });

        return true;
    }
};

export default ChartPlugin;
```

## 调试技巧

### 1. 使用 console.log

在关键位置添加日志输出：

```javascript
renderInMessage(messageBody) {
    console.log('[MyPlugin] 开始渲染');
    console.log('[MyPlugin] 消息内容:', messageBody.innerHTML);
    // ...
}
```

### 2. 开发者工具

使用浏览器开发者工具：
- **Elements**: 检查生成的 DOM 结构
- **Console**: 查看错误和日志
- **Network**: 监控资源加载
- **Performance**: 分析性能瓶颈

### 3. 单元测试

为插件编写测试：

```javascript
// test/plugins/myPlugin.test.js
describe('MyPlugin', () => {
    it('should detect pattern', () => {
        const content = '```my-syntax\ntest\n```';
        const result = MyPlugin.detectPattern(content);
        expect(result).toBeTruthy();
    });
});
```

## 发布插件

### 1. 文档

创建 README.md 文件描述：
- 插件功能
- 安装步骤
- 使用示例
- 配置选项

### 2. 版本控制

遵循语义化版本规范：
- **主版本号**: 不兼容的 API 更改
- **次版本号**: 向后兼容的功能增加
- **修订号**: 向后兼容的问题修正

### 3. 许可证

添加合适的开源许可证（如 MIT, Apache 2.0）。

## 获取帮助

如果在开发插件时遇到问题：

1. 查看现有插件示例
2. 阅读 Agent 模块源码
3. 在项目仓库提交 Issue
4. 加入开发者社区讨论

---

**最后更新**: 2026-01-11
**文档版本**: 1.0.0
