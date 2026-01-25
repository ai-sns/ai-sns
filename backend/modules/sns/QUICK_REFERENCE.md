# AISocialEngine Mixin 快速参考指南

## 目录结构

```
backend/modules/sns/
├── mixins/                          # Mixin 模块目录
│   ├── __init__.py
│   ├── initialization_mixin.py       # 初始化和配置
│   ├── agent_interaction_mixin.py    # Agent 交互
│   ├── location_mixin.py            # 位置和移动
│   ├── communication_mixin.py       # 通信管理
│   ├── message_handling_mixin.py     # XMPP 消息处理
│   ├── query_mixin.py              # 数据查询
│   ├── resource_mixin.py           # 资源管理
│   ├── ui_display_mixin.py         # UI 显示
│   ├── message_parsing_mixin.py     # 协议消息解析
│   └── refactored_engine_example.py # 重构后的主类示例
├── ai_social_engine_adapter.py      # 原始类（保留）
├── AISOCIAL_ENGINE_REFACTORING.md   # 重构详细说明
├── MIXIN_DEPENDENCY_GRAPH.md        # 依赖关系图
└── QUICK_REFERENCE.md              # 本文档
```

## 快速查找

### 我想... | 使用哪个 Mixin | 方法
|---------|----------------|-------
| 初始化引擎 | InitializationMixin | `_initialize_configuration()`, `load_all_user_data()`
| 与 Agent 对话 | AgentInteractionMixin | `ask_agent_and_get_instruction()`
| 移动到新位置 | LocationMixin | `move_ahead()`, `go_around()`, `move_by_route()`
| 与人员聊天 | CommunicationMixin | `talk_to_a_people()`, `communicate_with_a_people()`
| 发送/接收消息 | MessageHandlingMixin | `sendMessage()`, `receiveMessage()`
| 查询工具列表 | QueryMixin | `get_tool_list()`, `get_plugin_tool_list()`
| 查询人员列表 | QueryMixin | `get_people_list()`
| 保存用户数据 | ResourceMixin | `save_all_user_data()`
| 更新 UI 显示 | UIDisplayMixin | `write_thinking_process_to_pane()`
| 解析协议消息 | MessageParsingMixin | `get_tool_list_in_message()`

## Mixin 功能速查

### InitializationMixin
**核心功能**：引擎初始化

```python
# 初始化示例
engine = AISocialEngine(db)

# 加载用户数据
engine.load_all_user_data()

# 保存用户数据
engine.save_all_user_data()
```

### AgentInteractionMixin
**核心功能**：与 AI Agent 交互

```python
# 请求 Agent 指示
await engine.ask_agent_and_get_instruction(
    question="下一步该做什么？",
    system_role_prompt="你是一个助手"
)

# Agent 返回时会自动调用
# on_agent_return_instruction()
```

### LocationMixin
**核心功能**：位置和移动

```python
# 移动到目标位置
result = engine.move_ahead(
    current_position=[116.3, 39.9],
    target_position=[116.4, 40.0],
    target_place="天安门"
)

# 随机移动
result = engine.go_around()
```

### CommunicationMixin
**核心功能**：与其他人员通信

```python
# 与某人员交谈
engine.talk_to_a_people(
    content="你好！",
    nationid="AI123...",
    account="yangyang@xabber.de",
    user_name="W宝"
)
```

### MessageHandlingMixin
**核心功能**：XMPP 消息处理

```python
# 发送消息
engine.sendMessage(
    content="Hello!",
    to_jid="yangyang@xabber.de",
    to_name="W宝"
)

# 接收消息（自动调用）
# await engine.receiveMessage(event)
```

### QueryMixin
**核心功能**：数据查询

```python
# 获取工具列表
tools = engine.get_tool_list()

# 获取人员列表
people = engine.get_people_list()

# 获取地点列表
places = engine.get_place_list()
```

### ResourceMixin
**核心功能**：资源管理

