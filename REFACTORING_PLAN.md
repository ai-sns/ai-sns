# AISocialEngine 重构方案

## 一、功能模块划分

### 1. Agent通信适配器 (agent_communication_adapter.py)
**职责**: 处理与AI Agent的所有通信交互
**核心功能**:
- `ask_agent_and_get_instruction()` - 向Agent请求指令
- `on_agent_return_instruction()` - 处理Agent返回的指令
- 各种command_status的路由处理

**依赖关系**:
- 依赖: agent_manager, ai_chat_cfg
- 被依赖: 所有需要LLM决策的模块

**代码行数**: ~180行
**原始位置**: 423-603行

---

### 2. 任务管理适配器 (task_management_adapter.py)
**职责**: 任务分解、更新、执行流程管理
**核心功能**:
- `ask_agent_to_decompose_task()` - 任务分解
- `handle_agent_plan_task_result()` - 处理任务分解结果
- `ask_agent_to_update_task()` - 任务更新
- `handle_agent_update_task_result()` - 处理任务更新结果
- `restart_plan()` - 重启计划

**依赖关系**:
- 依赖: agent_communication_adapter, taskmng
- 被依赖: activity_processing_adapter

**代码行数**: ~150行
**原始位置**: 737-880行

---

### 3. 活动处理适配器 (activity_processing_adapter.py)
**职责**: 处理具体的活动执行逻辑
**核心功能**:
- `ask_agent_instruction_to_process_activity()` - 请求活动处理指令
- `parse_agent_instruction_for_process_activity()` - 解析活动指令
- `compose_full_ask_content()` - 构建完整请求内容
- `get_next_action()` - 获取下一步行动
- `get_current_task_list()` - 获取当前任务列表

**依赖关系**:
- 依赖: agent_communication_adapter, movement_adapter, communication_adapter, tool_adapter
- 被依赖: task_management_adapter

**代码行数**: ~180行
**原始位置**: 882-1061行

---

### 4. 移动管理适配器 (movement_adapter.py)
**职责**: 处理所有位置移动相关功能
**核心功能**:
- `go_around()` - 随机移动
- `move_ahead()` - 朝目标移动
- `move_by_route()` - 按路线移动
- `initial_bearing()` - 计算方位角
- `update_after_moving()` - 移动后更新

**依赖关系**:
- 依赖: aichatcfg_record, ui_adapter
- 被依赖: activity_processing_adapter

**代码行数**: ~160行
**原始位置**: 1142-1297行

---

### 5. 人员沟通适配器 (people_communication_adapter.py)
**职责**: 处理与其他人员的沟通交互
**核心功能**:
- `communicate_with_a_people()` - 与人沟通
- `talk_to_a_people()` - 向人发送消息
- `ask_agent_to_pick_people_list()` - 选择沟通对象
- `handle_agent_pick_people_list_result()` - 处理选择结果
- `ask_agent_to_review_conversation()` - 审查对话
- `handle_agent_review_conversation_result()` - 处理审查结果

**依赖关系**:
- 依赖: agent_communication_adapter, xmpp_adapter
- 被依赖: activity_processing_adapter, trading_adapter

**代码行数**: ~400行
**原始位置**: 1629-2234行, 部分在1298-1314行

---

### 6. 工具管理适配器 (tool_management_adapter.py)
**职责**: 工具的选择、调用和管理
**核心功能**:
- `get_tool_list()` - 获取工具列表
- `get_plugin_tool_list()` - 获取插件工具
- `get_service_list()` - 获取服务列表
- `ask_agent_to_pick_a_tool()` - 选择工具
- `handle_agent_pick_a_tool_result()` - 处理选择结果
- `call_tool()` - 调用工具
- `call_built_in_function()` - 调用内置功能

**依赖关系**:
- 依赖: agent_communication_adapter
- 被依赖: activity_processing_adapter

**代码行数**: ~200行
**原始位置**: 1513-1580行, 1874-1981行

---

### 7. 地点选择适配器 (place_selection_adapter.py)
**职责**: 地点的查询和选择
**核心功能**:
- `get_place_list()` - 获取地点列表
- `ask_agent_to_pick_place_list()` - 选择地点
- `handle_agent_pick_place_list_result()` - 处理选择结果
- `move_to_a_place()` - 移动到地点
- `handle_arrived_at_place()` - 到达地点处理

**依赖关系**:
- 依赖: agent_communication_adapter, movement_adapter
- 被依赖: activity_processing_adapter

**代码行数**: ~120行
**原始位置**: 1581-1589行, 1813-1873行

