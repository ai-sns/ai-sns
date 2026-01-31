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


class MapMovementMixin:

    def go_around(self):
        radius = 500  # 半径，单位为米
        # 初始化当前位置和上一个位置
        current_position = Point(self.aichatcfg_record.current_position[1], self.aichatcfg_record.current_position[0])
        last_position = Point(self.aichatcfg_record.last_position[1], self.aichatcfg_record.last_position[0])

        # 如果位置相同，跳过象限排除
        if current_position == last_position:
            excluded_quadrant = None
        else:
            # 确定上一个位置相对于当前坐标的象限
            last_lon_diff = last_position.longitude - current_position.longitude
            last_lat_diff = last_position.latitude - current_position.latitude

            # 根据差值计算上个位置所在的象限
            if last_lon_diff > 0 and last_lat_diff > 0:
                excluded_quadrant = 1  # 第一象限
            elif last_lon_diff < 0 and last_lat_diff > 0:
                excluded_quadrant = 2  # 第二象限
            elif last_lon_diff < 0 and last_lat_diff < 0:
                excluded_quadrant = 3  # 第三象限
            else:
                excluded_quadrant = 4  # 第四象限

        def generate_random_point(excluded_quadrant):
            while True:
                bearing = random.uniform(0, 360)
                candidate_position = distance(meters=radius).destination(current_position, bearing)

                if abs(candidate_position.latitude) >= 90:
                    candidate_position = Point(89.999 if candidate_position.latitude > 0 else -89.999,
                                               current_position.longitude)

                candidate_position = Point(candidate_position.latitude,
                                           (candidate_position.longitude + 180) % 360 - 180)

                if excluded_quadrant is None:  # 跳过象限排除
                    return candidate_position

                lon_diff = candidate_position.longitude - current_position.longitude
                lat_diff = candidate_position.latitude - current_position.latitude

                if lon_diff > 0 and lat_diff > 0:
                    candidate_quadrant = 1
                elif lon_diff < 0 and lat_diff > 0:
                    candidate_quadrant = 2
                elif lon_diff < 0 and lat_diff < 0:
                    candidate_quadrant = 3
                else:
                    candidate_quadrant = 4

                if candidate_quadrant != excluded_quadrant:
                    return candidate_position

        target_position = generate_random_point(excluded_quadrant)
        self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
        self.aichatcfg_record.current_position = [target_position.longitude, target_position.latitude]

        new_pos = self.aichatcfg_record.current_position
        command = ("move_to_a_place", str(new_pos[0]), str(new_pos[1]))
        self.send_msg_to_map(command)

        result = f"你移动了500米，附近没有任何人。"
        self.update_after_moving()
        return result

    def initial_bearing(self, p1: Point, p2: Point) -> float:
        """
        计算从 p1 指向 p2 的初始方位角（度，0-360）
        """
        lon1, lat1 = math.radians(p1.longitude), math.radians(p1.latitude)
        lon2, lat2 = math.radians(p2.longitude), math.radians(p2.latitude)
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    def move_ahead(self, current_position, target_position, target_place):
        move_distance = 500  # 移动距离（米）

        # 转换为 geopy.Point（Point 接受 lat, lon）
        if not isinstance(current_position, Point):
            current_position = Point(current_position[1], current_position[0])

        if not isinstance(target_position, Point):
            target_position = Point(target_position[1], target_position[0])

            # 计算实际距离
        actual_distance = distance(current_position, target_position).m

        try:
            # 情况 1: 已经在目标点（零距离）
            if actual_distance == 0:
                self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
                self.aichatcfg_record.current_position = [current_position.longitude, current_position.latitude]
                return f"您已在目标位置{target_place}。"

            # 情况 2: 剩余距离小于一步
            if actual_distance <= move_distance:
                self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
                self.aichatcfg_record.current_position = [target_position.longitude, target_position.latitude]
                new_pos = self.aichatcfg_record.current_position
                command = ("move_to_a_place", str(new_pos[0]), str(new_pos[1]))
                self.send_msg_to_map(command)
                return f"您已到达目标位置{target_place}（剩余 0 公里）。"

                # 情况 3: 需要计算 bearing

            if abs(current_position.latitude) == 90:
                # 极点：方向不唯一 -> 默认朝向赤道
                bearing = 180 if current_position.latitude > 0 else 0
            else:
                inv = Geodesic.WGS84.Inverse(
                    current_position.latitude, current_position.longitude,
                    target_position.latitude, target_position.longitude
                )
                bearing = inv['azi1'] % 360

            # 沿该方向移动 move_distance
            next_position = distance(meters=move_distance).destination(
                point=current_position,
                bearing=bearing
            )

            self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
            self.aichatcfg_record.current_position = [next_position.longitude, next_position.latitude]

            new_pos = self.aichatcfg_record.current_position
            command = ("move_to_a_place", str(new_pos[0]), str(new_pos[1]))
            self.send_msg_to_map(command)

            print("last_position", self.aichatcfg_record.last_position)
            print("current_position", self.aichatcfg_record.current_position)
            print("target_position", target_position)

            # 重新计算剩余距离
            remaining_distance = distance(next_position, target_position).km

            self.update_after_moving()

            return f"你向目标地点{target_place}移动了{move_distance}米。距离目标还剩 {remaining_distance:.2f} 公里。"


        except Exception as e:
            return f"计算移动坐标时出错：{str(e)}"

    def move_by_route(self):
        command = ("route_move_action", "", "")
        self.send_msg_to_map(command)
        target_place = self.route_target_place
        route_position_list = self.route_position_list
        total_distance = self.route_total_distance
        move_distance = self.route_move_distance
        remaining_distance = total_distance - move_distance
        return f"你向目标地点{target_place}移动了{move_distance}米。距离目标还剩 {remaining_distance:.2f} 公里。"

    def move_to_a_place(self, lng, lat):
        # self.write_thinking_process_to_pane(lt(f"move to the place:{lng},{lat}", f"移动到:{lng},{lat}"), "move_to_a_place")
        command = ("move_to_a_place", str(lng), str(lat))
        self.send_msg_to_map(command)
        place_name = self.place_selected[0].get("place_name", "")
        self.place_selected = None
        asyncio.create_task(self.taskmng.process_task(event="arrived_at_place", place_name=place_name))

    def explore_the_map(self):
        # self.write_thinking_process_to_pane("explore the map")
        return
        current_position = self.aichatcfg_record.current_position
        if len(self.taskmng.process_list) < 2:
            last_position = current_position
        else:
            last_position = self.taskmng.process_list[-2].get("current_position", [])

        search_radius = self.search_radius

        # 确保位置不为空
        if not last_position or not current_position:
            return None

        # 将位置转换为WKT（Well-Known Text）格式
        current_position_wkt = f"POINT({current_position[0]} {current_position[1]})"
        last_position_wkt = f"POINT({last_position[0]} {last_position[1]})"

        # SQL查询：寻找符合条件的坐标
        query = """
        SELECT ST_AsText(geom) AS location
        FROM locations
        WHERE ST_DWithin(geom::geography, ST_GeogFromText(%s), %s)
        AND NOT ST_DWithin(geom::geography, ST_GeogFromText(%s), %s)
        LIMIT 1;
        """

        # 执行查询并获取结果
        with db_conn.cursor() as cursor:
            cursor.execute(query, (current_position_wkt, search_radius, last_position_wkt, search_radius / 2))
            result = cursor.fetchone()

        # 返回结果
        if result:
            return result[0]
        return None

    def handle_arrived_at_place(self, place_name):
        # self.write_thinking_process_to_pane(lt(f"Arrived the place:{place_name}", f"到达了:{place_name}"), "handle_arrived_at_place")
        description = f"我成功到达地点：{place_name}。"
        self.taskmng.current_situation = description
        asyncio.create_task(self.taskmng.process_task(event="move_to_a_place_completed", description=description))

    def ask_agent_to_pick_place_list_sync(self, objective_to_achieve, provided_place_list):
        """
        向代理请求选择地点列表（同步版本）。

        :param objective_to_achieve: 任务描述
        :param provided_place_list: 提供的地点列表
        """
        self.show_status_on_map("watching")
        self.show_information(lt("Ask Agent to pick a place to move.", "让Agent选择一个地方作为目的地。"))
        task_summary = self.taskmng.get_task_summary()
        curren_situation = self.taskmng.current_situation
        current_process = f"- 当前目标\n{objective_to_achieve}\n- 当前进展\n{curren_situation}"
        role_prompt = get_prompt_by_title("__pick_place_list__")
        role_prompt = role_prompt.replace("__task_summary__", task_summary)
        role_prompt = role_prompt.replace("__current_situation__", current_process)
        role_prompt = role_prompt.replace("__provided_place_list__", provided_place_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        self.command_status = "ask_agent_to_pick_place_list"
        asyncio.create_task(self.ask_agent_and_get_instruction(question, role_prompt))

    # 4.让agent选择地址
    async def ask_agent_to_pick_place_list(self, objective_to_achieve, provided_place_list):
        """
        向代理请求选择地点列表。

        :param objective_to_achieve: 任务描述
        :param provided_place_list: 提供的地点列表
        """
        self.show_status_on_map("watching")
        self.show_information(lt("Ask Agent to pick a place to move.", "让Agent选择一个地方作为目的地。"))
        task_summary = self.taskmng.get_task_summary()
        curren_situation = self.taskmng.current_situation
        current_process = f"- 当前目标\n{objective_to_achieve}\n- 当前进展\n{curren_situation}"
        role_prompt = get_prompt_by_title("__pick_place_list__")
        role_prompt = role_prompt.replace("__task_summary__", task_summary)
        role_prompt = role_prompt.replace("__current_situation__", current_process)
        role_prompt = role_prompt.replace("__provided_place_list__", provided_place_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        self.command_status = "ask_agent_to_pick_place_list"  # 需要这一行
        await self.ask_agent_and_get_instruction(question, role_prompt)

    # 4.1处理agent选择的地址
    def handle_agent_pick_place_list_result(self, content):
        """
        处理代理选择地点的结果。

        :param content: 代理返回的结果内容
        """
        result_list = json.loads(content)
        if result_list:
            result = result_list[0]
            place_id = result["place_id"]
            place_name = result["place_name"]
            place_position = result["place_position"]
            reason_for_selection = result["reason_for_selection"]
            match_score = result["match_score"]
            self.place_selected = result_list

            if self.place_selected:
                asyncio.create_task(self.taskmng.process_task(action="move_to_a_place", place_name=self.place_selected[0]["place_name"], lng=self.place_selected[0]["place_position"][0], lat=self.place_selected[0]["place_position"][1], match_score=match_score))

    def move_on(self):
        if self.route_flag:
            self.move_on_route()

        else:
            self.move_on_people()

    def move_on_route(self):
        command = ("move_on_route", 500, "")
        self.send_msg_to_map(command)
        self.current_place = "未知"
        self.aichatcfg_record.current_position = [116.01, 29.01]
        self.taskmng.add_process(current_place=self.current_place, current_position=self.aichatcfg_record.current_position)
        ask_content = f"- 当前位置\n{self.current_place}\n- 当前坐标\n{self.aichatcfg_record.current_position}\n- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n{self.taskmng.current_situation}"
        asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=ask_content))

    def move_on_people(self):
        people = self.get_nearest_people()
        pos = people.get("location", [])
        new_pos = self.calculate_pos(pos)
        command = ("move_to_a_place", str(new_pos[0]), str(new_pos[1]))
        self.send_msg_to_map(command)
        self.current_place = "未知"
        self.aichatcfg_record.current_position = new_pos
        self.taskmng.add_process(current_place=self.current_place, current_position=self.aichatcfg_record.current_position)
        ask_content = f"- 当前位置\n{self.current_place}\n- 当前坐标\n{self.aichatcfg_record.current_position}\n- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n{self.taskmng.current_situation}"
        asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=ask_content))

    def get_nearest_people(self):
        url = "http://www.ai-sns.org/api/get_nearest_people"
        params = {
            "lng": self.aichatcfg_record.current_position[0],
            "lat": self.aichatcfg_record.current_position[1]
        }
        people = {
            "nation_id": "AI123451234567890ABCDEF7894",
            "account": "yangyang@xabber.de",
            "location": [
                116.30690718139134,
                40.06259235539735
            ],
            "nick_name": "W宝",
            "avatar": "img_woman_hi",
            "avatar_3d": "smallofficewoman_0_0_0_0_1_0.glb",
            "profile": "我是个医生",
            "talk_limit": 10,
            "talk_number": 5,
            "llm": "openai-4o",
            "level": 1,
            "credit": 100,
            "status": "1"
        }
        return people
        people = self.http_request(url, params)
        return people

    def calculate_pos(self, pos):
        new_pos = pos
        return new_pos

    def update_after_moving(self):
        lng = self.aichatcfg_record.current_position[0]
        lat = self.aichatcfg_record.current_position[1]
        url = "http://www.ai-sns.org/api/update-location/"
        params = {
            "nation_id": "AI123451234567890ABCDEF7890",
            "password": "securePassword123!",
            "longitude": lng,
            "latitude": lat,
        }
        response = requests.post(url, data=params)
        print(response)

    def check_place(self, address, lng, lat):
        command = ("check_place", address, str(lng) + "_" + str(lat));
        self.send_msg_to_map(command)
