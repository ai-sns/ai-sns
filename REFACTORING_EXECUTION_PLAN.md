================================================================================
重构执行计划
================================================================================


## activity_adapter
待处理方法: 2个

### 优先级1: 大型方法 (>20行)
- [ ] parse_agent_instruction_for_process_human_instruction (45行, line 1148)

### 优先级2: 小型方法 (<=20行)
- [ ] parse_agent_instruction_for_process_activity (10行, line 600)


## movement_adapter
待处理方法: 5个

### 优先级2: 小型方法 (<=20行)
- [ ] move_on (7行, line 2908)
- [ ] move_on_people (12行, line 2924)
- [ ] move_on_route (9行, line 2915)
- [ ] move_to_a_place (8行, line 1037)
- [ ] remove_dict_from_list (11行, line 2774)


## people_adapter
待处理方法: 21个

### 优先级1: 大型方法 (>20行)
- [ ] ask_agent_start_to_buy_from_a_people_sync (69行, line 1469)
- [ ] handle_ask_agent_start_to_buy_from_a_people_result (46行, line 1595)
- [ ] get_people_by_distance (33行, line 2855)
- [ ] get_nearest_people (28行, line 2936)
- [ ] talk_to_a_people (25行, line 1012)

### 优先级2: 小型方法 (<=20行)
- [ ] ask_a_people_for_help (4行, line 2840)
- [ ] ask_agent_start_to_sell_to_a_people_sync (13行, line 1456)
- [ ] ask_agent_start_to_talk_to_a_people_sync (13行, line 1443)
- [ ] ask_agent_to_pick_people_list_sync (15行, line 1428)
- [ ] ask_other_people_for_help (13行, line 2827)
- [ ] ask_people_help_fail (3行, line 2847)
- [ ] ask_people_help_success (3行, line 2844)
- [ ] buy_from_a_people (5行, line 698)
- [ ] communicate_with_a_people (7行, line 686)
- [ ] get_people_list (14行, line 970)
- [ ] get_people_nearby (5行, line 2850)
- [ ] handle_agent_pick_people_list_result (19行, line 1538)
- [ ] handle_ask_agent_start_to_sell_to_a_people_result (19行, line 1576)
- [ ] handle_ask_agent_start_to_talk_to_a_people_result (19行, line 1557)
- [ ] pay_to_a_people (7行, line 709)
- [ ] sell_to_a_people (5行, line 693)


## place_adapter
待处理方法: 4个

### 优先级1: 大型方法 (>20行)
- [ ] ask_agent_to_pick_place_list_sync (42行, line 1193)

### 优先级2: 小型方法 (<=20行)
- [ ] check_place (4行, line 1093)
- [ ] handle_agent_pick_place_list_result (19行, line 1235)
- [ ] handle_arrived_at_place (6行, line 1083)


## protocol_adapter
待处理方法: 1个

### 优先级2: 小型方法 (<=20行)
- [ ] check_buy_in_received (8行, line 2630)


## resource_adapter
待处理方法: 3个

### 优先级1: 大型方法 (>20行)
- [ ] decline_life (130行, line 3068)

### 优先级2: 小型方法 (<=20行)
- [ ] add_money (11行, line 2180)
- [ ] decline_energy (6行, line 3062)


## skill_adapter
待处理方法: 20个

### 优先级1: 大型方法 (>20行)
- [ ] get_skill_list (57行, line 841)
- [ ] skill_install (54行, line 2655)
- [ ] create_skill_cfg (32行, line 2467)
- [ ] create_skill_zip (30行, line 2499)

### 优先级2: 小型方法 (<=20行)
- [ ] _handle_skill_exchange (11行, line 2763)
- [ ] call_service (19行, line 1799)
- [ ] check_skill (13行, line 2529)
- [ ] execute_skill (4行, line 1846)
- [ ] get_service_list (12行, line 924)
- [ ] handle_service_called_result (19行, line 1818)
- [ ] handle_skill_executed_result (10行, line 1850)
- [ ] on_ask_agent_to_use_service_return (5行, line 1774)
- [ ] on_ask_agent_to_use_skill_return (5行, line 1837)
- [ ] on_human_confirm_skill (4行, line 2796)
- [ ] on_human_reject_skill (3行, line 2800)
- [ ] parse_content_to_call_service (20行, line 1779)
- [ ] received_skill (14行, line 2542)
- [ ] send_skill (6行, line 2461)
- [ ] update_service_list (14行, line 936)
- [ ] update_skill (3行, line 898)


