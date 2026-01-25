# AISocialEngine 类代码重组计划

## 概述
本文档说明 `ai_social_engine_adapter.py` 中 `AISocialEngine` 类的重组方案。

## 重组目标
1. 将功能相近的函数分组归类
2. 按业务模块划分区块
3. 添加清晰的注释说明每个区块功能
4. 为后续拆分为独立文件做准备

## 模块分类

### 模块1: 核心生命周期管理 (Core Lifecycle)
**行数范围**: 约 100-150 行
**功能说明**:
- 类的初始化、属性设置
- 异步初始化方法
- 启动和停止控制
- 状态管理和获取
- 用户数据的加载和保存
- 配置属性更新处理

**包含函数**:
- `__init__()` - 类初始化
- `async_init()` - 异步初始化
- `start()` - 启动引擎
- `stop()` - 停止引擎
- `_run_task_loop()` - 任务处理循环
- `get_status()` - 获取状态
- `start_task()` - 开始任务
- `stop_task()` - 停止任务
- `load_all_user_data()` - 加载用户数据
- `save_all_user_data()` - 保存用户数据
- `_parse_position_data()` - 解析位置数据
- `handle_aichatcfg_property_updated()` - 处理配置更新
- `decline_energy()` - 能量衰减
- `decline_life()` - 生命值衰减
- `set_current_task_record()` - 设置当前任务记录

---

### 模块2: AI代理交互核心 (AI Interaction Core)
**行数范围**: 约 300-400 行
**功能说明**:
- 向AI大模型发送请求
- 处理AI返回的指示
- 构建提示词内容
- 解析AI响应
- 命令状态管理

**包含函数**:
- `ask_agent_and_get_instruction()` - 请求AI指示
- `on_agent_return_instruction()` - 处理AI返回
- `compose_full_ask_content()` - 构建完整请求内容
- `compose_full_ask_content_human()` - 构建人类指令请求
- `get_next_action()` - 获取下一步行动
- `get_current_task_list()` - 获取当前任务列表
- `think()` - 思考处理

---

### 模块3: 任务规划与执行 (Task Planning & Execution)
**行数范围**: 约 200-250 行
**功能说明**:
- 任务分解
- 任务规划
- 任务更新和调整
- 执行流程控制
- 活动处理

**包含函数**:
- `ask_agent_to_decompose_task()` - 请求分解任务
- `handle_agent_plan_task_result()` - 处理任务分解结果
- `restart_plan()` - 重启计划
- `ask_agent_to_update_task()` - 请求更新任务
- `handle_agent_update_task_result()` - 处理任务更新结果
- `ask_agent_instruction_to_process_activity()` - 请求处理活动指令
- `handle_ask_agent_instruction_to_process_activity()` - 处理活动指令
- `ask_agent_instruction_to_process_human_instruction()` - 请求处理人类指令
- `parse_agent_instruction_for_process_activity()` - 解析活动指令
- `handle_parse_agent_instruction_for_process_activity()` - 处理解析的活动指令
- `parse_agent_instruction_for_process_human_instruction()` - 解析人类指令

---

### 模块4: 社交关系与沟通 (Social Interaction & Communication)
**行数范围**: 约 600-700 行
**功能说明**:
- 人员选择和管理
- 对话流程控制
- 聊天记录管理
- XMPP消息发送和接收
- 对话审查和评价
- 人工指令处理