```python
# 降低能量
engine.decline_energy()

# 降低生命值
engine.decline_life()

# 解析位置数据
position = engine._parse_position_data("[116.3, 39.9]")
```

### UIDisplayMixin
**核心功能**：UI 显示

```python
# 显示思考过程
engine.write_thinking_process_to_pane(
    title="分析中",
    content="正在分析下一步行动..."
)

# 显示状态
engine.show_status_on_map("thinking")
```

### MessageParsingMixin
**核心功能**：协议消息解析

```python
# 解析工具列表
tool_list_str = engine.get_tool_list_in_message(msg)

# 检查支付接收
pay_str = engine.check_pay_in_received(msg)

# 检查货物接收
good_str = engine.check_good_in_received(msg)
```

## 常见用例

### 用例 1：启动 AI 社交引擎

```python
from backend.modules.sns.mixins.refactored_engine_example import AISocialEngine

# 创建引擎实例
engine = AISocialEngine(db)

# 启动引擎
await engine.start()

# 处理任务
engine.start_task()

# 停止引擎
await engine.stop()
```

### 用例 2：处理接收到的消息

```python
# 消息接收由 XMPP 回调触发
async def on_message_received(event):
    await engine.receiveMessage(event)

    # 消息会自动路由到相应的处理器：
    # - 工具交易 -> tool_trade_xxx()
    # - 普通聊天 -> talk_to_a_people()
    # - 支付/货物 -> handle_pay_received() 等
```

### 用例 3：执行移动任务

```python
# 1. 请求 Agent 指示
await engine.ask_agent_and_get_instruction(
    question="我该如何到达天安门？",
    system_role_prompt="你是导航助手"
)

# 2. Agent 可能返回移动指令
# 3. 执行移动
result = engine.move_ahead(
    current_position=engine.aichatcfg_record.current_position,
    target_position=[116.3975, 39.9087],
    target_place="天安门"
)

# 4. 更新 UI
engine.write_on_going_process_to_pane(result)
```

### 用例 4：发起工具交易

```python
# 1. 与人员交谈
engine.talk_to_a_people(
    content="我想购买你的工具",
    nationid=people["nation_id"],
    account=people["account"],
    user_name=people["nick_name"]
)

# 2. 人员发送工具列表（AISNS_INT_001 协议）
# 3. 解析工具列表
tool_list_str = engine.get_tool_list_in_message(received_msg)

# 4. 发起订单
engine.tool_trade_order(tool_list_str)

# 5. 处理议价
bargain_str = engine.get_buyer_bargain_in_message(received_msg)
engine.tool_trade_bargain_for_seller(bargain_str)
```

## 状态属性参考

### 引擎状态
```python
engine.started_flag              # 是否已启动
engine.map_task_status          # 任务状态
engine.command_status            # 当前命令状态
engine.human_take_over          # 人工接管标志
engine.pause_flag               # 暂停标志
```

### 位置状态
```python
engine.current_place             # 当前地点
engine.aichatcfg_record.current_position  # 当前坐标 [lng, lat]
engine.aichatcfg_record.last_position     # 上次坐标
engine.target_place             # 目标地点
engine.target_position          # 目标坐标
```

### 资源状态
```python
engine.life_point              # 生命值 (0-100)
engine.energy_point            # 能量值 (0-100)
engine.move_point              # 行动力 (0-100)
engine.exp_point               # 经验值
engine.iq_point               # 智力
engine.money                   # 资金
engine.credit                 # 信用
engine.level                   # 等级
```

### 通信状态
```python
engine.talk_type               # 交谈类型 (communication/sell/buy)
engine.current_talk_people      # 当前交谈人员
engine.talk_history            # 聊天历史 {account: [messages]}
engine.current_talk_history     # 当前会话历史
```

## 事件流程

### 完整对话流程