---

### 8. 交易系统适配器 (trading_adapter.py)
**职责**: 处理工具/技能交易相关功能
**核心功能**:
- `tool_trade_show()` - 展示工具详情
- `tool_trade_order()` - 下单
- `tool_trade_order_confirm()` - 确认订单
- `tool_trade_send_tool()` - 发送工具
- `send_pay()` - 发送付款
- `handle_pay_received()` - 处理收款
- `handle_send_goods()` - 处理发货
- `tool_trade_receive_tool()` - 接收工具
- Bargaining相关函数

**依赖关系**:
- 依赖: people_communication_adapter, agent_communication_adapter
- 被依赖: xmpp_message_adapter

**代码行数**: ~400行
**原始位置**: 2480-2880行

---

### 9. XMPP消息适配器 (xmpp_message_adapter.py)
**职责**: XMPP消息的接收、发送和处理
**核心功能**:
- `receiveMessage()` - 接收消息
- `handle_receiveMessage()` - 处理接收的消息
- `sendMessage()` - 发送消息
- `send_xmpp_message()` - 发送XMPP消息
- `_resolve_recipient()` - 解析接收者
- `_save_message_to_database()` - 保存消息到数据库
- `_update_ui_with_sent_message()` - 更新UI

**依赖关系**:
- 依赖: xmpp_manager, ui_adapter, trading_adapter
- 被依赖: people_communication_adapter

**代码行数**: ~300行
**原始位置**: 3765-4061行

---

### 10. 消息协议解析适配器 (message_protocol_adapter.py)
**职责**: 解析各种消息协议格式
**核心功能**:
- `get_tool_list_in_message()` - 提取工具列表
- `get_tool_order_in_message()` - 提取订单信息
- `get_order_confirm_in_message()` - 提取确认信息
- `get_tool_mcp_in_message()` - 提取MCP信息
- `get_tool_inquiry_in_message()` - 提取询价信息
- `get_buyer_bargain_in_message()` - 提取买家议价
- `get_seller_bargain_in_message()` - 提取卖家议价
- `check_*_in_received()` - 各种检查函数

**依赖关系**:
- 依赖: 无
- 被依赖: xmpp_message_adapter, trading_adapter

**代码行数**: ~220行
**原始位置**: 2881-3095行

---

### 11. 资源管理适配器 (resource_management_adapter.py)
**职责**: 用户资源数据的保存和加载
**核心功能**:
- `save_all_user_data()` - 保存所有用户数据
- `load_all_user_data()` - 加载所有用户数据
- `_parse_position_data()` - 解析位置数据
- `decline_energy()` - 减少体力
- `decline_life()` - 减少生命值
- `add_money()` - 增加金钱

**依赖关系**:
- 依赖: aichatcfg_record, ui_adapter
- 被依赖: 初始化流程

**代码行数**: ~120行
**原始位置**: 3663-3763行

---

### 12. 技能服务适配器 (skill_service_adapter.py)
**职责**: 技能和服务的使用、安装
**核心功能**:
- `ask_agent_to_use_service()` - 使用服务
- `on_ask_agent_to_use_service_return()` - 服务使用返回
- `ask_agent_to_use_skill()` - 使用技能
- `on_ask_agent_to_use_skill_return()` - 技能使用返回
- `send_skill()` - 发送技能
- `create_skill_cfg()` - 创建技能配置
- `create_skill_zip()` - 创建技能压缩包
- `skill_install()` - 安装技能
- `received_skill()` - 接收技能

**依赖关系**:
- 依赖: agent_communication_adapter
- 被依赖: trading_adapter

**代码行数**: ~280行
**原始位置**: 2384-2479行, 3097-3367行

---

### 13. 辅助工具适配器 (utility_adapter.py)
**职责**: 提供通用辅助功能
**核心功能**:
- `http_request()` - HTTP请求
- `get_people_nearby()` - 获取附近的人
- `get_people_by_distance()` - 按距离获取人员
- `get_nearest_people()` - 获取最近的人
- `calculate_pos()` - 计算位置
- `download_file()` - 下载文件
- `unzip_file()` - 解压文件
- `get_dict_by_id()` - 根据ID获取字典
- `remove_dict_from_list()` - 从列表移除字典
- `are_lists_of_dicts_equal()` - 比较字典列表

**依赖关系**:
- 依赖: 无
- 被依赖: 多个模块

**代码行数**: ~180行
**原始位置**: 分散在多处

---

## 二、重构实施步骤