**包含函数**:
- `ask_agent_to_pick_people_list()` - 请求选择人员
- `ask_agent_start_to_talk_to_a_people()` - 请求开始交谈
- `ask_agent_start_to_sell_to_a_people()` - 请求开始推销
- `ask_agent_start_to_buy_from_a_people()` - 请求开始购买
- `handle_agent_pick_people_list_result()` - 处理人员选择结果
- `handle_ask_agent_start_to_talk_to_a_people_result()` - 处理交谈结果
- `handle_ask_agent_start_to_sell_to_a_people_result()` - 处理推销结果
- `handle_ask_agent_start_to_buy_from_a_people_result()` - 处理购买结果
- `talk_to_a_people()` - 与人员交谈
- `receiveMessage()` - 接收消息
- `handle_receiveMessage()` - 处理接收的消息
- `sendMessage()` - 发送消息
- `send_xmpp_message()` - 发送XMPP消息
- `_resolve_recipient()` - 解析接收者
- `_save_message_to_database()` - 保存消息到数据库
- `_update_ui_with_sent_message()` - 更新UI显示
- `ask_agent_to_review_conversation()` - 请求审查对话
- `ask_agent_to_review_conversation_sell()` - 请求审查销售对话
- `ask_agent_to_review_conversation_buy()` - 请求审查购买对话
- `handle_agent_review_conversation_result()` - 处理对话审查结果
- `handle_agent_review_conversation_result_final()` - 处理最终对话结果
- `handle_agent_review_conversation_sell_result()` - 处理销售对话结果
- `handle_agent_review_conversation_sell_result_final()` - 处理最终销售对话结果
- `communicate_with_a_people()` - 与人员沟通
- `sell_to_a_people()` - 向人员推销
- `buy_from_a_people()` - 向人员购买
- `ask_agent_to_bargain_for_buyer()` - 请求买方议价
- `ask_agent_to_bargain_for_seller()` - 请求卖方议价
- `handle_ask_agent_to_bargain_for_buyer_result()` - 处理买方议价结果
- `handle_ask_agent_to_bargain_for_seller_result()` - 处理卖方议价结果
- `handle_agent_think_after_conversation_result()` - 处理对话后思考
- `ask_human_instruction()` - 请求人类指令
- `handle_human_instruction()` - 处理人类指令
- `ask_other_people_for_help()` - 请求他人帮助
- `ask_a_people_for_help()` - 请求某人帮助
- `ask_people_help_success()` - 处理帮助成功
- `ask_people_help_fail()` - 处理帮助失败
- `get_people_nearby()` - 获取附近人员
- `get_people_by_distance()` - 按距离获取人员
- `handle_the_help_summary()` - 处理帮助摘要
- `analyze_help_summary()` - 分析帮助摘要

---

### 模块5: 位置与移动服务 (Location & Movement Services)
**行数范围**: 约 300-350 行
**功能说明**:
- 地理位置计算
- 路径规划
- 移动操作
- 地点选择
- 地图交互
- 坐标转换

**包含函数**:
- `ask_agent_to_pick_place_list()` - 请求选择地点
- `handle_agent_pick_place_list_result()` - 处理地点选择结果
- `move_ahead()` - 向前移动
- `go_around()` - 随机移动
- `move_by_route()` - 按路线移动
- `move_on()` - 继续
- `move_on_route()` - 继续路线
- `move_on_people()` - 继续走向人员
- `explore_the_map()` - 探索地图
- `handle_arrived_at_place()` - 处理到达地点
- `check_place()` - 检查地点
- `initial_bearing()` - 计算初始方位角
- `calculate_pos()` - 计算位置
- `update_after_moving()` - 移动后更新
- `get_nearest_people()` - 获取最近人员
- `get_place_list()` - 获取地点列表
- `send_msg_to_map()` - 发送消息到地图
- `show_status_on_map()` - 在地图显示状态
- `show_alert_on_map()` - 在地图显示警告

---

### 模块6: 工具与服务集成 (Tool & Service Integration)
**行数范围**: 约 400-500 行
**功能说明**:
- 工具选择和调用
- 第三方服务调用
- 技能执行
- HTTP请求处理
- 服务结果处理
- 工具列表管理