```
1. 引擎启动
   └── AISocialEngine.__init__()

2. 接收消息
   └── receiveMessage(event)
       └── handle_receiveMessage(content, from_str)
           ├── 检查消息类型
           └── 路由到处理器
               ├── 普通聊天
               │   └── talk_to_a_people()
               ├── 工具交易
               │   ├── tool_trade_order()
               │   └── tool_trade_bargain_xxx()
               └── 支付/货物
                   └── handle_xxx_received()

3. 请求 Agent 分析
   └── ask_agent_and_get_instruction()
       └── on_agent_return_instruction()
           └── taskmng.process_task()

4. 执行操作
   ├── 移动
   │   └── LocationMixin methods
   ├── 交易
   │   └── Trade methods (待实现)
   └── 沟通
       └── CommunicationMixin methods

5. 更新 UI
   └── UIDisplayMixin methods
```

## 调试技巧

### 1. 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或设置特定模块的日志级别
logging.getLogger('backend.modules.sns').setLevel(logging.DEBUG)
```

### 2. 追踪 Mixin 调用

```python
# 在 Mixin 方法中添加日志
def my_method(self, param):
    logger.info(f"Mixin: {self.__class__.__name__}, Method: my_method")
    # ... 方法实现
```

### 3. 检查状态

```python
# 打印当前状态
print(f"Started: {engine.started_flag}")
print(f"Position: {engine.aichatcfg_record.current_position}")
print(f"Resources: Life={engine.life_point}, Energy={engine.energy_point}")
```

### 4. 测试单个 Mixin

```python
# 创建只包含某个 Mixin 的测试类
class TestEngine(InitializationMixin, QueryMixin):
    def __init__(self):
        self._initialize_configuration(db)
        self._initialize_state_variables()

engine = TestEngine()
tools = engine.get_tool_list()
```

## 最佳实践

### 1. 错误处理

```python
# 使用 try-except 包裹外部调用
try:
    result = self.some_method()
except Exception as e:
    logger.error(f"Error in some_method: {e}", exc_info=True)
    # 提供降级处理
```

### 2. 异步操作

```python
# 确保异步方法使用 await
async def my_async_method(self):
    await self.some_async_operation()

# 同步方法中启动异步任务
def my_sync_method(self):
    asyncio.create_task(self.some_async_operation())
```

### 3. 状态验证

```python
# 在访问状态前验证
if hasattr(self, 'aichatcfg_record'):
    position = self.aichatcfg_record.current_position
else:
    logger.warning("aichatcfg_record not initialized")
    return None
```

### 4. 资源清理

```python
# 在停止时清理资源
async def stop(self):
    self.started_flag = False

    # 关闭连接
    if hasattr(self, 'xmpp_manager'):
        # 清理 XMPP 资源
        pass

    # 保存状态
    self.save_all_user_data()
```

## 常见问题

### Q1: 如何添加新的 Mixin？

**A**: 在 `mixins/` 目录创建新文件，继承自 `object`，然后在 `AISocialEngine` 中添加到继承列表。参考现有 Mixin 的结构。

### Q2: Mixin 之间如何共享数据？

**A**: 通过 `self` 对象共享状态。建议在 `InitializationMixin` 中定义共享属性，其他 Mixin 通过 `self.attribute_name` 访问。

### Q3: 如何处理 Mixin 方法冲突？

**A**: 后定义的 Mixin 会覆盖前面的同名方法。使用不同的方法名，或在主类中提供协调方法。

### Q4: 如何测试单个 Mixin？

**A**: 创建一个继承该 Mixin 的简单类，初始化必要的状态，然后测试其方法。

### Q5: 性能如何？

**A**: Mixin 本身不带来性能开销。主要考虑异步操作的正确使用和避免不必要的数据库查询。

## 相关文档

- [AISOCIAL_ENGINE_REFACTORING.md](./AISOCIAL_ENGINE_REFACTORING.md) - 详细重构说明
- [MIXIN_DEPENDENCY_GRAPH.md](./MIXIN_DEPENDENCY_GRAPH.md) - 依赖关系图
- [原始文件](./ai_social_engine_adapter.py) - 原始 AISocialEngine 类
- [重构示例](./mixins/refactored_engine_example.py) - 重构后的主类示例
