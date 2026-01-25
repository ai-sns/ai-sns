================================================================================
AISocialEngine重构分析报告
================================================================================

总方法数: 199
已委托方法: 27 (13%)
待处理方法: 172 (86%)

按适配器分组的待处理方法:
--------------------------------------------------------------------------------

activity_adapter: 2个方法, 55行代码
  大型方法 (>20行):
    - parse_agent_instruction_for_process_human_instruction: 45行 (line 1148)

movement_adapter: 5个方法, 47行代码

people_adapter: 21个方法, 365行代码
  大型方法 (>20行):
    - ask_agent_start_to_buy_from_a_people_sync: 69行 (line 1469)
    - handle_ask_agent_start_to_buy_from_a_people_result: 46行 (line 1595)
    - get_people_by_distance: 33行 (line 2855)
    - get_nearest_people: 28行 (line 2936)
    - talk_to_a_people: 25行 (line 1012)

place_adapter: 4个方法, 71行代码
  大型方法 (>20行):
    - ask_agent_to_pick_place_list_sync: 42行 (line 1193)

protocol_adapter: 1个方法, 8行代码

resource_adapter: 3个方法, 147行代码
  大型方法 (>20行):
    - decline_life: 130行 (line 3068)

skill_adapter: 20个方法, 335行代码
  大型方法 (>20行):
    - get_skill_list: 57行 (line 841)
    - skill_install: 54行 (line 2655)
    - create_skill_cfg: 32行 (line 2467)
    - create_skill_zip: 30行 (line 2499)

task_adapter: 3个方法, 84行代码
  大型方法 (>20行):
    - start_task: 77行 (line 384)

tool_adapter: 38个方法, 637行代码
  大型方法 (>20行):
    - get_tool_confirm_in_message: 54行 (line 2407)
    - tool_trade_receive_tool: 43行 (line 2061)
    - ask_agent_to_pick_a_tool_sync: 40行 (line 1254)
    - tool_trade_send_tool: 36行 (line 1918)
    - call_tool: 35行 (line 1327)
    - handle_agent_pick_a_tool_result: 33行 (line 1294)
    - tool_trade_order: 30行 (line 1872)
    - tool_trade_buy: 28行 (line 2191)
    - tool_trade_sell: 27行 (line 2219)
    - get_plugin_tool_list: 23行 (line 901)
    - tool_trade_send_bargain_for_buyer: 23行 (line 2134)
    - tool_trade_send_bargain_for_seller: 23行 (line 2157)
    - tool_trade_inquiry: 22行 (line 2104)
    - handle_agent_pick_a_tool_to_buy_result: 21行 (line 1407)

trading_adapter: 14个方法, 273行代码
  大型方法 (>20行):
    - handle_pay_received: 42行 (line 1977)
    - handle_send_goods: 25行 (line 2019)
    - send_pay: 23行 (line 1954)

utility_adapter: 58个方法, 1210行代码
  大型方法 (>20行):
    - __init__: 310行 (line 63)
    - __getattr__: 49行 (line 3355)
    - handle_agent_review_conversation_result_final: 46行 (line 1650)
    - _parse_position_data_impl: 44行 (line 3467)
    - _parse_position_data: 43行 (line 3019)
    - handle_aichatcfg_property_updated: 41行 (line 1097)
    - __setattr__: 39行 (line 3404)
    - explore_the_map: 38行 (line 1045)
    - compose_full_ask_content: 32行 (line 568)
    - get_dict_by_id: 32行 (line 1375)
    - handle_agent_review_conversation_sell_result_final: 32行 (line 1705)
    - http_request: 30行 (line 2981)
    - think: 25行 (line 500)
    - on_agent_make_deal_finished: 25行 (line 2717)
    - get_guidance: 24行 (line 732)
    - _resolve_recipient: 24行 (line 3226)
    - _parse_decision: 21行 (line 2742)

xmpp_adapter: 3个方法, 73行代码
  大型方法 (>20行):
    - _save_message_to_database: 25行 (line 3250)
    - send_xmpp_message: 24行 (line 3198)
    - _update_ui_with_sent_message: 24行 (line 3275)

================================================================================