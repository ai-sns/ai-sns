# 地图功能迁移计划

## 概述
将 `/mnt/c/dev/agi-ev/ai-sns/ai-sns/MessageBoxEarth.py`、`/mnt/c/dev/agi-ev/ai-sns/ai-sns/ui/ui_MessageWidgetEarth.py` 和 `/mnt/c/dev/agi-ev/ai-sns/ai-sns/scripts/map.html` 的功能迁移到当前项目，使用 Electron 前端 + api_server 后端 + http://localhost:8788/scripts/map.html 实现。

## 架构对比

### 原架构
- **前端**：PyQt6 + QWebEngineView + map.html
- **后端**：Python（MessageBoxEarth.py）
- **通信**：QWebChannel（Python ↔ JavaScript）

### 新架构
- **前端**：Electron + 渲染进程 + map.html
- **后端**：FastAPI（api_server.py）
- **通信**：Electron IPC + HTTP API + WebSocket

## 核心功能分析

### 1. 地图可视化（map.html）
- **地图引擎**：百度地图 API v1.0（WebGL 版本）+ Google 地图（可选）
- **3D 渲染**：Three.js + GLTF 模型加载
- **地图操作**：缩放、平移、旋转、地图类型切换
- **标记系统**：聚类标记、自定义标记、信息窗口
- **路径规划**：路线查询、导航、轨迹模拟

### 2. 聊天功能
- 地图上的聊天气泡
- 消息历史记录
- 实时聊天

### 3. AI 代理交互
- Agent 类集成
- 任务管理（MapTaskManager、JsTaskManager）
- 聊天回复生成

### 4. 地图标记和路径
- 地图标记管理
- 路径规划和导航
- 3D 模型展示和动画

### 5. 用户交互
- 顶部导航栏
- 右侧菜单栏
- 底部按钮
- 信息面板
- 设置界面

## 实施步骤

### 阶段一：基础准备（已完成）
- [x] 分析原项目架构
- [x] 研究当前项目结构
- [x] 复制 map.html 及相关资源到当前项目

### 阶段二：后端 API 开发
- [ ] 创建地图设置相关 API（获取/更新地图配置）
- [ ] 创建聊天消息相关 API（发送/接收/历史记录）
- [ ] 创建地图标记相关 API（添加/删除/更新标记）
- [ ] 创建路径规划相关 API（查询路线、轨迹模拟）
- [ ] 创建 3D 模型相关 API（加载模型、动画控制）
- [ ] 创建用户设置相关 API（个人信息、住址设置）
- [ ] 创建任务管理相关 API（任务创建、查询、执行）
- [ ] 实现 WebSocket 实时通信接口

### 阶段三：前端修改
- [ ] 修改 map.html 中的 QWebChannel 通信为 HTTP/API 通信
- [ ] 重写 interact_python.js 中的 Python 调用为 API 请求
- [ ] 更新页面 UI 以适应 Electron 环境
- [ ] 实现地图与 Electron 主进程的通信机制
- [ ] 优化地图加载和渲染性能

### 阶段四：Electron 集成
- [ ] 在 Electron 中创建地图窗口
- [ ] 实现窗口管理功能（最大化、最小化、关闭）
- [ ] 添加地图相关的菜单和工具栏
- [ ] 实现地图窗口与主窗口的通信
- [ ] 处理地图窗口的生命周期

### 阶段五：功能测试
- [ ] 测试地图初始化和加载
- [ ] 测试地图基本操作（缩放、平移、旋转）
- [ ] 测试地图标记和聚类功能
- [ ] 测试路径规划和导航
- [ ] 测试聊天功能
- [ ] 测试 3D 模型加载和动画
- [ ] 测试用户设置功能
- [ ] 测试任务管理功能

## API 设计方案

### 地图设置 API
```
GET /api/map/settings - 获取地图配置
PUT /api/map/settings - 更新地图配置
GET /api/map/settings/home - 获取住址配置
PUT /api/map/settings/home - 更新住址配置
```

### 聊天消息 API
```
POST /api/chat/send - 发送聊天消息
GET /api/chat/history - 获取聊天历史
GET /api/chat/unread - 获取未读消息计数
```

### 地图标记 API
```
GET /api/map/markers - 获取地图标记列表
POST /api/map/markers - 添加地图标记
PUT /api/map/markers/{id} - 更新地图标记
DELETE /api/map/markers/{id} - 删除地图标记
```

### 路径规划 API
```
POST /api/map/route - 查询路线
GET /api/map/route/{id} - 获取路线详情
POST /api/map/route/{id}/start - 开始轨迹模拟
POST /api/map/route/{id}/stop - 停止轨迹模拟
POST /api/map/route/{id}/pause - 暂停轨迹模拟
POST /api/map/route/{id}/resume - 恢复轨迹模拟
```

### 3D 模型 API
```
GET /api/models - 获取模型列表
POST /api/models/load - 加载模型
POST /api/models/animate - 控制模型动画
```

### 用户设置 API
```
GET /api/user/profile - 获取用户资料
PUT /api/user/profile - 更新用户资料
GET /api/user/settings - 获取用户设置
PUT /api/user/settings - 更新用户设置
```

### 任务管理 API
```
GET /api/tasks - 获取任务列表
POST /api/tasks - 创建任务
PUT /api/tasks/{id} - 更新任务
DELETE /api/tasks/{id} - 删除任务
POST /api/tasks/{id}/execute - 执行任务
```

