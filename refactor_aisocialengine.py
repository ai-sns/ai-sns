#!/usr/bin/env python3
"""
AISocialEngine Refactoring Script
Automatically splits AISocialEngine class into modular adapters
"""

import re
import os
from typing import Dict, List, Tuple

# Define method mappings based on the analysis report
MODULE_MAPPINGS = {
    "lifecycle_manager.py": {
        "class_name": "LifecycleManager",
        "methods": [
            "__init__",
            "async_init",
            "start",
            "stop",
            "_run_task_loop",
            "get_status",
            "start_task"
        ],
        "line_ranges": [(63, 157), (159, 228), (230, 294), (296, 318), (320, 339), (340, 349), (351, 419)]
    },
    
    "agent_communication_adapter.py": {
        "class_name": "AgentCommunicationAdapter",
        "methods": [
            "ask_agent_and_get_instruction",
            "on_agent_return_instruction",
            "set_current_task_record",
            "ask_agent_to_decompose_task",
            "handle_agent_plan_task_result",
            "ask_agent_to_update_task",
            "handle_agent_update_task_result",
            "restart_plan"
        ],
        "line_ranges": [(423, 492), (497, 604), (606, 607), (738, 746), (749, 769), (777, 834), (836, 879), (771, 774)]
    },
    
    "ui_communication_adapter.py": {
        "class_name": "UICommunicationAdapter",
        "methods": [
            "write_task_plan_to_pane",
            "_send_to_frontend",
            "write_thinking_process_to_pane",
            "write_task_process_to_pane",
            "get_task_process_history",
            "write_on_going_process_to_pane",
            "get_on_going_process",
            "show_information",
            "send_msg_to_map",
            "show_status_on_map",
            "show_alert_on_map"
        ],
        "line_ranges": [(609, 612), (614, 635), (637, 648), (651, 663), (665, 676), (678, 692), (694, 719), (721, 722), (1404, 1416), (1436, 1438), (1440, 1442)]
    },
    
    "task_executor.py": {
        "class_name": "TaskExecutor",
        "methods": [
            "think",
            "ask_agent_instruction_to_process_activity",
            "handle_ask_agent_instruction_to_process_activity",
            "compose_full_ask_content",
            "parse_agent_instruction_for_process_activity",
            "handle_parse_agent_instruction_for_process_activity",
            "get_next_action",
            "get_current_task_list",
            "ask_agent_instruction_to_process_human_instruction",
            "compose_full_ask_content_human",
            "parse_agent_instruction_for_process_human_instruction"
        ],
        "line_ranges": [(724, 735), (882, 889), (891, 902), (906, 934), (938, 945), (947, 1060), (1062, 1078), (1080, 1092), (1746, 1756), (1758, 1766), (1768, 1770)]
    },
    
    "map_navigation.py": {
        "class_name": "MapNavigation",
        "methods": [
            "go_around",
            "initial_bearing",
            "move_ahead",
            "move_by_route",
            "move_to_a_place",
            "explore_the_map",
            "handle_arrived_at_place",
            "check_place",
            "get_nearest_people",
            "calculate_pos",
            "update_after_moving",
            "move_on",
            "move_on_route",
            "move_on_people"
        ],
        "line_ranges": [(1142, 1206), (1208, 1217), (1219, 1286), (1288, 1296), (1657, 1663), (1665, 1701), (1703, 1707), (1713, 1715), (3588, 3614), (3616, 3618), (3620, 3631), (3560, 3565), (3567, 3574), (3576, 3586)]
    },
    
    "people_interaction_manager.py": {
        "class_name": "PeopleInteractionManager",
        "methods": [
            "communicate_with_a_people",
            "talk_to_a_people",
            "ask_agent_to_pick_people_list",
            "ask_agent_to_pick_people_list_sync",
            "ask_agent_start_to_talk_to_a_people",
            "ask_agent_start_to_sell_to_a_people",
            "ask_agent_start_to_buy_from_a_people",
            "ask_agent_start_to_talk_to_a_people_sync",
            "ask_agent_start_to_sell_to_a_people_sync",
            "ask_agent_start_to_buy_from_a_people_sync",
            "handle_agent_pick_people_list_result",
            "handle_ask_agent_start_to_talk_to_a_people_result",
            "handle_ask_agent_start_to_sell_to_a_people_result",
            "handle_ask_agent_start_to_buy_from_a_people_result",
            "ask_other_people_for_help",
            "ask_a_people_for_help",
            "ask_people_help_success",
            "ask_people_help_fail",
            "get_people_nearby",
            "get_people_by_distance",
            "handle_the_help_summary",
            "analyze_help_summary"
        ],
        "line_ranges": [(1298, 1301), (1632, 1655), (2103, 2116), (2048, 2061), (2118, 2129), (2131, 2142), (2144, 2155), (2063, 2074), (2076, 2087), (2089, 2100), (2158, 2175), (2177, 2194), (2196, 2213), (2215, 2233), (3479, 3490), (3492, 3494), (3496, 3497), (3499, 3500), (3502, 3505), (3507, 3538), (3540, 3551), (3553, 3558)]
    },
    
    "conversation_analyzer.py": {
        "class_name": "ConversationAnalyzer",
        "methods": [
            "ask_agent_to_review_conversation",
            "ask_agent_to_review_conversationbak",
            "ask_agent_to_review_conversation_sell",
            "ask_agent_to_review_conversation_buy",
            "handle_agent_review_conversation_result",
            "handle_agent_review_conversation_result_final",
            "handle_agent_review_conversation_sell_result",
            "handle_agent_review_conversation_sell_result_final"
        ],
        "line_ranges": [(2235, 2240), (2242, 2247), (2249, 2253), (2255, 2259), (2261, 2268), (2270, 2314), (2316, 2323), (2325, 2345)]
    },
    
    "tool_service_executor.py": {
        "class_name": "ToolServiceExecutor",
        "methods": [
            "use_tools",
            "get_tool_list",
            "get_tool_list_for_trade",
            "get_plugin_tool_list",
            "ask_agent_to_pick_a_tool",
            "ask_agent_to_pick_a_tool_sync",
            "handle_agent_pick_a_tool_result",
            "call_tool",
            "call_built_in_function",
            "get_dict_by_id",
            "ask_agent_to_run_a_tool",
            "ask_agent_to_run_a_tool_sync",
            "ask_agent_to_use_service",
            "on_ask_agent_to_use_service_return",
            "parse_content_to_call_service",
            "call_service",
            "handle_service_called_result"
        ],
        "line_ranges": [(1315, 1319), (1562, 1567), (1569, 1573), (1513, 1534), (1894, 1911), (1874, 1891), (1914, 1945), (1947, 1980), (1982, 1993), (1995, 2007), (2039, 2045), (1429, 1434), (2384, 2392), (2394, 2397), (2399, 2417), (2419, 2436), (2438, 2445)]
    },
    
    "skill_manager.py": {
        "class_name": "SkillManager",
        "methods": [
            "get_skill_list",
            "update_skill",
            "ask_agent_to_use_skill",
            "on_ask_agent_to_use_skill_return",
            "parse_content_to_code",
            "execute_skill",
            "handle_skill_executed_result",
            "create_skill_cfg",
            "create_skill_zip",
            "check_skill",
            "received_skill",
            "skill_install",
            "unzip_file",
            "on_human_confirm_skill",
            "on_human_reject_skill"
        ],
        "line_ranges": [(1453, 1508), (1510, 1511), (2447, 2455), (2457, 2460), (2462, 2464), (2466, 2468), (2470, 2478), (3103, 3133), (3135, 3163), (3165, 3176), (3178, 3190), (3307, 3359), (3361, 3367), (3448, 3450), (3452, 3453)]
    },
    
    "trade_negotiation_manager.py": {
        "class_name": "TradeNegotiationManager",
        "methods": [
            "ask_agent_to_pick_a_tool_to_buy",
            "handle_agent_pick_a_tool_to_buy_result",
            "ask_agent_to_bargain_for_buyer",
            "handle_ask_agent_to_bargain_for_buyer_result",
            "ask_agent_to_bargain_for_seller",
            "handle_ask_agent_to_bargain_for_seller_result",
            "tool_trade_show",
            "tool_trade_order",
            "tool_trade_order_confirm",
            "tool_trade_send_tool",
            "send_pay",
            "handle_pay_received",
            "handle_send_goods",
            "handle_good_received",
            "tool_trade_receive_tool",
            "tool_trade_inquiry",
            "tool_trade_bargain_for_buyer",
            "tool_trade_bargain_for_seller",
            "tool_trade_send_bargain_for_buyer",
            "tool_trade_send_bargain_for_seller",
            "add_money",
            "tool_trade_buy",
            "tool_trade_sell",
            "tool_trade_pay",
            "tool_trade_paid",
            "on_agent_make_deal_finished",
            "_parse_decision",
            "_handle_skill_exchange",
            "_handle_token_purchase",
            "remove_dict_from_list"
        ],
        "line_ranges": [(2009, 2025), (2027, 2037), (2347, 2355), (2357, 2363), (2365, 2373), (2375, 2382), (2480, 2490), (2492, 2520), (2522, 2536), (2538, 2572), (2574, 2595), (2597, 2637), (2639, 2662), (2664, 2679), (2681, 2722), (2724, 2744), (2746, 2752), (2750, 2752), (2754, 2775), (2777, 2798), (2800, 2809), (2811, 2837), (2839, 2864), (2866, 2873), (2875, 2876), (3369, 3392), (3394, 3413), (3415, 3425), (3437, 3446), (3426, 3435)]
    },
    
    "message_protocol_parser.py": {
        "class_name": "MessageProtocolParser",
        "methods": [
            "get_tool_list_in_message",
            "get_tool_order_in_message",
            "get_order_confirm_in_message",
            "get_tool_mcp_in_message",
            "get_tool_inquiry_in_message",
            "get_buyer_bargain_in_message",
            "get_seller_bargain_in_message",
            "get_tool_url_in_message",
            "get_tool_url_in_message_v2",
            "get_tool_confirm_in_message",
            "check_tool_for_buy",
            "check_tool_for_buyer_bargain",
            "check_tool_for_seller_bargain",
            "check_tool_for_inquiry",
            "check_tool_for_order",
            "check_tool_for_order_confirm",
            "check_tool_for_receive",
            "check_tool_for_trade",
            "check_tool_for_download",
            "check_tool_for_end",
            "check_pay_in_received",
            "check_good_in_received",
            "check_buy_in_received",
            "get_url_from_msg"
        ],
        "line_ranges": [(2881, 2899), (2901, 2919), (2921, 2939), (2941, 2959), (2961, 2979), (2981, 2999), (3001, 3019), (3021, 3030), (3032, 3041), (3043, 3049), (3192, 3194), (3196, 3198), (3200, 3202), (3204, 3206), (3208, 3210), (3212, 3214), (3216, 3218), (3220, 3224), (3226, 3237), (3238, 3240), (3242, 3260), (3262, 3280), (3282, 3288), (3290, 3292)]
    },
    
    "xmpp_communication_manager.py": {
        "class_name": "XMPPCommunicationManager",
        "methods": [
            "receiveMessage",
            "handle_receiveMessage",
            "send_xmpp_message",
            "sendMessage",
            "_resolve_recipient",
            "_save_message_to_database",
            "_update_ui_with_sent_message"
        ],
        "line_ranges": [(3765, 3800), (3802, 3918), (3921, 3943), (3945, 3993), (3995, 4017), (4019, 4042), (4044, 4060)]
    },
    
    "resource_data_manager.py": {
        "class_name": "ResourceManager",
        "methods": [
            "get_service_list",
            "update_service_list",
            "get_place_list",
            "get_people_list",
            "are_lists_of_dicts_equal",
            "get_balance",
            "update_balance",
            "add_friend",
            "get_ability_list",
            "save_all_user_data",
            "load_all_user_data",
            "_parse_position_data",
            "decline_energy",
            "decline_life",
            "http_request",
            "download_file",
            "get_mcp_list_for_trade"
        ],
        "line_ranges": [(1536, 1546), (1548, 1560), (1581, 1588), (1590, 1602), (1604, 1619), (1621, 1624), (1626, 1627), (1629, 1630), (1444, 1451), (3663, 3677), (3679, 3707), (3709, 3750), (3752, 3756), (3758, 3762), (3633, 3661), (3294, 3305), (1575, 1579)]
    },
    
    "event_hook_handler.py": {
        "class_name": "EventHookHandler",
        "methods": [
            "handle_event_before_decistion",
            "handle_event_before_decistion_result",
            "handle_event_after_decistion",
            "handle_event_after_decistion_result",
            "handle_event_receive_msg",
            "handle_event_receive_msg_result",
            "handle_event_before_send_msg",
            "handle_event_before_send_msg_result",
            "handle_aichatcfg_property_updated"
        ],
        "line_ranges": [(1094, 1099), (1101, 1103), (1105, 1110), (1112, 1114), (1116, 1121), (1123, 1126), (1128, 1133), (1135, 1140), (1717, 1744)]
    },
    
    "auxiliary_services.py": {
        "class_name": "AuxiliaryServices",
        "methods": [
            "sell_to_a_people",
            "buy_from_a_people",
            "pay_to_a_people",
            "send_good",
            "get_guidance",
            "set_food_order",
            "set_taxi_order",
            "call_a_doctor",
            "handle_as_coint"
        ],
        "line_ranges": [(1305, 1308), (1310, 1313), (1321, 1326), (1328, 1342), (1344, 1366), (1368, 1374), (1376, 1393), (1395, 1402), (2878, 2879)]
    }
}

