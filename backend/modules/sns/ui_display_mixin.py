from sqlalchemy.orm import Session
from backend.database.models.chat import AiChatCfg
from backend.modules.sns.map_task_manager import MapTaskManager
from backend.modules.sns.js_task_manager import JsTaskManager
from backend.modules.sns.xmpp_client import XMPPClientManager
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

class UIDisplayMixin:


    def write_on_going_process_to_pane(self, new_ongoing_content: str):
        # 定义标记
        self.current_ongoing_content = new_ongoing_content
        # 获取ongoing process和task process history的内容
        ongoing_process = self.get_on_going_process()
        task_process_history = self.get_task_process_history()

        # 合并内容并更新plan_edit
        combined_content = f"{ongoing_process}\n{task_process_history}"

        # 发送到前端 Process 页签的 On Going 部分
        asyncio.create_task(self._send_to_frontend('process', ongoing_process, section='ongoing'))

        # self.plan_edit.setPlainText(combined_content)
        print("write_on_going_process_to_pane")

    def get_on_going_process(self):
        """
        返回美化后的 ongoing process 文本（纯文本版）
        """
        # 获取基础信息
        profession = self.aichatcfg_record.profession
        lng = f"{self.aichatcfg_record.current_position[0]}" if self.aichatcfg_record.current_position and len(self.aichatcfg_record.current_position) >= 2 else "0"
        lat = f"{self.aichatcfg_record.current_position[1]}" if self.aichatcfg_record.current_position and len(self.aichatcfg_record.current_position) >= 2 else "0"

        # 构建美化文本
        result = "📊 Current Status\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += f"💰 Money      : {self.aichatcfg_record.money:,.2f}\n"
        result += f"❤️ Life           : {self.aichatcfg_record.life_point}\n"
        result += f"⚡ Energy      : {self.aichatcfg_record.energy_point}\n"
        result += f"🧑‍️ Profession: {profession}\n"
        result += "📍 Location\n"
        result += f"   ├─ lng : {lng}\n"
        result += f"   └─ lat : {lat}\n\n"

        result += "⏳ On Going\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        result += f"{self.current_ongoing_content or 'N/A'}\n"

        return result

    def show_information(self, info, type_str="1"):
        self.taskmng.js_task_manager.show_information(info, type_str)


    def write_task_plan_to_pane(self, content):
        # self.plan_edit.append(f"{content}")

        print("write_task_plan_to_pane")

    async def _send_to_frontend(self, tab_type, content, section=None):
        """
        发送内容到前端指定的页签

        Args:
            tab_type: 页签类型 ('think' 或 'process')
            content: 要发送的内容
            section: 可选的部分标识 ('ongoing' 或 'history')
        """
        try:
            message = {
                "type": "sns_update",
                "tab": tab_type,
                "content": content
            }
            if section:
                message["section"] = section
            # 广播到所有连接的客户端
            await websocket_manager.broadcast(message)
            logger.info(f"Sent {tab_type} update to frontend (section: {section})")
        except Exception as e:
            logger.error(f"Failed to send to frontend: {e}")

    def write_thinking_process_to_pane(self, title, content):
        # 假设 self.thinking_edit 是 QTextEdit 的实例
        self.thinking_step_index += 1

        # 组合新内容
        new_content = f"\n🔶【{self.thinking_step_index}】{title}\n"
        new_content += f"━━━━━━━━━━━━━━━━━━\n"
        new_content += f"{content}\n"

        # 发送到前端 Think 页签
        asyncio.create_task(self._send_to_frontend('think', new_content))

        # self.thinking_edit.append(new_content)

    def write_task_process_to_pane(self, content):
        # 获取ongoing process和task process history的内容
        ongoing_process = self.get_on_going_process()
        task_process_history = self.get_task_process_history()

        # 合并内容并更新plan_edit
        combined_content = f"{ongoing_process}\n{task_process_history}"

        # 发送到前端 Process 页签
        asyncio.create_task(self._send_to_frontend('process', combined_content))

        # self.plan_edit.setPlainText(combined_content)
        print("write_task_process_to_pane")


    def get_ai_model_display_name(self):
        """
        获取AI模型显示名称，格式为"🧠 {provider} {model_name}"
        """
        try:
            from db.DBFactory import query_AgentCfg

            # 获取账户信息
            snsaccount = self.aichatcfg_record.account
            agent_cfg = query_AgentCfg(snsaccount=snsaccount)

            # 获取默认模型
            if agent_cfg and agent_cfg.defaultmodel:
                defaultmodel = agent_cfg.defaultmodel
                return f"🧠 {defaultmodel}"
            else:
                return "🧠 OpenAI gpt-4o-mini"  # 默认值
        except Exception as e:
            print(f"获取AI模型名称时出错: {e}")
            return "🧠 OpenAI gpt-4o-mini"  # 出错时的默认值

    def update_resource_display(self):
        """
        更新资源显示内容，包括工具列表、人员名单和地址列表
        """
        # 获取各类资源数据
        tool_list = self.get_tool_list()
        people_list = self.get_people_list()
        place_list = self.get_place_list()

        # 格式化内容
        formatted_content = self._format_resource_content(tool_list, people_list, place_list)+"\n"

        # 发送到前端 Resource 页签
        import asyncio
        asyncio.create_task(self._send_to_frontend('resource', formatted_content))

    def _format_resource_content(self, tool_list, people_list, place_list):
        """
        格式化资源内容显示
        """
        content = ""

        # 格式化工具列表
        if tool_list:
            content += f"🌐 服务列表（共 {len(tool_list)} 项）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, tool in enumerate(tool_list):
                # 工具ID和名称
                content += f"#{tool.get('id', '')} {tool.get('name', '')}\n"


                # 地理坐标信息（如果lng,lat有值且不为0）
                lng = tool.get('lng', 0)
                lat = tool.get('lat', 0)
                if lng and lat and lng != 0 and lat != 0:
                    # 格式化坐标，最多8位小数，去除尾随零
                    formatted_lng = f"{lng:.8g}"
                    formatted_lat = f"{lat:.8g}"
                    content += f"📍 坐标：{formatted_lng}, {formatted_lat}\n"
                elif 'place' in tool and tool['place']:
                    content += f"🌍 位置：{tool['place']}\n"

                # 描述信息
                if 'description' in tool and tool['description']:
                    content += f"💬 描述：{tool['description']}\n"

                # 地址信息
                if 'address' in tool and tool['address'] and tool['address'] != "Not needed":
                    content += f"🔗 地址：{tool['address']}\n"

                # 类型和方法信息
                type_info = tool.get('type', '')
                method_info = tool.get('method', '')

                # 参数信息
                param_info = ""
                if 'parameter' in tool and tool['parameter']:
                    if isinstance(tool['parameter'], dict):
                        param_strs = [f"{k}={v}" for k, v in tool['parameter'].items()]
                        param_info = f"({', '.join(param_strs)})" if param_strs else ""
                    else:
                        param_info = f"({tool['parameter']})" if tool['parameter'] != "None" else ""

                content += f"⚙️ 类型：{type_info} ｜ 方法：{method_info}{param_info}\n"

                # 分隔线（除了最后一个工具）
                if i < len(tool_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n\n"

        # 格式化人员名单
        if people_list:
            content += f"🧑‍🤝‍🧑 人员名单（共 {len(people_list)} 位）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, person in enumerate(people_list):
                # 姓名和职业
                nick_name = person.get('nick_name', '')
                profession = person.get('profession', '')
                content += f"🧑‍ {nick_name} ｜ 👩‍💻 {profession}\n"

                # 位置信息
                location = person.get('location', [])
                if location and len(location) >= 2:
                    lng, lat = location[0], location[1]
                    # 简化城市信息

                    # 格式化经纬度，最多显示8位小数，不补零
                    formatted_lng = f"{lng:.8f}".rstrip('0').rstrip('.')
                    formatted_lat = f"{lat:.8f}".rstrip('0').rstrip('.')
                    content += f"📍 位置：{formatted_lng}, {formatted_lat}\n"

                # 账户信息
                account = person.get('account', '')
                if account:
                    content += f"💬 account: {account}\n"

                # SNS信息
                sns_url = person.get('sns_url', '')
                if sns_url:
                    content += f"🔗 sns: {sns_url}\n"

                # ID信息
                nation_id = person.get('nation_id', '')
                if nation_id:
                    content += f"🆔 nation_id: {nation_id}\n"

                # 简介信息
                profile = person.get('profile', '')
                if profile:
                    content += f"📝 profile: {profile}\n"

                # 分隔线（除了最后一个人）
                if i < len(people_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n\n"

        # 格式化地址列表
        if place_list:
            content += f"🗺️ 地址列表（共 {len(place_list)} 处）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, place in enumerate(place_list):
                # 地点名称
                place_name = place.get('place_name', '')
                content += f"🏞️ {place_name}\n"

                # 位置坐标
                position = place.get('place_position', [])
                if position and len(position) >= 2:
                    lng, lat = position[0], position[1]
                    # 格式化经纬度，最多显示8位小数，不补零
                    formatted_lng = f"{lng:.8f}".rstrip('0').rstrip('.')
                    formatted_lat = f"{lat:.8f}".rstrip('0').rstrip('.')
                    content += f"📍 {formatted_lng}, {formatted_lat}\n"

                # 描述信息
                description = place.get('description', '')
                if description:
                    content += f"📖 {description}\n"

                # 分隔线（除了最后一个地点）
                if i < len(place_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n"

        return content.strip()

    def send_command_to_map(self, command, param_1, param_2):
        """
        发送命令到地图系统

        Args:
            command: 命令类型
            param_1: 参数1
            param_2: 参数2
        """
        import asyncio
        from backend.shared.websocket_manager import manager as websocket_manager
        import logging

        logger = logging.getLogger(__name__)

        # 构建消息
        message = {
            "type": "command",
            "command": command,
            "param_1": param_1,
            "param_2": param_2
        }

        # 异步发送到前端
        async def send_message():
            try:
                await websocket_manager.broadcast(message)
                logger.info(f"Command sent to map: {command}, param_1={param_1}, param_2={param_2}")
            except Exception as e:
                logger.error(f"Failed to send command to map: {e}")

        asyncio.create_task(send_message())

    def send_talk_message(self, fromuser, touser, message):
        """
        发送聊天消息到前端地图

        Args:
            fromuser: 发送者账户
            touser: 接收者账户
            message: 消息内容
        """
        import asyncio
        from backend.shared.websocket_manager import manager as websocket_manager
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)

        # 构建chatWindow消息（原有格式）
        chat_msg = {
            "type": "chat_message",
            "from": fromuser,
            "to": touser,
            "content": message
        }

        # 构建地图消息（新格式）
        map_msg = {
            "type": "map_chat_message",
            "from_user": fromuser,
            "to_user": touser,
            "content": message,
            "timestamp": datetime.now().isoformat()
        }

        # 异步发送两种格式到前端
        async def send_messages():
            try:
                # 发送到 chatWindow
                await websocket_manager.broadcast(chat_msg)
                # 发送到地图
                await websocket_manager.broadcast(map_msg)
                logger.info(f"Chat messages sent from {fromuser} to {touser}: {message}")
            except Exception as e:
                logger.error(f"Failed to send chat messages: {e}")

        asyncio.create_task(send_messages())

    def show_status_on_map(self, status):
        """
        在地图上显示状态信息

        Args:
            status: 状态信息字符串
        """
        import asyncio
        from backend.shared.websocket_manager import manager as websocket_manager
        import logging

        logger = logging.getLogger(__name__)

        # 构建消息
        msg = {
            "type": "status_update",
            "status": status
        }

        # 异步发送到前端
        async def send_message():
            try:
                await websocket_manager.broadcast(msg)
                logger.info(f"Status update sent: {status}")
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")

        asyncio.create_task(send_message())

    def show_alert_on_map(self, message, is_error=False):
        """
        在地图上显示警告/提示信息

        Args:
            message: 警告/提示信息
            is_error: 是否为错误信息，默认False
        """
        import asyncio
        from backend.shared.websocket_manager import manager as websocket_manager
        import logging

        logger = logging.getLogger(__name__)

        # 构建消息
        msg = {
            "type": "alert",
            "message": message,
            "is_error": is_error
        }

        # 异步发送到前端
        async def send_message():
            try:
                await websocket_manager.broadcast(msg)
                logger.info(f"Alert sent: {message} (is_error={is_error})")
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")

        asyncio.create_task(send_message())



    def send_msg_to_map(self, command):
        """
        将命令发送到地图系统。
        """
        action, param_1, param_2 = command
        if action == "Use skills":
            print(f"执行技能：{param_1}")

            self.send_command_to_map(action, param_1, param_2)
        else:
            print(f"执行行动：{action}")

            self.send_command_to_map(action, param_1, param_2)

    def update_map_charts(self):
        """
        更新地图图表数据并发送到前端
        当用户属性（如智力、体力、生命值等）发生变化时调用此函数
        """
        import asyncio

        # 准备雷达图数据
        radar_data = [
            self.aichatcfg_record.iq_point,
            self.aichatcfg_record.energy_point,
            self.aichatcfg_record.life_point,
            self.aichatcfg_record.move_point,
            self.aichatcfg_record.exp_point
        ]
        radar_categories = [
            f'{lt("IQ", "智力")}:{self.aichatcfg_record.iq_point}',
            f'{lt("Energy", "体力")}:{self.aichatcfg_record.energy_point}',
            f'{lt("Life", "生命")}:{self.aichatcfg_record.life_point}',
            f'{lt("Move", "行动")}:{self.aichatcfg_record.move_point}',
            f'{lt("Exp", "经验")}:{self.aichatcfg_record.exp_point}'
        ]

        # 准备柱状图数据
        formatted_number = f"{self.aichatcfg_record.money:,.2f}"
        bar_indicators = [
            f'{lt("Money", "资金")}:{formatted_number}',
            f'{lt("Credit", "信用")}:{self.aichatcfg_record.credit}',
            f'{lt("Level", "等级")}{self.aichatcfg_record.level}'
        ]
        bar_values = [100, self.aichatcfg_record.credit, self.aichatcfg_record.level * 10]
        bar_colors = ['#ffb676', '#c3f1d7', '#99d4ff']

        # 构建用户统计数据对象
        user_stats = {
            "level": self.aichatcfg_record.level or 1,
            "credit": self.aichatcfg_record.credit or 100,
            "money": float(self.aichatcfg_record.money or 0),
            "life": self.aichatcfg_record.life_point or 100,
            "iq": self.aichatcfg_record.iq_point or 60,
            "energy": self.aichatcfg_record.energy_point or 100,
            "move": self.aichatcfg_record.move_point or 100,
            "exp": self.aichatcfg_record.exp_point or 0
        }

        # 通过WebSocket发送更新到前端
        asyncio.create_task(self._send_chart_update(user_stats))

        logger.info(f"Chart data updated and sent to frontend: {user_stats}")

    async def _send_chart_update(self, user_stats: dict):
        """
        发送图表更新数据到前端

        Args:
            user_stats: 用户统计数据字典
        """
        try:
            message = {
                "type": "user_stats_update",
                "data": user_stats
            }
            await websocket_manager.broadcast(message)
            logger.info(f"User stats update sent to frontend")
        except Exception as e:
            logger.error(f"Failed to send chart update: {e}")