### 阶段1: 创建基础适配器（第1-2天）
1. 创建 `utility_adapter.py` - 无依赖，优先创建
2. 创建 `message_protocol_adapter.py` - 无依赖
3. 创建 `resource_management_adapter.py` - 依赖少

### 阶段2: 创建核心适配器（第3-4天）
4. 创建 `agent_communication_adapter.py` - 核心依赖
5. 创建 `movement_adapter.py` - 基础功能
6. 创建 `place_selection_adapter.py` - 依赖movement

### 阶段3: 创建业务适配器（第5-7天）
7. 创建 `tool_management_adapter.py` - 依赖agent_communication
8. 创建 `people_communication_adapter.py` - 依赖agent_communication
9. 创建 `xmpp_message_adapter.py` - 依赖people_communication
10. 创建 `trading_adapter.py` - 依赖people_communication

### 阶段4: 创建高级适配器（第8-9天）
11. 创建 `skill_service_adapter.py` - 依赖agent_communication
12. 创建 `task_management_adapter.py` - 依赖agent_communication
13. 创建 `activity_processing_adapter.py` - 依赖多个模块

### 阶段5: 重构主类和测试（第10-12天）
14. 重构 `AISocialEngine` 主类，使用各个适配器
15. 测试 POST /api/sns/start-engine 接口
16. 集成测试和bug修复

---

## 三、代码风格规范

参考 `ui_adapter.py` 的风格：

```python
class XxxAdapter:
    """
    适配器说明文档
    """

    def __init__(self, parent):
        """初始化适配器"""
        self.parent = parent
        self.logger = logging.getLogger(__name__)

    def public_method(self, param1, param2):
        """
        公共方法说明

        Args:
            param1: 参数1说明
            param2: 参数2说明

        Returns:
            返回值说明
        """
        # 实现代码
        pass

    def _private_method(self):
        """私有方法说明"""
        pass
```

### 关键规范：
1. 所有适配器都接收 `parent` 参数
2. 通过 `self.parent` 访问主类的数据和方法
3. 使用 `self.logger` 进行日志记录
4. 公共方法使用完整的文档字符串
5. 私有方法使用下划线前缀
6. 异步方法使用 `async def`
7. 使用 `asyncio.create_task()` 创建后台任务

---

## 四、依赖关系图

```
AISocialEngine (主类)
├── utility_adapter (工具)
├── message_protocol_adapter (协议解析)
├── resource_management_adapter (资源管理)
├── agent_communication_adapter (Agent通信)
│   ├── task_management_adapter (任务管理)
│   ├── tool_management_adapter (工具管理)
│   ├── people_communication_adapter (人员沟通)
│   │   └── xmpp_message_adapter (XMPP消息)
│   │       └── trading_adapter (交易系统)
│   ├── skill_service_adapter (技能服务)
│   └── activity_processing_adapter (活动处理)
│       ├── movement_adapter (移动管理)
│       └── place_selection_adapter (地点选择)
└── ui_adapter (UI适配器 - 已存在)
```

---

## 五、接口兼容性保证

### 关键接口保持不变：
1. `async def start()` - 启动引擎
2. `async def stop()` - 停止引擎
3. `def get_status()` - 获取状态
4. `async def receiveMessage(event)` - 接收消息
5. `def sendMessage(content, ...)` - 发送消息

### 数据库操作保持不变：
- 所有 `query_*` 和 `update_*` 函数调用保持原样
- `aichatcfg_record` 的访问方式保持不变

---

## 六、测试策略

### 单元测试：
- 每个适配器独立测试
- Mock parent对象
- 测试核心功能

### 集成测试：
- 测试适配器间的协作
- 测试完整的业务流程

### 接口测试：
- 重点测试 POST /api/sns/start-engine
- 验证前后端通信正常
- 验证数据库操作正确

---

## 七、风险控制

### 高风险点：
1. Agent通信流程 - 核心功能，需仔细测试
2. XMPP消息处理 - 涉及实时通信
3. 交易系统 - 涉及金钱和资源

### 降低风险措施：
1. 分阶段实施，每个阶段都进行测试
2. 保留原始代码作为备份
3. 使用Git分支进行开发
4. 关键功能添加详细日志
5. 编写回滚方案

---

## 八、预期收益

### 代码质量提升：
- 单个文件从4280行降至~300行
- 职责清晰，易于维护
- 降低代码耦合度

### 开发效率提升：
- 新功能开发更快
- Bug定位更准确
- 代码复用性提高

### 系统可扩展性：
- 易于添加新的适配器
- 易于替换特定模块
- 支持插件化架构