def extract_method_from_file(file_path: str, start_line: int, end_line: int) -> str:
    """Extract method code from file by line range"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract lines (convert to 0-indexed)
        method_lines = lines[start_line-1:end_line]
        
        # Find the method definition line
        method_def = None
        indent_level = None
        for i, line in enumerate(method_lines):
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                method_def = i
                indent_level = len(line) - len(line.lstrip())
                break
        
        if method_def is None:
            return ""
        
        # Extract complete method including nested functions
        result_lines = [method_lines[method_def]]
        for line in method_lines[method_def+1:]:
            # Check if we've exited the method
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break
            result_lines.append(line)
        
        return ''.join(result_lines)
    except Exception as e:
        print(f"Error extracting method from {start_line}-{end_line}: {e}")
        return ""

def read_entire_file(file_path: str) -> str:
    """Read entire file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_method_by_name(content: str, method_name: str) -> Tuple[int, int, str]:
    """Find method by name and return (start_line, end_line, method_code)"""
    lines = content.split('\n')
    
    # Find method definition
    method_pattern = rf'^(async\s+)?def\s+{re.escape(method_name)}\s*\('
    
    for i, line in enumerate(lines, start=1):
        if re.search(method_pattern, line.strip()):
            # Found the method, now find its end
            indent_level = len(line) - len(line.lstrip())
            method_lines = [line]
            
            for j in range(i, len(lines)):
                next_line = lines[j]
                # Skip empty lines
                if not next_line.strip():
                    if j < len(lines) - 1:
                        method_lines.append(next_line)
                    continue
                
                # Check if we've exited the method
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_line.strip() and next_indent <= indent_level:
                    if re.search(r'^(async\s+)?def\s+\w+\s*\(', next_line.strip()):
                        break
                
                method_lines.append(next_line)
            
            return (i, i + len(method_lines) - 1, '\n'.join(method_lines))
    
    return (0, 0, "")

