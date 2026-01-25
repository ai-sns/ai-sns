"""
Agent 和 AI 交互相关的 Mixin
包含与 AI Agent 的对话、指令获取、任务规划等功能
"""
import logging
import json
import asyncio
import re
from typing import List, Dict, Optional
from backend.modules.agent.agent_manager import agent_manager
from db.DBFactory import get_prompt_by_title

logger = logging.getLogger(__name__)


class AgentInteractionMixin:

    # a.请求agent指示
    async def ask_agent_and_get_instruction(self, question, system_role_prompt, type_flag="command"):
        if self.stopping_ai_process_flag:
            self.stop_AI_process_finished()
            return

        command_status = self.command_status
        title_str = "Ask agent to get instruction"
        content_str = f"""🟪 *The function is*:

    ask_agent_and_get_instruction

    🟦 *The Command_status is*:

    {command_status}

    🟩 *The system_role_prompt is*:

    {system_role_prompt}

    🟨 *The content send to ai llm is*:

    {question} 
    """

        self.write_thinking_process_to_pane(title_str, content_str)

        # Get agent instance from agent_manager by agent_id
        if hasattr(self.ai_chat_cfg, 'agent_id') and self.ai_chat_cfg.agent_id:
            self.agent = agent_manager.get_agent_by_id(self.ai_chat_cfg.agent_id)
            if not self.agent:
                logger.error(f"Failed to load agent with ID: {self.ai_chat_cfg.agent_id}")
                return
        else:
            logger.warning("No agent_id configured in ai_chat_cfg")
            return

        agent = self.agent
        # agent.give_it_plugin(pluginname)#使用配置里面的第一个
        # agent.give_it_km(vector_path, embedding_model_name)
        self.messages_command = []
        self.messages_command.append({"role": "user", "content": question})

        if self.messages_command[0]["role"] != "system":
            self.messages_command.insert(0, {"role": "system", "content": f"{system_role_prompt}"})
        else:
            self.messages_command[0]["content"] = system_role_prompt

        messages = self.messages_command
        # 保存原始system prompt
        original_prompt = agent.role_config.get('system_prompt', '')

        modified_prompt = system_role_prompt + original_prompt

        # 临时修改system prompt
        agent.role_config['system_prompt'] = modified_prompt

        try:
            # 调用Agent进行对话
            reply = await agent.chat(
                message=question,
                conversation_id=f"sns_cjrtesting",
                use_memory=False,
                use_knowledge_base=False
            )
            # return reply
        finally:
            # 恢复原始system prompt
            agent.role_config['system_prompt'] = original_prompt

        self.on_agent_return_instruction(question, reply)

        agent.role_config['system_prompt'] = original_prompt

    # b.agent返回指示
    def on_agent_return_instruction(self, question, content):
        self.agent_replying_flag = False
        if self.stopping_ai_process_flag:
            self.stop_AI_process_finished()
            return
        # content = content.strip('```json').strip('```').strip()
        content = re.sub(r'^\s*```json\s*|\s*```\s*$', '', content, flags=re.DOTALL)
        command_status = self.command_status
        title_str = "Agent return the instruction"
        content_str = f"""🟪 *The function is*:

    on_agent_return_instruction

    🟫 *The Content Returned is*:

    {content}
            """

        self.write_thinking_process_to_pane(title_str, content_str)

        # self.loading_tab.stop_loading()

        if command_status == "ask_agent_to_decompose_task":
            self.taskmng.process_task(event="ask_agent_to_decompose_task_returned", result=content)

        elif command_status == "ask_agent_instruction_to_process_activity":
            self.taskmng.process_task(event="agent_instruction_to_process_activity_returned", instruction=content)

        elif command_status == "ask_agent_instruction_to_process_human_instruction":
            self.taskmng.process_task(event="agent_instruction_to_process_human_instruction_returned", instruction=content)


        elif command_status == "ask_agent_to_review_conversation":
            self.taskmng.process_task(event="ask_agent_to_review_conversation_returned", result=content)

        elif command_status == "ask_agent_to_review_conversation_sell":
            self.taskmng.process_task(event="ask_agent_to_review_conversation_sell_returned", result=content)


        elif command_status == "ask_agent_to_pick_place_list":
            self.taskmng.process_task(event="agent_pick_place_list_returned", result=content)


        elif command_status == "ask_agent_to_pick_people_list":
            self.taskmng.process_task(event="agent_pick_people_list_returned", result=content)

        elif command_status == "ask_agent_start_to_sell_to_a_people":
            self.taskmng.process_task(event="ask_agent_start_to_sell_to_a_people_returned", result=content)

        elif command_status == "ask_agent_start_to_buy_from_a_people":
            self.taskmng.process_task(event="ask_agent_start_to_buy_from_a_people_returned", result=content)


        elif command_status == "ask_agent_how_to_talk":
            self.taskmng.process_task(event="ask_agent_how_to_talk_returned", result=content)


        elif command_status == "ask_agent_to_pick_a_tool_to_buy":
            self.taskmng.process_task(event="ask_agent_to_pick_a_tool_to_buy_returned", result=content)

        elif command_status == "ask_agent_to_bargain_for_buyer":
            self.handle_ask_agent_to_bargain_for_buyer_result(content)

        elif command_status == "ask_agent_to_bargain_for_seller":
            self.handle_ask_agent_to_bargain_for_seller_result(content)


        elif command_status == "ask_agent_to_pick_a_tool":
            self.taskmng.process_task(event="ask_agent_to_pick_a_tool_returned", result=content)


        elif command_status == "ask_agent_to_make_a_deal":
            self.on_agent_make_deal_finished(content)

        elif command_status == "ask_agent_to_use_skill":
            self.on_ask_agent_to_use_skill_return(content)

        elif command_status == "ask_agent_to_use_service":
            self.on_ask_agent_to_use_service_return(content)

        elif command_status == "ask_agent_to_think_after_conversation":
            self.handle_agent_think_after_conversation_result(content)

        elif command_status == "ask_agent_to_arrange_function_list":
            self.handle_agent_arrange_function_list_result(content)

        elif command_status == "ask_agent_to_update_task":
            self.handle_agent_update_task_result(content)

        elif command_status == "run_tool_before_send_good":
            self.handle_send_goods(content)

        elif command_status == "handle_event_before_decistion":
            self.handle_event_before_decistion_result(content)

        elif command_status == "handle_event_after_decistion":
            self.handle_event_after_decistion_result(content)

        elif command_status == "handle_event_receive_msg":
            self.handle_event_receive_msg_result(content)

        elif command_status == "handle_event_before_send_msg":
            self.handle_event_before_send_msg_result(content)

        else:
            pass

        # self.loading_tab.stop_loading()

