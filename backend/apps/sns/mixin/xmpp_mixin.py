from sqlalchemy.orm import Session
from backend.database.models.chat import AiChatCfg
from backend.apps.sns.map_task_manager import MapTaskManager
from backend.apps.sns.js_task_manager import JsTaskManager
from backend.apps.sns.xmpp_client import XMPPClientManager
from backend.modules.agent.agent_manager import agent_manager
from backend.shared.websocket_manager import manager as websocket_manager

# *********
import os
import math
# 主要用于发送附件
import asyncio
import zipfile
import shutil
import time

import logging

import re

log = logging.getLogger(__name__)
from db.DBFactory import (query_AgentCfg, add_AIChatMessages, get_prompt_by_title, query_function_mng,
                          add_function_mng, update_map_task, add_map_visit, get_key_value,
                          update_map_trade, add_map_trade, add_map_tool, query_single_map_trade, update_AiChatCfg_by_user_id, update_AiChatCfg_map, query_AiChatCfg_map, add_mcp_mng, query_mcp_mng,
                          delete_map_preset_msg, query_map_preset_msg_all, add_map_preset_msg, query_tool_list, query_single_tool, query_AiChatCfg_map_setting)
from util import (generate_random_id, add_memory_list)
from i18n import lt
from enum import Enum
from typing import List, Dict, Optional
import json
import logging
import requests
import geopy.distance
from geopy.distance import distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
import random

logger = logging.getLogger(__name__)