### WebSocket 接口
```
ws://localhost:8788/ws/map - 地图实时通信
  发送：聊天消息、地图操作、任务指令
  接收：聊天回复、地图更新、任务状态
```

## 通信机制

### 前端 → 后端
- **HTTP API**：用于常规请求-响应操作
- **WebSocket**：用于实时通信
- **Electron IPC**：用于前端与主进程通信

### 后端 → 前端
- **HTTP 响应**：常规 API 响应
- **WebSocket 推送**：实时消息推送
- **EventSource**：服务器发送事件（可选）

## 数据结构

### 地图配置
```json
{
  "map_type": "baidu",  // "baidu" 或 "google"
  "current_position": {
    "lng": 116.3974,
    "lat": 39.9093,
    "altitude": 0
  },
  "home_position": {
    "lng": 116.3974,
    "lat": 39.9093,
    "altitude": 0,
    "scale": 1.0,
    "rotation": {
      "x": 0,
      "y": 0,
      "z": 0
    }
  },
  "route_status": "stopped",  // "playing" 或 "stopped"
  "route_start": "北京大学",
  "route_end": "清华大学",
  "route_current_position": {
    "lng": 116.3974,
    "lat": 39.9093
  },
  "route_distance": 5.2
}
```

### 用户资料
```json
{
  "nationid": "123456",
  "account": "user@example.com",
  "nick_name": "用户昵称",
  "avatar": "avatar.png",
  "avatar_3d": "model.glb",
  "profile": "个人简介",
  "sns_url": "https://example.com",
  "status": "online"
}
```

### 聊天消息
```json
{
  "id": "msg_123",
  "from": "user1",
  "to": "user2",
  "content": "聊天内容",
  "timestamp": "2024-01-08T10:30:00Z",
  "location": {
    "lng": 116.3974,
    "lat": 39.9093
  }
}
```

### 地图标记
```json
{
  "id": "marker_123",
  "location": {
    "lng": 116.3974,
    "lat": 39.9093
  },
  "type": "person",
  "data": {
    "nation_id": "123456",
    "nick_name": "用户昵称",
    "avatar": "avatar.png"
  },
  "visible": true
}
```

### 路径信息
```json
{
  "id": "route_123",
  "start": "北京大学",
  "end": "清华大学",
  "distance": 5.2,
  "duration": 1200,
  "polyline": [...],
  "status": "completed"
}
```

## 技术实现要点

### 1. 地图引擎集成
- 保留百度地图和 Google 地图支持
- 实现地图类型切换功能
- 处理地图初始化和加载错误

### 2. 3D 模型渲染
- 使用 Three.js 加载 GLTF 模型
- 实现模型动画控制
- 优化模型加载和渲染性能

### 3. 实时通信
- 使用 WebSocket 实现实时聊天
- 实现地图状态同步
- 处理连接断开和重连

### 4. 性能优化
- 地图标记聚类
- 懒加载和虚拟滚动
- 资源预加载

### 5. 错误处理
- 地图加载失败
- API 请求错误
- 网络连接异常
- 模型加载失败

## 测试计划

### 功能测试
- [ ] 地图初始化
- [ ] 地图基本操作
- [ ] 地图标记管理
- [ ] 路径规划
- [ ] 聊天功能
- [ ] 3D 模型渲染
- [ ] 用户设置
- [ ] 任务管理

### 性能测试
- [ ] 地图加载时间
- [ ] 标记渲染性能
- [ ] 路径计算时间
- [ ] 3D 模型渲染帧率
- [ ] 内存使用情况

### 兼容性测试
- [ ] 不同浏览器（Chrome、Firefox、Safari）
- [ ] 不同操作系统（Windows、macOS、Linux）
- [ ] 不同屏幕分辨率

## 交付成果

### 文档
- [ ] 架构设计文档
- [ ] API 文档
- [ ] 用户使用指南
- [ ] 开发说明文档

### 代码
- [ ] api_server.py 中的地图相关 API
- [ ] map.html 及相关 JavaScript 文件
- [ ] Electron 地图窗口实现
- [ ] 测试代码

### 测试报告
- [ ] 功能测试报告
- [ ] 性能测试报告
- [ ] 兼容性测试报告

## 风险评估

### 技术风险
1. **地图引擎兼容性**：百度地图和 Google 地图 API 变更
2. **3D 模型渲染性能**：复杂模型在低配置设备上的渲染
3. **实时通信稳定性**：WebSocket 连接的稳定性和可靠性

### 实施风险
1. **API 开发进度**：后端 API 开发可能延迟
2. **前端修改复杂度**：map.html 中的 JavaScript 修改可能比预期复杂
3. **测试覆盖范围**：可能存在未覆盖的测试场景

### 解决方案
1. 提前研究地图引擎 API 文档
2. 优化 3D 模型和渲染代码
3. 实现完善的错误处理和重连机制
4. 制定详细的开发计划和测试方案

## 时间估算

| 阶段 | 任务 | 时间估算 |
|------|------|----------|
| 阶段一 | 基础准备 | 1 天 |
| 阶段二 | 后端 API 开发 | 7 天 |
| 阶段三 | 前端修改 | 5 天 |
| 阶段四 | Electron 集成 | 3 天 |
| 阶段五 | 功能测试 | 4 天 |
| 总计 | - | 20 天 |

---

**备注**：本计划为初步估算，实际开发时间可能会根据具体情况进行调整。