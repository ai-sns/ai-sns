"""
通信和社交相关的 Mixin
包含与其他 Agent 交流、XMPP 消息处理、对话管理等功能
"""
import logging
import json
import asyncio
from typing import List, Dict, Optional
from db.DBFactory import add_AIChatMessages

logger = logging.getLogger(__name__)


class CommunicationMixin:
    """通信和社交相关功能"""

    async def talk_to_a_people(self, message, nation_id, account, nick_name):
        """
        与指定人员开始对话
        
        Args:
            message: 要发送的消息内容
            nation_id: 对方的 nation ID
            account: 对方的账号(JID)
            nick_name: 对方的昵称
        """
        try:
            # 设置当前对话人员
            self.current_talk_people = {
                "nation_id": nation_id,
                "account": account,
                "nick_name": nick_name
            }

            # 添加到对话历史
            self.current_talk_history.append({
                "role": "user",
                "content": message
            })

            # 发送消息
            await self.send_message_to_jid(account, message)

            logger.info(f"Started conversation with {nick_name}: {message}")
            return {"status": "success", "message": "Conversation started"}

        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            return {"status": "error", "message": str(e)}

    async def send_message_to_jid(self, to_jid, content):
        """
        通过 XMPP 发送消息给指定 JID
        
        Args:
            to_jid: 接收者的 JID
            content: 消息内容
        """
        try:
            # 使用 XMPP 管理器发送消息
            await self.xmpp_manager.send_message(to_jid, content)
            
            # 保存消息到数据库
            self._save_message_to_database(to_jid, content, is_sent=True)
            
            # 更新 UI
            self._update_ui_with_sent_message(to_jid, content)
            
            logger.info(f"Message sent to {to_jid}")
            return {"status": "success"}

        except Exception as e:
            logger.error(f"Failed to send message to {to_jid}: {e}")
            return {"status": "error", "message": str(e)}

    async def handle_receiveMessage(self, content, from_jid):
        """
        处理接收到的消息
        
        Args:
            content: 消息内容
            from_jid: 发送者的 JID
        """
        try:
            logger.info(f"Received message from {from_jid}: {content}")

            # 保存消息到数据库
            self._save_message_to_database(from_jid, content, is_sent=False)

            # 检查是否需要处理事件
            if self.ai_chat_cfg.event_receive_msg and self.ai_chat_cfg.event_receive_msg != "N/A":
                tool_name = self.ai_chat_cfg.event_receive_msg
                self.handle_event_receive_msg(tool_name, content, from_jid)
                return

            # 添加到对话历史
            self.current_talk_history.append({
                "role": "assistant",
                "content": content
            })

            # 如果正在与该用户对话，继续对话逻辑
            if self.current_talk_people and self.current_talk_people.get("account") == from_jid:
                await self._process_ongoing_conversation(content, from_jid)
            else:
                # 新对话
                await self._process_new_conversation(content, from_jid)

        except Exception as e:
            logger.error(f"Failed to handle received message: {e}")

    async def _process_ongoing_conversation(self, content, from_jid):
        """处理正在进行的对话"""
        try:
            # 根据对话类型处理
            if self.talk_type == "sell":
                await self.ask_agent_to_review_conversation_sell()
            elif self.talk_type == "buy":
                await self.ask_agent_to_bargain_for_buyer(json.dumps(self.get_tool_list()))
            else:
                await self.ask_agent_to_review_conversation()

        except Exception as e:
            logger.error(f"Failed to process ongoing conversation: {e}")

    async def _process_new_conversation(self, content, from_jid):
        """处理新对话"""
        try:
            # 初始化新对话
            self.current_talk_history = [{
                "role": "assistant",
                "content": content
            }]

            # 根据配置决定是否自动回复
            if self.ai_chat_cfg.auto_reply:
                await self.ask_agent_to_review_conversation()

        except Exception as e:
            logger.error(f"Failed to process new conversation: {e}")

    async def ask_agent_to_review_conversation(self):
        """让 Agent 审查对话并生成回复"""
        try:
            from db.DBFactory import get_prompt_by_title

            messages_history = json.dumps(self.current_talk_history, ensure_ascii=False)
            conversation_target = self.taskmng.current_objective if hasattr(self, 'taskmng') else "友好交流"
            
            role_prompt = get_prompt_by_title("__review_conversation_content__")
            role_prompt = role_prompt.replace("__conversation_target__", conversation_target)
            role_prompt = role_prompt.replace("__messages_history__", messages_history)
            
            question = "请严格遵照要求评估，并严格按照格式输出。"
            
            self.command_status = "ask_agent_to_review_conversation"
            await self.ask_agent_and_get_instruction(question, role_prompt)

        except Exception as e:
            logger.error(f"Failed to review conversation: {e}")

    async def ask_agent_to_review_conversation_sell(self):
        """让 Agent 审查销售对话"""
        try:
            from db.DBFactory import get_prompt_by_title

            messages_history = json.dumps(self.current_talk_history, ensure_ascii=False)
            conversation_target = self.taskmng.current_objective if hasattr(self, 'taskmng') else "销售产品"
            tool_list = json.dumps(self.get_tool_list(), ensure_ascii=False)
            
            role_prompt = get_prompt_by_title("__review_conversation_sell_content__")
            role_prompt = role_prompt.replace("__conversation_target__", conversation_target)
            role_prompt = role_prompt.replace("__messages_history__", messages_history)
            role_prompt = role_prompt.replace("__tool_list__", tool_list)
            
            question = "请严格遵照要求评估，并严格按照格式输出。"
            
            self.command_status = "ask_agent_to_review_conversation_sell"
            await self.ask_agent_and_get_instruction(question, role_prompt)

        except Exception as e:
            logger.error(f"Failed to review sell conversation: {e}")

    def handle_agent_review_conversation_result_final(self, content):
        """处理对话审查结果"""
        try:
            content = content.strip()
            result = json.loads(content)
            continue_chat = result.get("continue_chat", False)
            current_chat_summary = result.get("summary", "")
            message = result.get("next_message", "")

            if not continue_chat:
                # 结束对话
                if hasattr(self, 'taskmng'):
                    self.taskmng.add_process_info_to_list(f"和朋友沟通后得到如下情况：{current_chat_summary}")
                    self.taskmng.current_situation = f"和别人沟通后，得到如下情况:{current_chat_summary}"
                logger.info(f"Conversation ended: {current_chat_summary}")
            else:
                # 继续对话
                if self.current_talk_people:
                    asyncio.create_task(self.talk_to_a_people(
                        message,
                        self.current_talk_people.get("nation_id"),
                        self.current_talk_people.get("account"),
                        self.current_talk_people.get("nick_name")
                    ))

        except Exception as e:
            logger.error(f"Failed to handle conversation review result: {e}")

    def _save_message_to_database(self, jid, content, is_sent):
        """保存消息到数据库"""
        try:
            add_AIChatMessages(
                self.conversation_id,
                self.ai_chat_cfg.account if is_sent else jid,
                jid if is_sent else self.ai_chat_cfg.account,
                content,
                is_sent
            )
            logger.debug(f"Message saved to database for conversation {self.conversation_id}")
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")

    def _update_ui_with_sent_message(self, to_jid, content):
        """更新UI显示发送的消息"""
        if self.map_mode != 'org':
            logger.debug(f"Skipping UI update, map_mode is '{self.map_mode}' (not 'org')")
            return

        try:
            self.ui_adapter.send_talk_message(self.ai_chat_cfg.account, to_jid, content)
            logger.debug(f"UI updated with sent message to {to_jid}")
        except Exception as e:
            logger.error(f"Failed to update UI with sent message: {e}")

    def get_people_list(self):
        """获取周围的人员列表"""
        # 这个方法的实现在原文件中,这里返回示例结构
        return []

    def clear_conversation_history(self):
        """清空对话历史"""
        self.current_talk_history = []
        self.current_talk_people = None
        logger.info("Conversation history cleared")
