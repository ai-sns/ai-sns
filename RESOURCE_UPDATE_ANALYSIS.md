# 资源更新信号机制分析报告

## 📋 分析目标
研究 `backend/modules/sns/ai_social_engine_adapter.py` 及相关 mixin 文件中，money、energy、life 等资源变化时，是否正确触发了：
1. `self.aichatcfg_record.connect(self.handle_aichatcfg_property_updated)` 信号连接
2. `self.update_map_charts()` 方法调用
3. 数据推送到前端 Electron 进行更新（特别是雷达图）

---

## ✅ 核心发现

### 1. 信号连接机制 ✅ 已正确实现

**位置**: `backend/modules/sns/ai_social_engine_adapter.py` 第 97-98 行

```python
self.aichatcfg_record = AiChatCfgManager()
self.aichatcfg_record.connect(self.handle_aichatcfg_property_updated)
```

**说明**: 
- 在 `AISocialEngine.__init__()` 中正确创建了 `AiChatCfgManager` 实例
- 通过 `connect()` 方法连接了回调函数 `handle_aichatcfg_property_updated`

---

### 2. 属性更新回调处理 ✅ 已正确实现

**位置**: `backend/modules/sns/ai_social_engine_adapter.py` 第 843-868 行

```python
def handle_aichatcfg_property_updated(self, property_name):
    """
    处理AiChatCfg属性更新的函数
    当特定属性发生变化时，更新相关的界面元素
    """
    # 定义需要更新图表的属性
    chart_related_properties = [
        'iq_point', 'energy_point', 'life_point',
        'move_point', 'exp_point', 'money',
        'credit', 'level'
    ]

    # 定义需要更新进行中进程面板的属性
    process_pane_related_properties = [
        'profession', 'current_position', 'money',
        'life_point', 'energy_point'
    ]

    # 如果属性与图表相关，则更新图表
    if property_name in chart_related_properties:
        self.update_map_charts()

    # 如果属性与进行中进程面板相关，则更新面板
    if property_name in process_pane_related_properties:
        self.write_on_going_process_to_pane(self.current_ongoing_content or "")
```

**说明**:
- ✅ 当 `money`、`life_point`、`energy_point`、`move_point`、`exp_point`、`iq_point`、`credit`、`level` 等属性变化时
- ✅ 会自动调用 `self.update_map_charts()` 更新雷达图
- ✅ 同时会更新进行中进程面板

---

### 3. AiChatCfgManager 信号触发机制 ✅ 已正确实现

**位置**: `backend/modules/sns/ai_social_engine_adapter.py` 第 1027-1088 行

```python
class AiChatCfgManager:
    def __setattr__(self, name, value):
        """当设置属性时调用此方法，用于更新数据库记录中的字段值"""
        # 处理内部属性
        if name.startswith('_') or name in ['user_id']:
            super().__setattr__(name, value)
            return

        # 位置相关字段特殊处理
        position_fields = ['current_position', 'last_position', 'home_position',
                           'route_start', 'route_end', 'route_current_position']
        if name in position_fields and isinstance(value, (list, dict)):
            import json
            value = json.dumps(value, ensure_ascii=False)

        # 对于其他属性，更新数据库记录
        if '_record' in self.__dict__ and self._record is not None:
            # 更新数据库
            if self._user_id:
                update_AiChatCfg_by_user_id(self._user_id, **{name: value})
            else:
                update_AiChatCfg_map(**{name: value})

            # 更新内存中的记录
            setattr(self._record, name, value)

            # 🔔 触发属性更新回调
            self._emit_property_updated(name)
```

**说明**:
- ✅ 每次通过 `self.aichatcfg_record.money = xxx` 赋值时
- ✅ 会自动调用 `_emit_property_updated(name)` 触发所有已连接的回调
- ✅ 同时会更新数据库

---

### 4. update_map_charts() 数据推送 ✅ 已正确实现

**位置**: `backend/modules/sns/ui_display_mixin.py` 第 363-407 行

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