def create_adapter_file(class_name: str, methods_dict: Dict[str, str], output_path: str):
    """Create an adapter file with the specified methods"""
    
    template = f'''"""
{class_name} - Business Adapter for AISocialEngine
This module provides {class_name} functionality
"""
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {class_name} adapter for AISocialEngine
    Handles {class_name.replace("Manager", "").replace("Adapter", "").replace("Executor", "").lower()} related operations
    """

'''

    # Add each method
    for method_name, method_code in methods_dict.items():
        # Preserve original formatting by adding 4 spaces of indentation for each line
        lines = method_code.split('\n')
        indented_lines = []
        for i, line in enumerate(lines):
            if i == 0:
                # First line already has def, just add it
                indented_lines.append(line)
            elif line.strip():  # Non-empty line - add indentation
                indented_lines.append('    ' + line)
            else:  # Empty line
                indented_lines.append('')
        template += '\n' + '\n'.join(indented_lines) + '\n'
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"Created: {output_path}")

def main():
    """Main refactoring process"""
    
    source_file = r'c:\dev\agi-ev\ai-sns-el\backend\modules\sns\ai_social_engine_adapter.py'
    output_dir = r'c:\dev\agi-ev\ai-sns-el\backend\modules\sns\adapters'
    
    # Read source file
    print("Reading source file...")
    content = read_entire_file(source_file)
    
    # Extract imports from source
    import_section = []
    in_imports = True
    for line in content.split('\n'):
        if in_imports:
            if line.strip().startswith('class ') or line.strip().startswith('# '):
                in_imports = False
                break
            import_section.append(line)
    
    # Process each module
    for filename, module_info in MODULE_MAPPINGS.items():
        class_name = module_info["class_name"]
        method_names = module_info["methods"]
        
        print(f"\nProcessing {filename} ({class_name})...")
        
        # Extract each method
        methods_dict = {}
        for method_name in method_names:
            start_line, end_line, method_code = find_method_by_name(content, method_name)
            
            if method_code:
                # Clean method code (remove extra indentation)
                lines = method_code.split('\n')
                if lines:
                    first_line = lines[0]
                    base_indent = len(first_line) - len(first_line.lstrip())
                    
                    cleaned_lines = [first_line]
                    for line in lines[1:]:
                        if line.strip():  # Skip empty lines for indentation calculation
                            if len(line) > base_indent:
                                cleaned_lines.append(line[base_indent:])
                            else:
                                cleaned_lines.append(line)
                        else:
                            cleaned_lines.append(line)
                    
                    methods_dict[method_name] = '\n'.join(cleaned_lines)
                else:
                    methods_dict[method_name] = method_code
                
                print(f"  [OK] Extracted {method_name} (lines {start_line}-{end_line})")
            else:
                print(f"  [FAIL] Failed to find {method_name}")
        
        # Create adapter file
        output_path = os.path.join(output_dir, filename)
        if methods_dict:
            create_adapter_file(class_name, methods_dict, output_path)
        else:
            print(f"  ⚠ No methods found for {filename}")

if __name__ == "__main__":
    main()