## task_adapter
待处理方法: 3个

### 优先级1: 大型方法 (>20行)
- [ ] start_task (77行, line 384)

### 优先级2: 小型方法 (<=20行)
- [ ] set_current_task_record (3行, line 465)
- [ ] stop_task (4行, line 1089)


## tool_adapter
待处理方法: 38个

### 优先级1: 大型方法 (>20行)
- [ ] get_tool_confirm_in_message (54行, line 2407)
- [ ] tool_trade_receive_tool (43行, line 2061)
- [ ] ask_agent_to_pick_a_tool_sync (40行, line 1254)
- [ ] tool_trade_send_tool (36行, line 1918)
- [ ] call_tool (35行, line 1327)
- [ ] handle_agent_pick_a_tool_result (33行, line 1294)
- [ ] tool_trade_order (30行, line 1872)
- [ ] tool_trade_buy (28行, line 2191)
- [ ] tool_trade_sell (27行, line 2219)
- [ ] get_plugin_tool_list (23行, line 901)
- [ ] tool_trade_send_bargain_for_buyer (23行, line 2134)
- [ ] tool_trade_send_bargain_for_seller (23行, line 2157)
- [ ] tool_trade_inquiry (22行, line 2104)
- [ ] handle_agent_pick_a_tool_to_buy_result (21行, line 1407)

### 优先级2: 小型方法 (<=20行)
- [ ] ask_agent_to_run_a_tool_sync (7行, line 817)
- [ ] check_tool_for_buy (4行, line 2556)
- [ ] check_tool_for_buyer_bargain (4行, line 2560)
- [ ] check_tool_for_download (12行, line 2590)
- [ ] check_tool_for_end (4行, line 2602)
- [ ] check_tool_for_inquiry (4行, line 2568)
- [ ] check_tool_for_order (4行, line 2572)
- [ ] check_tool_for_order_confirm (4行, line 2576)
- [ ] check_tool_for_receive (4行, line 2580)
- [ ] check_tool_for_seller_bargain (4行, line 2564)
- [ ] check_tool_for_trade (6行, line 2584)
- [ ] get_tool_inquiry_in_message (20行, line 2325)
- [ ] get_tool_list_for_trade (6行, line 954)
- [ ] get_tool_mcp_in_message (20行, line 2305)
- [ ] get_tool_order_in_message (20行, line 2265)
- [ ] get_tool_url_in_message (11行, line 2385)
- [ ] get_tool_url_in_message_v2 (11行, line 2396)
- [ ] tool_trade_bargain_for_buyer (4行, line 2126)
- [ ] tool_trade_bargain_for_seller (4行, line 2130)
- [ ] tool_trade_order_confirm (16行, line 1902)
- [ ] tool_trade_paid (3行, line 2255)
- [ ] tool_trade_pay (9行, line 2246)
- [ ] tool_trade_show (12行, line 1860)
- [ ] use_tools (6行, line 703)


## trading_adapter
待处理方法: 14个

### 优先级1: 大型方法 (>20行)
- [ ] handle_pay_received (42行, line 1977)
- [ ] handle_send_goods (25行, line 2019)
- [ ] send_pay (23行, line 1954)

### 优先级2: 小型方法 (<=20行)
- [ ] check_good_in_received (20行, line 2610)
- [ ] get_buyer_bargain_in_message (20行, line 2345)
- [ ] get_mcp_list_for_trade (6行, line 960)
- [ ] get_order_confirm_in_message (20行, line 2285)
- [ ] get_seller_bargain_in_message (20行, line 2365)
- [ ] handle_ask_agent_to_bargain_for_buyer_result (18行, line 1737)
- [ ] handle_ask_agent_to_bargain_for_seller_result (19行, line 1755)
- [ ] handle_good_received (17行, line 2044)
- [ ] send_good (16行, line 716)
- [ ] set_food_order (8行, line 756)
- [ ] set_taxi_order (19行, line 764)