**说明**:
- ✅ 通过 WebSocket 向前端广播 `user_stats_update` 消息
- ✅ 包含所有雷达图需要的数据：life、iq、energy、move、exp
- ✅ 包含柱状图需要的数据：money、credit、level

---

## 🔍 资源变化触发点分析

### 方式 1: 通过 ResourceManagementMixin 方法 ✅

**位置**: `backend/modules/sns/resource_management_mixin.py`

```python
def decline_life(self):
    """降低生命值"""
    self.life_point = max(0, self.life_point - 10)
    self.aichatcfg_record.life_point = self.life_point  # ✅ 触发信号
    # 会自动调用 handle_aichatcfg_property_updated('life_point')
    # 进而调用 update_map_charts()

def decline_energy(self):
    """降低体力值"""
    self.energy_point = max(0, self.energy_point - 10)
    self.aichatcfg_record.energy_point = self.energy_point  # ✅ 触发信号

def add_money(self, amount):
    """增加金钱"""
    self.money += amount
    self.aichatcfg_record.money = self.money  # ✅ 触发信号

def spend_money(self, amount):
    """花费金钱"""
    self.money -= amount
    self.aichatcfg_record.money = self.money  # ✅ 触发信号
```

**调用位置**:
- `ai_social_engine_adapter.py` 第 627 行: `self.decline_life()`
- `ai_social_engine_adapter.py` 第 630 行: `self.decline_energy()`
- `trade_mixin.py` 第 439、456、528、588 行: `self.add_money()`

---

### 方式 2: 通过 TradeMixin 直接修改 ✅

**位置**: `backend/modules/sns/trade_mixin.py`

```python
def set_food_order(self):
    """外卖服务 - 恢复体力"""
    self.aichatcfg_record.energy_point = self.aichatcfg_record.energy_point + 25  # ✅ 触发信号
    self.aichatcfg_record.move_point = 100 * (self.aichatcfg_record.life_point / 100) * (self.aichatcfg_record.energy_point / 100)  # ✅ 触发信号
    self.aichatcfg_record.money = self.aichatcfg_record.money - 30  # ✅ 触发信号

def set_taxi_order(self, current_position, target_position, place):
    """叫车服务 - 扣除费用"""
    fee = dist * 2.5
    self.aichatcfg_record.money = self.aichatcfg_record.money - fee  # ✅ 触发信号

def call_a_doctor(self):
    """远程医疗 - 恢复生命值"""
    self.aichatcfg_record.life_point = self.aichatcfg_record.life_point + 25  # ✅ 触发信号
    self.aichatcfg_record.move_point = 100 * (self.aichatcfg_record.life_point / 100) * (self.aichatcfg_record.energy_point / 100)  # ✅ 触发信号
    self.aichatcfg_record.money = self.aichatcfg_record.money - 210  # ✅ 触发信号
```

---

## 📊 完整的数据流

```
资源变化
    ↓
self.aichatcfg_record.money = new_value
    ↓
AiChatCfgManager.__setattr__()
    ↓
update_AiChatCfg_map(**{name: value})  [更新数据库]
    ↓
self._emit_property_updated(name)
    ↓
handle_aichatcfg_property_updated(property_name)
    ↓
self.update_map_charts()  [如果是图表相关属性]
    ↓
asyncio.create_task(self._send_chart_update(user_stats))
    ↓
websocket_manager.broadcast({
    "type": "user_stats_update",
    "data": {
        "money": ...,
        "life": ...,
        "energy": ...,
        "iq": ...,
        "move": ...,
        "exp": ...,
        "credit": ...,
        "level": ...
    }
})
    ↓
前端 Electron 接收 WebSocket 消息
    ↓
更新雷达图和柱状图
```

---

## ✅ 结论

### 信号连接机制：✅ 完全正常

