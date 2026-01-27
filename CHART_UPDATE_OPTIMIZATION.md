# Chart Update Optimization - 图表更新优化

## 概述 (Overview)

本文档描述了对 `update_map_charts` 函数的优化，使其能够在用户属性更新时实时更新前端的柱状图和雷达图。

This document describes the optimization of the `update_map_charts` function to enable real-time updates of bar charts and radar charts in the frontend when user properties change.

## 问题描述 (Problem Description)

### 原始问题
- `backend/modules/sns/ui_display_mixin.py` 中的 `update_map_charts()` 函数只准备了数据，但没有发送到前端
- 前端 `renderer/js/modules/sns/SNSSidebar.js` 中的 `userStats` 无法实时更新
- 柱状图和雷达图不会自动刷新

### Original Problem
- The `update_map_charts()` function in `backend/modules/sns/ui_display_mixin.py` only prepared data but didn't send it to the frontend
- The `userStats` in frontend `renderer/js/modules/sns/SNSSidebar.js` couldn't update in real-time
- Bar charts and radar charts wouldn't refresh automatically

## 解决方案 (Solution)

### 1. 后端优化 (Backend Optimization)

#### 文件: `backend/modules/sns/ui_display_mixin.py`

**优化的 `update_map_charts()` 函数:**

```python
def update_map_charts(self):
    """
    更新地图图表数据并发送到前端
    当用户属性（如智力、体力、生命值等）发生变化时调用此函数
    """
    import asyncio

    # 准备雷达图数据
    radar_data = [
        self.aichatcfg_record.iq_point,
        self.aichatcfg_record.energy_point,
        self.aichatcfg_record.life_point,
        self.aichatcfg_record.move_point,
        self.aichatcfg_record.exp_point
    ]

    # 准备柱状图数据
    formatted_number = f"{self.aichatcfg_record.money:,.2f}"

    # 构建用户统计数据对象
    user_stats = {
        "level": self.aichatcfg_record.level or 1,
        "credit": self.aichatcfg_record.credit or 100,
        "money": float(self.aichatcfg_record.money or 0),
        "life": self.aichatcfg_record.life_point or 100,
        "iq": self.aichatcfg_record.iq_point or 60,
        "energy": self.aichatcfg_record.energy_point or 100,
        "move": self.aichatcfg_record.move_point or 100,
        "exp": self.aichatcfg_record.exp_point or 0
    }

    # 通过WebSocket发送更新到前端
    asyncio.create_task(self._send_chart_update(user_stats))

async def _send_chart_update(self, user_stats: dict):
    """发送图表更新数据到前端"""
    try:
        message = {
            "type": "user_stats_update",
            "data": user_stats
        }
        await websocket_manager.broadcast(message)
        logger.info(f"User stats update sent to frontend")
    except Exception as e:
        logger.error(f"Failed to send chart update: {e}")
```

**关键改进:**
1. 创建完整的 `user_stats` 对象，包含所有需要的属性
2. 通过 WebSocket 广播消息到前端
3. 使用异步任务发送更新，不阻塞主线程
4. 添加错误处理和日志记录

#### 文件: `backend/modules/sns/data_query_mixin.py`

在 `load_all_user_data()` 函数中添加了对 `update_map_charts()` 的调用:

```python
# 在加载完所有数据后更新资源显示和图表
self.update_resource_display()
self.update_map_charts()  # 新增
```

### 2. 前端优化 (Frontend Optimization)

#### 文件: `renderer/js/modules/sns/SNSSidebar.js`

**新增 WebSocket 消息处理:**

```javascript
setupWebSocketListener() {
    window.addEventListener('websocket-message', (event) => {
        const message = event.detail;
        if (message.type === 'new_message') {
            this.handleNewMessage(message.data);
        } else if (message.type === 'user_stats_update') {
            // 处理用户统计数据更新
            this.handleUserStatsUpdate(message.data);
        }
    });
},

handleUserStatsUpdate(data) {
    console.log('Received user stats update:', data);

    // 更新本地userStats对象
    if (data) {
        this.userStats = {
            level: data.level || this.userStats.level,
            credit: data.credit || this.userStats.credit,
            money: data.money || this.userStats.money,
            life: data.life || this.userStats.life,
            iq: data.iq || this.userStats.iq,
            energy: data.energy || this.userStats.energy,
            move: data.move || this.userStats.move,
            exp: data.exp || this.userStats.exp
        };

        // 重新渲染图表和统计数据
        this.renderStats();

        console.log('User stats updated successfully:', this.userStats);
    }
},
```

**关键改进:**
1. 监听 `user_stats_update` 类型的 WebSocket 消息
2. 更新本地 `userStats` 对象
3. 调用 `renderStats()` 重新渲染柱状图和雷达图
4. 添加控制台日志便于调试