## utility_adapter
待处理方法: 58个

### 优先级1: 大型方法 (>20行)
- [ ] __init__ (310行, line 63)
- [ ] __getattr__ (49行, line 3355)
- [ ] handle_agent_review_conversation_result_final (46行, line 1650)
- [ ] _parse_position_data_impl (44行, line 3467)
- [ ] _parse_position_data (43行, line 3019)
- [ ] handle_aichatcfg_property_updated (41行, line 1097)
- [ ] __setattr__ (39行, line 3404)
- [ ] explore_the_map (38行, line 1045)
- [ ] compose_full_ask_content (32行, line 568)
- [ ] get_dict_by_id (32行, line 1375)
- [ ] handle_agent_review_conversation_sell_result_final (32行, line 1705)
- [ ] http_request (30行, line 2981)
- [ ] think (25行, line 500)
- [ ] on_agent_make_deal_finished (25行, line 2717)
- [ ] get_guidance (24行, line 732)
- [ ] _resolve_recipient (24行, line 3226)
- [ ] _parse_decision (21行, line 2742)

### 优先级2: 小型方法 (<=20行)
- [ ] __getitem__ (13行, line 3443)
- [ ] __init__ (12行, line 3299)
- [ ] __setitem__ (11行, line 3456)
- [ ] _emit_property_updated (13行, line 3331)
- [ ] _handle_token_purchase (11行, line 2785)
- [ ] _load_record (7行, line 3344)
- [ ] _refresh_record (4行, line 3351)
- [ ] add_friend (3行, line 1009)
- [ ] analyze_help_summary (7行, line 2901)
- [ ] are_lists_of_dicts_equal (17行, line 984)
- [ ] ask_human_instruction (10行, line 2803)
- [ ] calculate_pos (4行, line 2964)
- [ ] call_a_doctor (9行, line 783)
- [ ] call_built_in_function (13行, line 1362)
- [ ] compose_full_ask_content_human (10行, line 1138)
- [ ] connect (10行, line 3311)
- [ ] disconnect (10行, line 3321)
- [ ] download_file (13行, line 2642)
- [ ] get_ability_list (9行, line 832)
- [ ] get_balance (5行, line 1001)
- [ ] get_status (11行, line 373)
- [ ] get_url_from_msg (4行, line 2638)
- [ ] handle_agent_review_conversation_result (9行, line 1641)
- [ ] handle_agent_review_conversation_sell_result (9行, line 1696)
- [ ] handle_as_coint (3行, line 2258)
- [ ] handle_event_after_decistion_result (4行, line 640)
- [ ] handle_event_before_decistion (7行, line 622)
- [ ] handle_event_before_decistion (7行, line 806)
- [ ] handle_event_before_decistion_result (11行, line 629)
- [ ] handle_event_before_decistion_result (4行, line 813)
- [ ] handle_event_before_send_msg (7行, line 656)
- [ ] handle_event_before_send_msg_result (7行, line 663)
- [ ] handle_event_receive_msg (7行, line 644)
- [ ] handle_event_receive_msg_result (5行, line 651)
- [ ] handle_human_instruction (14行, line 2813)
- [ ] handle_the_help_summary (13行, line 2888)
- [ ] parse_content_to_code (4行, line 1842)
- [ ] send_msg_to_map (14行, line 792)
- [ ] unzip_file (8行, line 2709)
- [ ] update_after_moving (13行, line 2968)
- [ ] update_balance (3行, line 1006)


## xmpp_adapter
待处理方法: 3个

### 优先级1: 大型方法 (>20行)
- [ ] _save_message_to_database (25行, line 3250)
- [ ] send_xmpp_message (24行, line 3198)
- [ ] _update_ui_with_sent_message (24行, line 3275)

================================================================================