**包含函数**:
- `ask_agent_to_pick_a_tool()` - 请求选择工具
- `ask_agent_to_pick_a_tool_to_buy()` - 请求选择购买工具
- `handle_agent_pick_a_tool_result()` - 处理工具选择结果
- `handle_agent_pick_a_tool_to_buy_result()` - 处理购买工具选择结果
- `ask_agent_to_run_a_tool()` - 请求运行工具
- `ask_agent_to_run_a_tool_sync()` - 同步请求运行工具
- `call_tool()` - 调用工具
- `call_built_in_function()` - 调用内置函数
- `check_in_at_a_place()` - 在某地点签到
- `get_a_clue_at_a_place()` - 在某地点获取线索
- `ask_agent_to_use_service()` - 请求使用服务
- `on_ask_agent_to_use_service_return()` - 处理服务使用返回
- `parse_content_to_call_service()` - 解析服务调用内容
- `call_service()` - 调用服务
- `handle_service_called_result()` - 处理服务调用结果
- `ask_agent_to_use_skill()` - 请求使用技能
- `on_ask_agent_to_use_skill_return()` - 处理技能使用返回
- `parse_content_to_code()` - 解析代码内容
- `execute_skill()` - 执行技能
- `handle_skill_executed_result()` - 处理技能执行结果
- `handle_ask_agent_to_use_skill_return()` - 处理技能使用返回
- `get_ability_list()` - 获取能力列表
- `get_skill_list()` - 获取技能列表
- `get_plugin_tool_list()` - 获取插件工具列表
- `get_service_list()` - 获取服务列表
- `update_service_list()` - 更新服务列表
- `get_tool_list()` - 获取工具列表
- `get_tool_list_for_trade()` - 获取交易工具列表
- `get_mcp_list_for_trade()` - 获取MCP交易列表
- `get_dict_by_id()` - 根据ID获取字典
- `http_request()` - HTTP请求
- `use_tools()` - 使用工具
- `pay_to_a_people()` - 支付给某人
- `send_good()` - 发送商品
- `get_guidance()` - 获取导航
- `set_food_order()` - 设置外卖订单
- `set_taxi_order()` - 设置出租车订单
- `call_a_doctor()` - 呼叫医生
- `show_information()` - 显示信息
- `update_skill()` - 更新技能

---

### 模块7: 交易系统 (Transaction System)
**行数范围**: 约 700-800 行
**功能说明**:
- 技能交易
- 工具交易
- 订单管理
- 支付处理
- 议价流程
- 文件传输
- 交易状态检查
- 消息解析

