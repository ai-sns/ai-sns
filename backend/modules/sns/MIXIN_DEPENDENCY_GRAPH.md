# Mixin 依赖关系图

## Mixin 依赖层次结构

```
AISocialEngine (主类)
    │
    ├── InitializationMixin (1)
    │       └── 初始化所有基础状态和配置
    │
    ├── ResourceMixin (2)
    │       └── 依赖: InitializationMixin (需要基础状态)
    │
    ├── QueryMixin (3)
    │       └── 依赖: ResourceMixin (需要位置信息进行查询)
    │
    ├── LocationMixin (4)
    │       └── 依赖: InitializationMixin, ResourceMixin
    │
    ├── MessageParsingMixin (5)
    │       └── 独立功能
    │
    ├── AgentInteractionMixin (6)
    │       └── 依赖: UIDisplayMixin (需要显示思考过程)
    │
    ├── CommunicationMixin (7)
    │       └── 依赖: MessageHandlingMixin, LocationMixin
    │
    ├── MessageHandlingMixin (8)
    │       └── 依赖: MessageParsingMixin, CommunicationMixin
    │
    ├── UIDisplayMixin (9)
    │       └── 依赖: ResourceMixin (需要显示资源状态)
    │
    └── (其他 Mixin 可按需添加)
```

## Mixin 功能矩阵

| Mixin | 职责 | 依赖 | 状态管理 | 外部依赖 |
|--------|--------|--------|----------|----------|
| InitializationMixin | 初始化配置和状态 | 无 | Session, AiChatCfg |
| ResourceMixin | 资源管理 | InitializationMixin | 数据库查询函数 |
| QueryMixin | 数据查询 | ResourceMixin | API 请求 |
| LocationMixin | 位置和移动 | InitializationMixin, ResourceMixin | geopy, geographiclib |
| MessageParsingMixin | 消息解析 | 无 | re (正则表达式) |
| AgentInteractionMixin | Agent 交互 | UIDisplayMixin | agent_manager |
| CommunicationMixin | 通信管理 | MessageHandlingMixin, LocationMixin | taskmng |
| MessageHandlingMixin | 消息处理 | MessageParsingMixin, CommunicationMixin | XMPPClientManager, UIAdapter |
| UIDisplayMixin | UI 显示 | ResourceMixin | websocket_manager |

## Mixin 交互流

### 1. 初始化流程
```
AISocialEngine.__init__()
    │
    ├── InitializationMixin._initialize_configuration()
    │   └── 设置数据库连接和配置
    │
    ├── InitializationMixin._initialize_state_variables()
    │   └── 初始化所有状态变量
    │
    ├── InitializationMixin._initialize_position_variables()
    │   └── 初始化位置变量
    │
    └── ResourceMixin.load_all_user_data()
        └── 从数据库加载用户数据
```

### 2. 消息接收流程
```
XMPP 消息到达
    │
    ├── MessageHandlingMixin.receiveMessage()
    │
    ├── MessageParsingMixin 检查消息类型
    │   ├── check_tool_for_buy()
    │   ├── check_tool_for_order()
    │   ├── check_pay_in_received()
    │   └── ...
    │
    ├── 根据消息类型路由
    │   ├── CommunicationMixin.talk_to_a_people()
    │   └── (其他处理)
    │
    └── UIDisplayMixin._update_ui_with_sent_message()
        └── 更新 UI 显示
```

### 3. Agent 交互流程
```
需要 Agent 指示
    │
    ├── AgentInteractionMixin.ask_agent_and_get_instruction()
    │
    ├── UIDisplayMixin.write_thinking_process_to_pane()
    │   └── 显示思考过程
    │
    ├── Agent 返回结果
    │
    ├── AgentInteractionMixin.on_agent_return_instruction()
    │
    └── 根据命令状态分发结果
        ├── taskmng.process_task()
        └── (其他处理)
```

### 4. 位置移动流程
```
需要移动
    │
    ├── LocationMixin.move_ahead()
    │   ├── 计算新位置
    │   └── 更新位置状态
    │
    ├── ResourceMixin._parse_position_data()
    │   └── 解析位置数据
    │
    ├── UIDisplayMixin.send_msg_to_map()
    │   └── 发送移动命令到地图
    │
    └── ResourceMixin.save_all_user_data()
        └── 保存新位置到数据库
```