## 触发机制 (Trigger Mechanism)

### 自动触发场景

`update_map_charts()` 会在以下情况自动调用:

1. **属性更新时** - 通过 `handle_aichatcfg_property_updated()` 函数
   - 当以下属性变化时触发:
     - `iq_point` (智力)
     - `energy_point` (体力)
     - `life_point` (生命值)
     - `move_point` (行动力)
     - `exp_point` (经验值)
     - `money` (资金)
     - `credit` (信用)
     - `level` (等级)

2. **数据加载时** - 通过 `load_all_user_data()` 函数
   - 系统启动时
   - 用户数据重新加载时

### 代码位置

**触发点 1:** `backend/modules/sns/ai_social_engine_adapter.py` (Line 818-841)

```python
def handle_aichatcfg_property_updated(self, property_name):
    chart_related_properties = [
        'iq_point', 'energy_point', 'life_point',
        'move_point', 'exp_point', 'money',
        'credit', 'level'
    ]

    if property_name in chart_related_properties:
        self.update_map_charts()  # 触发更新
```

**触发点 2:** `backend/modules/sns/data_query_mixin.py` (Line 182-184)

```python
def load_all_user_data(self):
    # ... 加载数据 ...
    self.update_resource_display()
    self.update_map_charts()  # 触发更新
```

## 数据流 (Data Flow)

```
┌─────────────────────────────────────────────────────────────┐
│  1. 属性更新 (Property Update)                               │
│     - AiChatCfgManager.__setattr__()                        │
│     - 触发回调: handle_aichatcfg_property_updated()          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 图表更新 (Chart Update)                                  │
│     - update_map_charts()                                   │
│     - 准备 user_stats 数据                                   │
│     - 调用 _send_chart_update()                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. WebSocket 广播 (WebSocket Broadcast)                    │
│     - websocket_manager.broadcast()                         │
│     - 消息类型: "user_stats_update"                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 前端接收 (Frontend Receives)                             │
│     - window.addEventListener('websocket-message')          │
│     - handleUserStatsUpdate()                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 界面更新 (UI Update)                                     │
│     - 更新 userStats 对象                                    │
│     - renderStats() - 更新柱状图                             │
│     - renderRadarChart() - 更新雷达图                        │
└─────────────────────────────────────────────────────────────┘
```

## 测试方法 (Testing Method)

### 1. 手动测试

在后端代码中修改用户属性:

```python
# 示例: 修改用户的金钱属性
self.aichatcfg_record.money = 15000.50

# 这会自动触发:
# 1. AiChatCfgManager.__setattr__()
# 2. handle_aichatcfg_property_updated('money')
# 3. update_map_charts()
# 4. 前端图表更新
```

### 2. 通过 API 测试

使用 API 更新用户配置:

```bash
curl -X PUT http://localhost:8000/api/sns/config \
  -H "Content-Type: application/json" \
  -d '{
    "money": 20000,
    "life_point": 150,
    "energy_point": 120
  }'
```

### 3. 前端控制台验证

打开浏览器开发者工具，查看控制台输出:

```
Received user stats update: {level: 3, credit: 100, money: 20000, ...}
User stats updated successfully: {level: 3, credit: 100, money: 20000, ...}
```

## 相关文件 (Related Files)

### 后端 (Backend)
- `backend/modules/sns/ui_display_mixin.py` - 图表更新逻辑
- `backend/modules/sns/ai_social_engine_adapter.py` - 属性更新处理
- `backend/modules/sns/data_query_mixin.py` - 数据加载
- `backend/shared/websocket_manager.py` - WebSocket 管理

### 前端 (Frontend)
- `renderer/js/modules/sns/SNSSidebar.js` - 侧边栏和图表渲染

## 注意事项 (Notes)

1. **WebSocket 连接**: 确保前端已建立 WebSocket 连接
2. **数据格式**: 所有数值属性都有默认值，避免 `None` 或 `undefined`
3. **性能**: 使用异步任务发送更新，不会阻塞主线程
4. **错误处理**: 添加了完整的错误处理和日志记录
5. **兼容性**: 保持向后兼容，不影响现有功能

## 未来改进 (Future Improvements)

1. 添加节流机制，避免频繁更新
2. 支持批量更新多个属性
3. 添加动画效果使图表更新更平滑
4. 支持自定义图表样式和配置

## 总结 (Summary)

通过这次优化:
- ✅ 完善了 `update_map_charts()` 函数，使其能够发送数据到前端
- ✅ 添加了前端 WebSocket 监听器，实时接收更新
- ✅ 实现了柱状图和雷达图的自动刷新
- ✅ 提供了完整的数据流和触发机制
- ✅ 添加了详细的日志和错误处理

现在，当用户属性（如金钱、生命值、体力等）发生变化时，前端的图表会自动更新，无需手动刷新页面。