class XmppMixin:

    async def receiveMessage(self, event):
        """
        接收并处理XMPP消息

        Args:
            event: XMPP消息事件，包含'body'和'from'字段
        """
        if event is None:
            logger.warning("Received None event in receiveMessage")
            return

        try:
            # 提取消息内容和发送者
            content = event.get('body', '')
            from_str = str(event.get('from', ''))

            if not content or not from_str:
                logger.warning(f"Invalid message event: content={content}, from={from_str}")
                return

            logger.info(f"Received message from {from_str}: {content[:50]}...")

            # 默认消息处理流程
            await self.handle_receiveMessage(content, from_str)

        except KeyError as e:
            logger.error(f"Missing required field in message event: {e}")
        except Exception as e:
            logger.error(f"Error in receiveMessage: {e}", exc_info=True)

    async def handle_receiveMessage(self, content, from_str):
        """
        处理接收到的XMPP消息内容

        Args:
            content: 消息内容
            from_str: 发送者JID
        """
        try:
            logger.info(f"Processing message from {from_str}, content length: {len(content)}")

            # 检查map_mode，只在org模式下处理
            if self.map_mode != 'org':
                logger.debug(f"Skipping message processing, map_mode is '{self.map_mode}' (not 'org')")
                return

            # 提取账户信息
            account = from_str.split('/')[0]
            logger.debug(f"Extracted account: {account}")

            # 发送聊天消息到UI
            try:
                self.send_talk_message(account, self.ai_chat_cfg.account, content)
            except Exception as e:
                logger.error(f"Failed to send talk message to UI: {e}")

            # 管理聊天历史
            if account not in self.talk_history:
                self.talk_history[account] = []
                logger.debug(f"Created new talk history for account: {account}")

            self.talk_history[account].append("Friend:" + content)
            self.current_talk_history.append("Friend:" + content)
            logger.debug(f"Updated talk history for {account}, total messages: {len(self.talk_history[account])}")

            # 消息类型路由 - 使用walrus operator进行条件检查
            message_handled = False

            if (pay_received_str := self.check_pay_in_received(content)):
                logger.info(f"Detected payment received from {account}")
                self.handle_pay_received(pay_received_str)
                message_handled = True

            elif (good_received_str := self.check_good_in_received(content)):
                logger.info(f"Detected goods received from {account}")
                self.handle_good_received(good_received_str)
                message_handled = True

            else:
                # 检查是否为购买请求
                if (buy_flag := self.check_buy_in_received(content)):
                    logger.info(f"Detected buy inquiry from {account}")
                    self.talk_type = "sell"
                else:
                    logger.debug(f"Processing as general conversation message from {account}")

                # 处理一般对话消息
                asyncio.create_task(self.taskmng.process_task(
                    event="conversation_message_received",
                    talk_history_str=json.dumps(self.current_talk_history, ensure_ascii=False)
                ))
                message_handled = True

            # 保存当前接收的消息
            self.current_received_msg = content

            # 检查人工接管标志
            if not self.human_take_over:
                logger.debug("Human takeover is disabled, continuing automated processing")
            else:
                logger.info("Human takeover is enabled")

            logger.info(f"Message processing completed for {account}, handled: {message_handled}")

        except Exception as e:
            logger.error(f"Error in handle_receiveMessage: {e}", exc_info=True)
            # 即使出错也要保存消息内容
            try:
                self.current_received_msg = content
            except:
                pass


    def send_xmpp_message(self, to_jid: str, content: str) -> bool:
        """
        通过XMPPClientManager发送XMPP消息

        Args:
            to_jid: 接收者JID
            content: 消息内容

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        try:
            client = self.xmpp_manager.get_client()
            if not client or not client.is_client_connected():
                logger.error("XMPP client not connected")
                return False

            client.send_message_to_jid(to_jid, content)
            logger.debug(f"XMPP message sent to {to_jid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send XMPP message to {to_jid}: {e}")
            return False

    def sendMessage(self, content, by_click=False, to_jid=None, to_name=None, back_ground=False):
        """
        发送XMPP消息

        Args:
            content: 消息内容
            by_click: 是否通过点击触发，默认False
            to_jid: 接收者JID，默认None（从current_talk_people获取）
            to_name: 接收者名称，默认None（从current_talk_people获取）
            back_ground: 是否后台发送，默认False

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        if not to_jid:
            if self.current_talk_people:
                current_talk_people = self.current_talk_people
                to_jid = current_talk_people["account"]
                to_name = current_talk_people["nick_name"]
            else:
                return
        try:
            # 验证消息内容
            if not content:
                logger.warning("Cannot send empty message")
                return False

            # 解析接收者信息
            recipient = self._resolve_recipient(to_jid, to_name)
            if not recipient:
                return False

            to_jid = recipient['jid']
            to_name = recipient['name']

            logger.info(f"Sending message to {to_jid}: {content[:50]}...")

            # 保存到数据库（如果是通过点击触发）
            if by_click:
                self._save_message_to_database(content, to_jid, to_name)

            # 发送XMPP消息
            if not self.send_xmpp_message(to_jid, content):
                logger.error(f"Failed to send XMPP message to {to_jid}")
                return False

            # 更新UI（如果不是后台发送）
            if not back_ground:
                self._update_ui_with_sent_message(to_jid, content)

            logger.info(f"Message sent successfully to {to_jid}")
            return True

        except Exception as e:
            logger.error(f"Error in sendMessage: {e}", exc_info=True)
            return False

    def _resolve_recipient(self, to_jid=None, to_name=None):
        """
        解析接收者信息

        Args:
            to_jid: 接收者JID
            to_name: 接收者名称

        Returns:
            dict: 包含jid和name的字典，失败返回None
        """
        if to_jid:
            return {'jid': to_jid, 'name': to_name}

        if self.current_talk_people:
            current_talk_people = self.current_talk_people
            jid = current_talk_people.get("account")
            name = current_talk_people.get("nick_name")
            logger.debug(f"Resolved recipient from current_talk_people: {jid}")
            return {'jid': jid, 'name': name}

        logger.warning("No recipient specified and no current_talk_people available")
        return None

    def _save_message_to_database(self, content, to_jid, to_name):
        """
        保存消息到数据库

        Args:
            content: 消息内容
            to_jid: 接收者JID
            to_name: 接收者名称
        """
        try:
            add_AIChatMessages(
                self.conversation_id,
                0,
                "",
                content,
                self.ai_chat_cfg.name,
                self.ai_chat_cfg.account,
                to_name,
                to_jid,
                False
            )
            logger.debug(f"Message saved to database for conversation {self.conversation_id}")
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")

    def _update_ui_with_sent_message(self, to_jid, content):
        """
        更新UI显示发送的消息

        Args:
            to_jid: 接收者JID
            content: 消息内容
        """
        if self.map_mode != 'org':
            logger.debug(f"Skipping UI update, map_mode is '{self.map_mode}' (not 'org')")
            return

        try:
            self.send_talk_message(self.ai_chat_cfg.account, to_jid, content)
            logger.debug(f"UI updated with sent message to {to_jid}")
        except Exception as e:
            logger.error(f"Failed to update UI with sent message: {e}")