### 5. 资源更新流程
```
操作导致资源变化
    │
    ├── ResourceMixin.decline_energy()
    │   └── 降低能量值
    │
    ├── ResourceMixin.decline_life()
    │   └── 降低生命值
    │
    ├── UIDisplayMixin.get_on_going_process()
    │   └── 获取进行中状态
    │
    ├── UIDisplayMixin.write_on_going_process_to_pane()
    │   └── 更新 UI 显示
    │
    └── ResourceMixin.save_all_user_data()
        └── 持久化资源状态
```

## Mixin 接口约定

### 状态属性
所有 Mixin 共享以下状态属性（在 `InitializationMixin` 中定义）：
- `self.db` - 数据库会话
- `self.config` - 配置对象
- `self.ai_chat_cfg` - AI 聊天配置
- `self.started_flag` - 启动标志
- `self.map_task_status` - 地图任务状态
- `self.current_place` - 当前地点
- `self.current_talk_people` - 当前交谈人员
- `self.talk_history` - 聊天历史
- 资源属性：`life_point`, `energy_point`, `money`, `credit`, `level`

### 任务管理器
所有 Mixin 可以访问：
- `self.taskmng` - MapTaskManager 实例
- `self.taskmng_js` - JsTaskManager 实例

### UI 适配器
所有 Mixin 可以访问：
- `self.ui_adapter` - UIAdapter 实例

### XMPP 管理器
所有 Mixin 可以访问：
- `self.xmpp_manager` - XMPPClientManager 实例

### 配置管理器
所有 Mixin 可以访问：
- `self.aichatcfg_record` - AiChatCfgManager 实例

## Mixin 设计原则

### 1. 单一职责
- 每个 Mixin 只负责一个明确的功能领域
- 方法命名清晰反映其职责
- 避免在 Mixin 中实现不相关的功能

### 2. 最小依赖
- Minimize 依赖其他 Mixin
- 通过接口而非具体实现进行交互
- 使用状态共享而非直接调用方法

### 3. 明确接口
- 每个 Mixin 定义清晰的公共接口
- 文档说明方法的用途和参数
- 遵循一致的命名约定

### 4. 可测试性
- 每个方法应该是可独立测试的
- 避免全局状态
- 使用依赖注入便于 Mock

### 5. 向后兼容
- 保持公共方法签名不变
- 逐步迁移，分阶段进行
- 提供兼容层支持旧代码

## 扩展 Mixin

### 添加新 Mixin
1. 创建新的 Mixin 文件在 `mixins/` 目录
2. 继承自 `object`
3. 实现所需方法
4. 在 `AISocialEngine` 类中添加到继承列表
5. 更新本文档说明依赖关系

### 示例：创建 TradeMixin
```python
# trade_mixin.py
class TradeMixin:
    """
    处理交易相关操作
    """

    def initiate_trade(self, trade_type, counterparty_id, items):
        """发起交易"""
        # 实现交易逻辑
        pass

    def accept_trade(self, trade_id):
        """接受交易"""
        # 实现接受逻辑
        pass

    def reject_trade(self, trade_id, reason):
        """拒绝交易"""
        # 实现拒绝逻辑
        pass

# 在 AISocialEngine 中添加
class AISocialEngine(
    # ... 现有 Mixin
    TradeMixin,
):
    pass
```

## 注意事项

1. **避免循环依赖**
   - Mixin A 依赖 Mixin B
   - Mixin B 不应该依赖 Mixin A

2. **明确状态所有权**
   - 哪个 Mixin "拥有" 哪些状态
   - 其他 Mixin 只读或通过方法访问

3. **错误处理**
   - 每个 Mixin 应该处理自己的错误
   - 不要假设其他 Mixin 会捕获异常

4. **日志记录**
   - 使用统一的日志格式
   - 在 Mixin 中添加适当的日志

5. **性能考虑**
   - 避免在 Mixin 中进行阻塞操作
   - 使用异步方法进行 I/O 操作