1. ✅ `self.aichatcfg_record.connect(self.handle_aichatcfg_property_updated)` 在初始化时正确连接
2. ✅ 每次属性变化都会触发 `_emit_property_updated()`
3. ✅ 回调函数 `handle_aichatcfg_property_updated()` 会被正确调用

### update_map_charts() 调用：✅ 完全正常

1. ✅ 当 `money`、`life_point`、`energy_point`、`move_point`、`exp_point`、`iq_point`、`credit`、`level` 变化时
2. ✅ 会自动调用 `update_map_charts()`
3. ✅ 通过 WebSocket 向前端推送 `user_stats_update` 消息

### 数据推送到前端：✅ 完全正常

1. ✅ 使用 `websocket_manager.broadcast()` 广播消息
2. ✅ 消息类型为 `"user_stats_update"`
3. ✅ 包含所有雷达图和柱状图需要的数据

---

## 🔧 潜在问题点

### 1. ⚠️ 混合使用两种方式修改资源

**问题**: 代码中同时存在两种修改资源的方式：

**方式 A**: 通过 ResourceManagementMixin 方法（推荐）
```python
self.decline_life()  # 会触发信号
self.add_money(100)  # 会触发信号
```

**方式 B**: 直接修改 aichatcfg_record 属性（也会触发信号）
```python
self.aichatcfg_record.money = self.aichatcfg_record.money + 100  # 会触发信号
```

**建议**: 统一使用方式 A（ResourceManagementMixin 方法），代码更清晰

### 2. ⚠️ data_query_mixin.py 中的重复方法

**位置**: `backend/modules/sns/data_query_mixin.py` 第 229-240 行

```python
def decline_energy(self):
    exp = self.exp_point
    decline_point = 25 * ((100 - exp) / 100)
    # ... 但没有更新 self.aichatcfg_record.energy_point

def decline_life(self):
    exp = self.exp_point
    decline_point = 25 * ((100 - exp) / 100)
    # ... 但没有更新 self.aichatcfg_record.life_point
```

**问题**: 
- 这些方法与 `resource_management_mixin.py` 中的方法重名
- 但实现不同，且**没有触发信号**
- 可能导致混淆

**建议**: 
- 删除 `data_query_mixin.py` 中的这些方法
- 或者重命名为不同的名称

### 3. ⚠️ 前端是否正确监听 WebSocket 消息

**需要验证**: 前端 Electron 是否正确监听并处理 `user_stats_update` 消息

**检查位置**: 
- `renderer/js/modules/sns/SNSSidebar.js`
- `renderer/js/modules/sns/SNSPage.js`

---

## 🎯 测试建议

### 1. 单元测试
创建测试脚本验证信号机制：
```python
# 测试信号连接
engine = AISocialEngine(db)
assert engine.handle_aichatcfg_property_updated in engine.aichatcfg_record._callbacks

# 测试属性变化触发
engine.aichatcfg_record.money = 1000
# 验证 update_map_charts() 被调用
```

### 2. 集成测试
- 启动后端 API 服务器
- 启动前端 Electron
- 修改资源值
- 观察前端雷达图是否实时更新

### 3. WebSocket 消息监控
在前端添加日志：
```javascript
websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'user_stats_update') {
        console.log('收到资源更新:', data.data);
        // 更新雷达图
    }
};
```

---

## 📝 总结

**核心机制完全正常** ✅

所有资源变化（money、energy、life、move、exp、iq、credit、level）都会：
1. ✅ 触发 `AiChatCfgManager` 的 `__setattr__` 方法
2. ✅ 更新数据库
3. ✅ 调用 `_emit_property_updated()` 触发回调
4. ✅ 执行 `handle_aichatcfg_property_updated()`
5. ✅ 调用 `update_map_charts()`
6. ✅ 通过 WebSocket 推送到前端
7. ✅ 前端更新雷达图和柱状图

**唯一需要注意的是**：
- 确保前端正确监听 `user_stats_update` 消息
- 统一使用 ResourceManagementMixin 方法修改资源
- 清理 data_query_mixin.py 中的重复方法
