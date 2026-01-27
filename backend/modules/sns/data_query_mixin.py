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

class DataQueryMixin:

    def get_place_list(self):
        url = "http://www.ai-sns.org/api/get_place_list/"
        params = {
            "lng": self.aichatcfg_record.current_position[0],
            "lat": self.aichatcfg_record.current_position[1]
        }
        place_list = self.http_request(url, params)
        return place_list

    def get_people_list(self):
        url = "http://www.ai-sns.org/api/get_people_list/"
        params = {
            "lng": self.aichatcfg_record.current_position[0],
            "lat": self.aichatcfg_record.current_position[1]
        }
        data = self.http_request(url, params)

        remove_id = self.user_map_setting.get("nationid", "")

        people_list = [item for item in data if item["nation_id"] != remove_id]

        return people_list

    def are_lists_of_dicts_equal(self, list1, list2):
        """
        Checks if two lists of dictionaries are equal, regardless of order.

        Args:
            list1: The first list of dictionaries.
            list2: The second list of dictionaries.

        Returns:
            True if both lists contain the same dictionaries, otherwise False.
        """
        # Sort both lists by their string representations of dicts for consistent comparison
        sorted_list1 = sorted(list1, key=lambda d: str(sorted(d.items())))
        sorted_list2 = sorted(list2, key=lambda d: str(sorted(d.items())))

        return sorted_list1 == sorted_list2

    def get_balance(self):
        token_balance = 1000
        self.token_balance = token_balance
        return token_balance

    def update_balance(self, token_balance):
        self.token_balance = token_balance

    def add_friend(self):
        pass

    def get_dict_by_id(self, dict_list, target_id):
        """
        根据目标 id 从字典列表中查找并返回对应的字典

        :param dict_list: 包含若干字典的列表
        :param target_id: 目标 id 字符串
        :return: 对应 id 的字典，如果没有找到，则返回 None
        """
        # 使用字典推导式将列表转换为以 id 为键的字典，以实现 O(1) 的查找效率
        dict_map = {d['id']: d for d in dict_list}

        # 使用 get 方法返回目标字典，若目标 id 不存在，则返回 None
        return dict_map.get(target_id)

    def http_request(self, url, params=None, method="POST"):
        """
        # GET 请求
        res = http_request("http://example.com/api", {"key": "value"}, method="GET")

        # POST 请求
        res = http_request("http://example.com/api", {"username": "tom", "password": "123"}, method="POST")

        """
        try:
            method = method.upper()
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, data=params)
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            response.raise_for_status()  # 检查 HTTP 状态码
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP错误发生: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"请求错误发生: {req_err}")
        except ValueError as json_err:
            print(f"JSON解析错误: {json_err}")

        return None

    def save_all_user_data(self):
        data = {
            "current_place": self.current_place,
            "current_position": json.dumps(self.aichatcfg_record.current_position, ensure_ascii=False),
            "last_position": json.dumps(self.aichatcfg_record.last_position, ensure_ascii=False),
            "life_point": self.life_point,
            "energy_point": self.energy_point,
            "move_point": self.move_point,
            "exp_point": self.exp_point,
            "iq_point": self.iq_point,
            "money": self.money,
            "credit": self.credit,
            "level": self.level,
        }
        update_AiChatCfg_map(**data)

    def load_all_user_data(self):
        record = query_AiChatCfg_map()
        self.current_place = record.current_place

        # 处理 current_position，支持多种格式
        self.aichatcfg_record.current_position = self._parse_position_data(record.current_position)
        self.last_position = self._parse_position_data(record.last_position)

        self.life_point = record.life_point  # db
        self.energy_point = record.energy_point  # db
        self.move_point = record.move_point  # db
        self.exp_point = record.exp_point  # db
        self.iq_point = record.iq_point  # db
        self.money = record.money  # db
        self.credit = record.credit  # db
        self.level = record.level  # db

        if record.route_status == "playing":
            self.move_by_route_flag = True
        else:
            self.move_by_route_flag = False

        user_map_setting = query_AiChatCfg_map_setting()
        self.user_map_setting = user_map_setting
        print("self.aichatcfg_record", self.aichatcfg_record.current_position)
        print("self.aichatcfg_recordprofile", self.aichatcfg_record.sign)

        # 在加载完所有数据后更新资源显示和图表
        self.update_resource_display()
        self.update_map_charts()

    def _parse_position_data(self, position_data):
        """
        解析位置数据，支持以下格式：
        1. JSON字符串格式：{"lat": 39.51783322503789, "lng": -76.20197639555775}
        2. JSON数组格式：[116.31633245364759, 39.83663838626669]
        3. 已经是数组格式：[lng, lat]
        返回统一的 [lng, lat] 数字数组格式
        """
        if not position_data:
            return []

        # 如果已经是列表格式，直接返回
        if isinstance(position_data, list):
            # 确保是 [lng, lat] 格式
            if len(position_data) >= 2:
                return [float(position_data[0]), float(position_data[1])]
            else:
                return []

        # 如果是字符串，尝试解析
        if isinstance(position_data, str):
            try:
                # 尝试解析为JSON
                parsed_data = json.loads(position_data)

                # 如果解析后是字典格式 {"lat": ..., "lng": ...}
                if isinstance(parsed_data, dict):
                    lat = float(parsed_data.get("lat", 0))
                    lng = float(parsed_data.get("lng", 0))
                    return [lng, lat]

                # 如果解析后是列表格式 [lng, lat] 或 [lat, lng]
                elif isinstance(parsed_data, list) and len(parsed_data) >= 2:
                    # 假设列表中第一个是lng，第二个是lat
                    return [float(parsed_data[0]), float(parsed_data[1])]

            except json.JSONDecodeError:
                # 如果不是有效的JSON，返回空数组
                return []

        # 其他情况返回空数组
        return []

    def decline_energy(self):
        exp = self.exp_point
        decline_point = 25 * ((100 - exp) / 100)
        self.energy_point = self.energy_point - decline_point
        self.move_point = 100 * (self.life_point / 100) * (self.energy_point / 100)

    def decline_life(self):
        exp = self.exp_point
        decline_point = 25 * ((100 - exp) / 100)
        self.life_point = self.life_point - decline_point
        self.move_point = 100 * (self.life_point / 100) * (self.energy_point / 100)
