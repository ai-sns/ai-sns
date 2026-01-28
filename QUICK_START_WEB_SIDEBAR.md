# Web Sidebar 功能快速启动指南

## 🚀 快速开始

### 1. 启动后端服务器

```bash
# Windows
python api_server.py

# Linux/Mac
python3 api_server.py
```

确保服务器运行在 `http://localhost:8788`

### 2. 启动前端应用

```bash
# 如果使用 Electron
npm start

# 或者直接运行主程序
python Application.py
```

### 3. 测试功能

打开应用后，进入 **Web** 页面，你会看到两个区域：
- **LLM Online** - LLM 服务列表
- **AI Tools Online** - AI 工具列表

## 📋 功能测试清单

### ✅ 搜索功能

**LLM 搜索**:
1. 在 "LLM Online" 区域找到搜索框
2. 输入关键词（例如：GPT、Claude）
3. 观察列表实时过滤
4. 清空搜索框，列表恢复显示所有项目

**Tool 搜索**:
1. 在 "AI Tools Online" 区域找到搜索框
2. 输入关键词
3. 观察列表实时过滤

### ✅ 管理功能

**打开管理对话框**:
1. 点击 "Manage" 按钮
2. 看到所有项目的列表
3. 每个项目显示：
   - 拖拽手柄（六点图标）
   - 图标
   - 名称和 URL
   - 编辑按钮（铅笔图标）
   - 删除按钮（垃圾桶图标）

### ✅ 编辑功能

1. 在管理对话框中点击编辑按钮
2. 填写/修改表单：
   - **Name** (必填): 服务名称
   - **Title**: 显示标题
   - **URL** (必填): 服务地址
   - **Description**: 描述信息
   - **Icon Filename**: 图标文件名
3. 点击 "Save" 保存
4. 观察列表自动更新

### ✅ 删除功能

1. 在管理对话框中点击删除按钮
2. 在确认对话框中点击 "确定"
3. 观察项目从列表中移除
4. 侧边栏也同步更新

### ✅ 拖拽排序功能

1. 在管理对话框中，按住项目左侧的拖拽手柄
2. 拖动到新位置
3. 释放鼠标
4. 观察位置立即更新
5. 关闭对话框，侧边栏顺序也已更新
6. 刷新页面，顺序保持不变（已保存到数据库）

## 🧪 API 测试

### 使用 Python 脚本测试

```bash
python test_web_sidebar_api.py
```

这个脚本会自动测试所有 API 端点：
- ✅ 获取数据
- ✅ 创建项目
- ✅ 更新项目
- ✅ 重排序
- ✅ 删除项目

### 使用 curl 测试

**获取所有项目**:
```bash
curl http://localhost:8788/api/system/web-mng
```

**创建新项目**:
```bash
curl -X POST http://localhost:8788/api/system/web-mng \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test LLM",
    "url": "https://test.com",
    "type": "LLM",
    "description": "Test description"
  }'
```

**更新项目**:
```bash
curl -X PUT http://localhost:8788/api/system/web-mng/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "description": "Updated description"
  }'
```

**删除项目**:
```bash
curl -X DELETE http://localhost:8788/api/system/web-mng/1
```

**重排序**:
```bash
curl -X PUT http://localhost:8788/api/system/web-mng/reorder \
  -H "Content-Type: application/json" \
  -d '[
    {"id": 1, "position": 0},
    {"id": 2, "position": 1},
    {"id": 3, "position": 2}
  ]'
```

## 🎨 界面预览

### 侧边栏
```
┌─────────────────────────┐
│  🌐 LLM Online      ▼   │
├─────────────────────────┤
│  🔍 Search...           │
│  [Add]  [Manage]        │
│                         │
│  [GPT]  [Claude]  [...]│
└─────────────────────────┘
```

### 管理对话框
```
┌──────────────────────────────┐
│  Manage LLM Services      ✕  │
├──────────────────────────────┤
│  ⋮⋮ [Icon] GPT-4            │
│           https://...        │
│           [✏️] [🗑️]          │
│                              │
│  ⋮⋮ [Icon] Claude            │
│           https://...        │
│           [✏️] [🗑️]          │
└──────────────────────────────┘
```

### 编辑对话框
```
┌──────────────────────────────┐
│  Edit LLM                 ✕  │
├──────────────────────────────┤
│  Name *                      │
│  [GPT-4                   ]  │
│                              │
│  Title                       │
│  [OpenAI GPT-4            ]  │
│                              │
│  URL *                       │
│  [https://chat.openai.com ]  │
│                              │
│  Description                 │
│  [Advanced AI model...    ]  │
│                              │
│  Icon Filename               │
│  [gpt4.png                ]  │
├──────────────────────────────┤
│         [Cancel]  [Save]     │
└──────────────────────────────┘
```

## 🐛 故障排除

### 问题 1: 搜索不工作
**解决方案**: 
- 检查浏览器控制台是否有错误
- 确认 WebSidebar.js 已正确加载
- 检查搜索框的 ID 是否正确

### 问题 2: 编辑/删除按钮无响应
**解决方案**:
- 检查后端服务器是否运行
- 检查 API 端点是否可访问
- 查看浏览器控制台的网络请求

### 问题 3: 拖拽不工作
**解决方案**:
- 确认浏览器支持 HTML5 拖拽 API
- 检查 CSS 中的 `draggable` 属性
- 查看控制台是否有 JavaScript 错误

### 问题 4: 位置更新不保存
**解决方案**:
- 检查数据库中是否有 `position` 字段
- 确认后端 API `/web-mng/reorder` 正常工作
- 查看后端日志

## 📚 相关文档

- `WEB_SIDEBAR_IMPLEMENTATION_SUMMARY.md` - 完整实现总结
- `TEST_WEB_SIDEBAR_FEATURES.md` - 详细测试指南
- `test_web_sidebar_frontend.html` - 可视化测试页面

## 💡 提示

1. **搜索技巧**: 搜索支持部分匹配，不区分大小写
2. **拖拽技巧**: 按住拖拽手柄（六点图标）而不是整个项目
3. **编辑技巧**: Name 和 URL 是必填字段
4. **删除技巧**: 删除是软删除，可以在数据库中恢复

## 🎯 下一步

完成测试后，你可以：
1. 添加更多 LLM 服务和工具
2. 自定义图标（放在 `resource/images/` 目录）
3. 调整样式（修改 `renderer/css/web.css`）
4. 扩展功能（参考实现总结文档）

## ✨ 功能亮点

- 🔍 **实时搜索** - 无延迟，即时响应
- ✏️ **快速编辑** - 简洁的表单，清晰的验证
- 🗑️ **安全删除** - 确认对话框，软删除机制
- 🔄 **流畅拖拽** - 平滑动画，即时保存
- 🎨 **优雅界面** - 现代设计，响应式布局

---

**祝你使用愉快！** 🎉

如有问题，请查看详细文档或联系开发团队。
