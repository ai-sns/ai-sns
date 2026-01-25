"""
事件处理相关的 Mixin
包含配置更新、事件回调等功能
"""
import logging
import json
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class EventHandlerMixin:
    """事件处理相关功能"""

    def handle_aichatcfg_property_updated(self, property_name):
        """
        处理 AiChatCfg 属性更新事件
        
        Args:
            property_name: 被更新的属性名
        """
        try:
            logger.info(f"AiChatCfg property updated: {property_name}")

            # 根据不同的属性执行不同的处理
            if property_name == 'current_position':
                self._handle_position_update()
            elif property_name == 'life_point':
                self._handle_life_point_update()
            elif property_name == 'energy_point':
                self._handle_energy_point_update()
            elif property_name == 'money':
                self._handle_money_update()
            else:
                logger.debug(f"No specific handler for property: {property_name}")

            # 更新 UI 显示
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_resource_display()

        except Exception as e:
            logger.error(f"Failed to handle property update: {e}")

    def _handle_position_update(self):
        """处理位置更新"""
        try:
            if hasattr(self, 'current_position'):
                # 更新 UI 上的位置显示
                if hasattr(self, 'ui_adapter'):
                    self.ui_adapter.update_current_location(self.current_position)
                
                logger.debug(f"Position updated to: {self.current_position}")

        except Exception as e:
            logger.error(f"Failed to handle position update: {e}")

    def _handle_life_point_update(self):
        """处理生命值更新"""
        try:
            if hasattr(self, 'life_point'):
                # 检查是否需要触发警告
                if self.life_point <= 20:
                    self.show_notification(
                        "警告",
                        "生命值过低,请注意休息!",
                        "warning"
                    )
                
                logger.debug(f"Life point updated to: {self.life_point}")

        except Exception as e:
            logger.error(f"Failed to handle life point update: {e}")

    def _handle_energy_point_update(self):
        """处理体力值更新"""
        try:
            if hasattr(self, 'energy_point'):
                # 检查是否需要触发警告
                if self.energy_point <= 20:
                    self.show_notification(
                        "警告",
                        "体力值过低,建议补充能量!",
                        "warning"
                    )
                
                logger.debug(f"Energy point updated to: {self.energy_point}")

        except Exception as e:
            logger.error(f"Failed to handle energy point update: {e}")

    def _handle_money_update(self):
        """处理金钱更新"""
        try:
            if hasattr(self, 'money'):
                # 检查是否需要触发警告
                if self.money <= 100:
                    self.show_notification(
                        "提醒",
                        "资金不足,请注意财务状况!",
                        "info"
                    )
                
                logger.debug(f"Money updated to: {self.money}")

        except Exception as e:
            logger.error(f"Failed to handle money update: {e}")

    def handle_event_before_decistion(self, tool_name, ask_content):
        """
        处理决策前事件
        
        Args:
            tool_name: 工具名称
            ask_content: 请求内容
        """
        try:
            from db.DBFactory import query_single_tool

            self.command_status = "handle_event_before_decistion"
            tool_record = query_single_tool(name=tool_name)
            tool_id = tool_record.id
            what_to_do = ask_content if ask_content else "请执行"
            self.ask_agent_to_run_a_tool_sync(tool_id, tool_name, what_to_do)

        except Exception as e:
            logger.error(f"Failed to handle event before decision: {e}")

    def handle_event_before_decistion_result(self, result_content):
        """处理决策前事件的结果"""
        try:
            self.command_status = "ask_agent_instruction_to_process_activity"
            asyncio.create_task(
                self.handle_ask_agent_instruction_to_process_activity(result_content)
            )

        except Exception as e:
            logger.error(f"Failed to handle event before decision result: {e}")

    async def handle_event_after_decistion(self, tool_name, instruction):
        """
        处理决策后事件
        
        Args:
            tool_name: 工具名称
            instruction: 指令内容
        """
        try:
            from db.DBFactory import query_single_tool

            self.command_status = "handle_event_after_decistion"
            tool_record = query_single_tool(name=tool_name)
            tool_id = tool_record.id
            what_to_do = instruction
            await self.ask_agent_to_run_a_tool(tool_id, tool_name, what_to_do)

        except Exception as e:
            logger.error(f"Failed to handle event after decision: {e}")

    def handle_event_after_decistion_result(self, instruction):
        """处理决策后事件的结果"""
        try:
            self.command_status = ""
            self.handle_parse_agent_instruction_for_process_activity(instruction)

        except Exception as e:
            logger.error(f"Failed to handle event after decision result: {e}")

    def handle_event_receive_msg(self, tool_name, content, from_str):
        """
        处理接收消息事件
        
        Args:
            tool_name: 工具名称
            content: 消息内容
            from_str: 发送者
        """
        try:
            from db.DBFactory import query_single_tool

            self.command_status = "handle_event_receive_msg"
            tool_record = query_single_tool(name=tool_name)
            tool_id = tool_record.id
            what_to_do = content
            self.ask_agent_to_run_a_tool_sync(tool_id, tool_name, what_to_do)

        except Exception as e:
            logger.error(f"Failed to handle receive message event: {e}")

    def handle_event_receive_msg_result(self, content):
        """处理接收消息事件的结果"""
        try:
            self.command_status = ""
            from_str = self.current_talk_people.get("account") if self.current_talk_people else ""
            asyncio.create_task(self.handle_receiveMessage(content, from_str))

        except Exception as e:
            logger.error(f"Failed to handle receive message event result: {e}")

    def handle_event_before_send_msg(self, tool_name, content, conversation_type):
        """
        处理发送消息前事件
        
        Args:
            tool_name: 工具名称
            content: 消息内容
            conversation_type: 对话类型
        """
        try:
            from db.DBFactory import query_single_tool

            self.command_status = "handle_event_before_send_msg"
            tool_record = query_single_tool(name=tool_name)
            tool_id = tool_record.id
            what_to_do = content
            self.ask_agent_to_run_a_tool_sync(tool_id, tool_name, what_to_do)

        except Exception as e:
            logger.error(f"Failed to handle before send message event: {e}")

    def handle_event_before_send_msg_result(self, content):
        """处理发送消息前事件的结果"""
        try:
            self.command_status = ""
            if hasattr(self, 'talk_type'):
                if self.talk_type == "sell":
                    self.handle_agent_review_conversation_sell_result_final(content)
                else:
                    self.handle_agent_review_conversation_result_final(content)

        except Exception as e:
            logger.error(f"Failed to handle before send message event result: {e}")

    def register_event_callback(self, event_name, callback):
        """
        注册事件回调
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        try:
            if not hasattr(self, '_event_callbacks'):
                self._event_callbacks = {}

            if event_name not in self._event_callbacks:
                self._event_callbacks[event_name] = []

            self._event_callbacks[event_name].append(callback)
            logger.debug(f"Event callback registered for: {event_name}")

        except Exception as e:
            logger.error(f"Failed to register event callback: {e}")

    def trigger_event(self, event_name, *args, **kwargs):
        """
        触发事件
        
        Args:
            event_name: 事件名称
            *args, **kwargs: 传递给回调函数的参数
        """
        try:
            if not hasattr(self, '_event_callbacks'):
                return

            if event_name in self._event_callbacks:
                for callback in self._event_callbacks[event_name]:
                    try:
                        callback(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Error in event callback for {event_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to trigger event: {e}")
