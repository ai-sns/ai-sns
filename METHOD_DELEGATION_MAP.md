# AISocialEngine 方法委托映射

## 需要替换的方法列表

### 1. Utility方法 -> utility_adapter
- `http_request()` -> `self.utility_adapter.http_request()`
- `get_dict_by_id()` -> `self.utility_adapter.get_dict_by_id()`
- `remove_dict_from_list()` -> `self.utility_adapter.remove_dict_from_list()`
- `are_lists_of_dicts_equal()` -> `self.utility_adapter.are_lists_of_dicts_equal()`
- `get_people_by_distance()` -> `self.utility_adapter.get_people_by_distance()`
- `get_people_nearby()` -> `self.utility_adapter.get_people_nearby()`
- `download_file()` -> `self.utility_adapter.download_file()`
- `unzip_file()` -> `self.utility_adapter.unzip_file()`

### 2. Protocol方法 -> protocol_adapter
- `get_tool_list_in_message()` -> `self.protocol_adapter.get_tool_list_in_message()`
- `get_tool_order_in_message()` -> `self.protocol_adapter.get_tool_order_in_message()`
- `get_order_confirm_in_message()` -> `self.protocol_adapter.get_order_confirm_in_message()`
- `get_tool_mcp_in_message()` -> `self.protocol_adapter.get_tool_mcp_in_message()`
- `check_pay_in_received()` -> `self.protocol_adapter.check_pay_in_received()`
- `check_good_in_received()` -> `self.protocol_adapter.check_good_in_received()`
- `check_tool_for_buy()` -> `self.protocol_adapter.check_tool_for_buy()`

### 3. Resource方法 -> resource_adapter
- `save_all_user_data()` -> `self.resource_adapter.save_all_user_data()`
- `load_all_user_data()` -> `self.resource_adapter.load_all_user_data()`
- `decline_energy()` -> `self.resource_adapter.decline_energy()`
- `decline_life()` -> `self.resource_adapter.decline_life()`

### 4. Movement方法 -> movement_adapter
- `go_around()` -> `self.movement_adapter.go_around()`
- `move_ahead()` -> `self.movement_adapter.move_ahead()`
- `move_by_route()` -> `self.movement_adapter.move_by_route()`
- `update_after_moving()` -> `self.movement_adapter.update_after_moving()`

### 5. Agent Communication方法 -> agent_comm_adapter
- `ask_agent_and_get_instruction()` -> `self.agent_comm_adapter.ask_agent_and_get_instruction()`
- `on_agent_return_instruction()` -> `self.agent_comm_adapter.on_agent_return_instruction()`

### 6. Place Selection方法 -> place_adapter
- `get_place_list()` -> `self.place_adapter.get_place_list()`
- `ask_agent_to_pick_place_list()` -> `self.place_adapter.ask_agent_to_pick_place_list()`
- `move_to_a_place()` -> `self.place_adapter.move_to_a_place()`

### 7. Tool Management方法 -> tool_adapter
- `get_tool_list()` -> `self.tool_adapter.get_tool_list()`
- `get_service_list()` -> `self.tool_adapter.get_service_list()`
- `get_plugin_tool_list()` -> `self.tool_adapter.get_plugin_tool_list()`
- `ask_agent_to_pick_a_tool()` -> `self.tool_adapter.ask_agent_to_pick_a_tool()`
- `call_tool()` -> `self.tool_adapter.call_tool()`

### 8. People Communication方法 -> people_adapter
- `communicate_with_a_people()` -> `self.people_adapter.communicate_with_a_people()`
- `talk_to_a_people()` -> `self.people_adapter.talk_to_a_people()`
- `ask_agent_to_pick_people_list()` -> `self.people_adapter.ask_agent_to_pick_people_list()`

### 9. XMPP Message方法 -> xmpp_adapter
- `receiveMessage()` -> `self.xmpp_adapter.receiveMessage()`
- `sendMessage()` -> `self.xmpp_adapter.sendMessage()`

### 10. Trading方法 -> trading_adapter
- `tool_trade_show()` -> `self.trading_adapter.tool_trade_show()`
- `tool_trade_order()` -> `self.trading_adapter.tool_trade_order()`
- `send_pay()` -> `self.trading_adapter.send_pay()`

### 11. Skill Service方法 -> skill_adapter
- `ask_agent_to_use_service()` -> `self.skill_adapter.ask_agent_to_use_service()`
- `ask_agent_to_use_skill()` -> `self.skill_adapter.ask_agent_to_use_skill()`
- `skill_install()` -> `self.skill_adapter.skill_install()`

### 12. Task Management方法 -> task_adapter
- `ask_agent_to_decompose_task()` -> `self.task_adapter.ask_agent_to_decompose_task()`

### 13. Activity Processing方法 -> activity_adapter
- `ask_agent_instruction_to_process_activity()` -> `self.activity_adapter.ask_agent_instruction_to_process_activity()`

## 替换策略

由于文件有4280行，我们采用以下策略：

1. **保留原方法作为委托方法**：不删除原方法，而是将其实现改为调用适配器
2. **分批替换**：按适配器分组，每次替换一组方法
3. **保持接口不变**：确保所有公共方法签名保持不变

## 示例

原代码：
```python
def http_request(self, url, params=None, method="POST"):
    # 实现代码...
```

替换后：
```python
def http_request(self, url, params=None, method="POST"):
    """委托给utility_adapter"""
    return self.utility_adapter.http_request(url, params, method)
```