**包含函数**:
- `tool_trade_show()` - 展示工具交易
- `tool_trade_order()` - 工具订单
- `tool_trade_order_confirm()` - 工具订单确认
- `tool_trade_send_tool()` - 发送工具
- `tool_trade_receive_tool()` - 接收工具
- `tool_trade_inquiry()` - 工具询价
- `tool_trade_bargain_for_buyer()` - 买方议价
- `tool_trade_bargain_for_seller()` - 卖方议价
- `tool_trade_send_bargain_for_buyer()` - 发送买方议价
- `tool_trade_send_bargain_for_seller()` - 发送卖方议价
- `send_pay()` - 发送支付
- `handle_pay_received()` - 处理接收支付
- `handle_send_goods()` - 处理发送商品
- `handle_good_received()` - 处理接收商品
- `send_skill()` - 发送技能
- `create_skill_cfg()` - 创建技能配置
- `create_skill_zip()` - 创建技能压缩包
- `received_skill()` - 接收技能
- `check_skill()` - 检查技能
- `skill_install()` - 技能安装
- `unzip_file()` - 解压文件
- `download_file()` - 下载文件
- `get_url_from_msg()` - 从消息获取URL
- `tool_trade_buy()` - 工具购买
- `tool_trade_sell()` - 工具销售
- `tool_trade_pay()` - 工具支付
- `tool_trade_paid()` - 工具已支付
- `add_money()` - 添加金钱
- `check_tool_for_buy()` - 检查购买工具
- `check_tool_for_buyer_bargain()` - 检查买方议价
- `check_tool_for_seller_bargain()` - 检查卖方议价
- `check_tool_for_inquiry()` - 检查询价
- `check_tool_for_order()` - 检查订单
- `check_tool_for_order_confirm()` - 检查订单确认
- `check_tool_for_receive()` - 检查接收
- `check_tool_for_trade()` - 检查交易
- `check_tool_for_download()` - 检查下载
- `check_tool_for_end()` - 检查结束
- `check_pay_in_received()` - 检查接收支付
- `check_good_in_received()` - 检查接收商品
- `check_buy_in_received()` - 检查接收购买
- `get_tool_list_in_message()` - 从消息获取工具列表
- `get_tool_order_in_message()` - 从消息获取订单
- `get_order_confirm_in_message()` - 从消息获取订单确认
- `get_tool_mcp_in_message()` - 从消息获取MCP工具
- `get_tool_inquiry_in_message()` - 从消息获取询价
- `get_buyer_bargain_in_message()` - 从消息获取买方议价
- `get_seller_bargain_in_message()` - 从消息获取卖方议价
- `get_tool_url_in_message()` - 从消息获取工具URL
- `get_tool_url_in_message_v2()` - 从消息获取工具URL V2
- `get_tool_confirm_in_message()` - 从消息获取工具确认
- `initiate_tool_trade()` - 发起工具交易
- `respond_to_skill_trade()` - 响应技能交易
- `on_agent_make_deal_finished()` - 处理交易完成
- `_parse_decision()` - 解析决策
- `_handle_skill_exchange()` - 处理技能交换
- `_handle_token_purchase()` - 处理代币购买
- `remove_dict_from_list()` - 从列表移除字典
- `on_human_confirm_skill()` - 确认技能
- `on_human_reject_skill()` - 拒绝技能
- `ask_agent_to_arrange_function_list()` - 请求安排功能列表
- `handle_agent_arrange_function_list_result()` - 处理功能列表结果
- `move_to_a_place()` - 移动到某地
- `get_people_list()` - 获取人员列表
- `are_lists_of_dicts_equal()` - 检查字典列表是否相等
- `get_balance()` - 获取余额
- `update_balance()` - 更新余额
- `add_friend()` - 添加好友
- `write_task_plan_to_pane()` - 写入任务计划
- `write_task_process_to_pane()` - 写入任务过程
- `write_thinking_process_to_pane()` - 写入思考过程
- `write_on_going_process_to_pane()` - 写入进行中过程
- `get_task_process_history()` - 获取任务历史
- `get_on_going_process()` - 获取进行中状态
- `_send_to_frontend()` - 发送到前端
- `handle_event_before_decistion()` - 处理决策前事件
- `handle_event_before_decistion_result()` - 处理决策前事件结果
- `handle_event_after_decistion()` - 处理决策后事件
- `handle_event_after_decistion_result()` - 处理决策后事件结果
- `handle_event_receive_msg()` - 处理接收消息事件
- `handle_event_receive_msg_result()` - 处理接收消息事件结果
- `handle_event_before_send_msg()` - 处理发送消息前事件
- `handle_event_before_send_msg_result()` - 处理发送消息前事件结果

---

## 执行计划

由于文件太大（4280行），重组将通过以下步骤完成：

### 步骤1: 分析和分类
✅ 已完成 - 所有函数已按功能模块分类

### 步骤2: 创建重组文件
🔄 进行中 - 将按照上述模块结构重新组织代码

### 步骤3: 添加区块注释
📝 待执行 - 为每个模块添加清晰的注释说明

### 步骤4: 验证完整性
📋 待执行 - 确保所有函数都已正确移位，无遗漏

---

## 注意事项

1. **代码完整性**: 所有函数仅移动位置，代码逻辑、参数、返回值保持100%不变
2. **依赖关系**: 函数移动时考虑调用关系，底层函数在前，高层函数在后
3. **注释格式**: 统一使用以下格式的区块注释：

```python
# ============================================================================
# 模块X: [模块名称]
# 功能: [功能说明]
# 包含函数数: [数量]
# ============================================================================
```

4. **兼容性**: 保持所有原有的导入语句、类定义、枚举定义不变

---

## 后续拆分建议

重组完成后，建议按照以下方式拆分为独立文件：

```
backend/modules/sns/
├── ai_social_engine_adapter.py          # 主入口（组合模式）
├── core_lifecycle_adapter.py             # 核心生命周期管理
├── ai_interaction_adapter.py            # AI代理交互核心
├── task_execution_adapter.py            # 任务规划与执行
├── social_interaction_adapter.py         # 社交关系与沟通
├── location_movement_adapter.py          # 位置与移动服务
├── tool_service_adapter.py              # 工具与服务集成
└── trade_transaction_adapter.py         # 交易系统
```

---

**生成时间**: 2025年
**重组者**: AI Assistant
