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


class CommunicationMixin:
    def talk_to_a_people(self, content, nationid, account, user_name):
        title_str = "选择人员交谈"
        content_str = f"""🟪 *The function is*:

talk_to_a_people

🟩 *The Content is*:

{lt(f"Talk to a people with {user_name} acount:{account},nationid:{nationid},content:{content}", f"和别人交谈 with {user_name} acount:{account},nationid:{nationid},content:{content}")}
            """

        self.write_thinking_process_to_pane(title_str, content_str)

        current_talk_people = self.current_talk_people
        round = current_talk_people.get("talk_round", 0) + 1
        self.current_talk_people["talk_round"] = round
        command = ("start_talk_to_it", nationid, content)
        self.send_msg_to_map(command)
        self.sendMessage(content, False, account, user_name)

        if account not in self.talk_history:
            self.talk_history[account] = []
        self.talk_history[account].append("Me:" + content)
        self.current_talk_history.append("Me:" + content)

    def communicate_with_a_people(self, action_str, instrunction):
        human_object = ""
        self.talk_type = "communication"
        self.ask_agent_start_to_talk_to_a_people_sync(action_str, human_object)

        # self.taskmng.process_task(action="process_activity", ask_content=ask_content)

    def ask_agent_to_pick_people_list_sync(self, provided_profile_list, human_objective_to_achieve=""):
        # provided_profile_list = json.dumps(self.get_people_list(),indent=4,ensure_ascii=False)
        objective_to_achieve = self.taskmng.get_current_objective()
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        task_summary = self.taskmng.get_task_summary()
        current_process = f"- 当前位置\n{self.current_place}\n- 当前坐标\n{self.aichatcfg_record.current_position}\n- 当前目标\n{objective_to_achieve}\n- 当前进展\n{self.taskmng.current_situation}"
        role_prompt = get_prompt_by_title("__pick_people_list__")
        role_prompt = role_prompt.replace("__task_summary__", task_summary)
        role_prompt = role_prompt.replace("__current_process__", current_process)
        role_prompt = role_prompt.replace("__people__to__select__", provided_profile_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        self.command_status = "ask_agent_to_pick_people_list"
        asyncio.create_task(self.ask_agent_and_get_instruction(question, role_prompt))

    def ask_agent_start_to_talk_to_a_people_sync(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_talk_to_a_people__")

        content_prompt = get_prompt_by_title("__start_to_talk_to_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_to_pick_people_list"
        asyncio.create_task(self.ask_agent_and_get_instruction(content_prompt, role_prompt))

    async def ask_agent_to_pick_people_list(self, provided_profile_list, human_objective_to_achieve=""):
        # provided_profile_list = json.dumps(self.get_people_list(),indent=4,ensure_ascii=False)
        objective_to_achieve = self.taskmng.get_current_objective()
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        task_summary = self.taskmng.get_task_summary()
        current_process = f"- 当前位置\n{self.current_place}\n- 当前坐标\n{self.aichatcfg_record.current_position}\n- 当前目标\n{objective_to_achieve}\n- 当前进展\n{self.taskmng.current_situation}"
        role_prompt = get_prompt_by_title("__pick_people_list__")
        role_prompt = role_prompt.replace("__task_summary__", task_summary)
        role_prompt = role_prompt.replace("__current_process__", current_process)
        role_prompt = role_prompt.replace("__people__to__select__", provided_profile_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        self.command_status = "ask_agent_to_pick_people_list"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    async def ask_agent_start_to_talk_to_a_people(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_talk_to_a_people__")

        content_prompt = get_prompt_by_title("__start_to_talk_to_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_to_pick_people_list"
        await  self.ask_agent_and_get_instruction(content_prompt, role_prompt)

    def handle_agent_pick_people_list_result(self, content):
        result = json.loads(content)
        if result:
            nation_id = result["nation_id"]
            account = result["account"]
            nick_name = result["nick_name"]
            message = result["message"]
            self.current_talk_people = result

            self.taskmng.current_process["people_communicated_list"].append(nation_id)
            self.taskmng.current_process["rounds_current_person"] = 1
            self.current_talk_history = []
            self.talk_to_a_people(message, nation_id, account, nick_name)

        else:
            description = "我未找到目标人员。"

            asyncio.create_task(self.taskmng.process_task(event="agent_pick_people_list_fail"))

    def handle_ask_agent_start_to_talk_to_a_people_result(self, content):
        result = json.loads(content)
        if result:
            nation_id = result["nation_id"]
            account = result["account"]
            nick_name = result["nick_name"]
            message = result["message"]
            self.current_talk_people = result

            self.taskmng.current_process["people_communicated_list"].append(nation_id)
            self.taskmng.current_process["rounds_current_person"] = 1
            self.current_talk_history = []
            self.talk_to_a_people(message, nation_id, account, nick_name)

        else:
            description = "我未找到目标人员。"

            asyncio.create_task(self.taskmng.process_task(event="agent_pick_people_list_fail"))

    async def ask_agent_to_review_conversation(self, conversation_target, messages_history):
        role_prompt = get_prompt_by_title("__review_conversation__")
        # role_prompt = role_prompt.replace("__conversation_target__", conversation_target)
        # role_prompt = role_prompt.replace("__messages_history__", messages_history)
        question = "## 聊天记录 \n" + messages_history
        await   self.ask_agent_and_get_instruction(question, role_prompt)

    def handle_agent_review_conversation_result(self, content):
        if self.ai_chat_cfg.event_before_send_msg:
            if self.ai_chat_cfg.event_before_send_msg != "N/A":
                tool_name = self.ai_chat_cfg.event_before_send_msg
                self.handle_event_before_send_msg(tool_name, content, "common")
                return

        self.handle_agent_review_conversation_result_final(content)

    def handle_agent_review_conversation_result_final(self, content):
        content = content.strip()
        result = json.loads(content)
        continue_chat = result["continue_chat"]
        current_chat_summary = result["summary"]
        message = result["next_message"]

        buy_score = result.get("buy_score", False)
        price = result.get("price", 0)

        if buy_score >= 80 and price >= 0:
            self.send_pay(price)
            return

        if not continue_chat:
            self.taskmng.add_process_info_to_list(f"和朋友沟通后得到如下情况：{current_chat_summary}")
            self.write_task_process_to_pane(f"和朋友沟通后得到如下情况：{current_chat_summary}\n\n")
            self.taskmng.current_situation = f"和别人沟通后，得到如下情况:{current_chat_summary}"
            asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n和别人沟通后，得到如下情况:{current_chat_summary}"))

        else:
            if not self.taskmng.current_process:
                self.taskmng.current_process = {"rounds_current_person": 0}
            if not self.current_talk_people:
                self.current_talk_people = {
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
                    "sns_url": "x.com"
                }

            if self.taskmng.current_process["rounds_current_person"] < self.max_rounds_per_person:
                self.taskmng.current_process["rounds_current_person"] = self.taskmng.current_process["rounds_current_person"] + 1
                self.talk_to_a_people(message, self.current_talk_people["nation_id"], self.current_talk_people["account"], self.current_talk_people["nick_name"])
            else:
                self.taskmng.add_process_info_to_list(f"和朋友沟通后得到如下情况：{current_chat_summary}")
                self.taskmng.current_situation = f"和别人沟通后，得到如下情况:{current_chat_summary}"
                asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n和别人沟通后，得到如下情况:{current_chat_summary}"))


    def ask_other_people_for_help(self, objective_to_achieve):
        if self.asking_people_for_help_flag == False:
            self.people_list_to_ask_for_help = self.get_people_nearby()
            self.asking_people_for_help_flag = True

        if self.people_list_to_ask_for_help:
            people = self.people_list_to_ask_for_help.pop(0)
            self.current_talk_people = people
            self.ask_a_people_for_help(people)
        else:
            self.asking_people_for_help_flag = False
            self.move_on()

    def ask_a_people_for_help(self, people):
        objective_to_achieve = self.taskmng.current_objective
        self.talk_to_a_people(objective_to_achieve, people["nation_id"], people["account"], people["nick_name"])

    def ask_people_help_success(self, summary):
        self.handle_the_help_summary(summary)

    def ask_people_help_fail(self, summary):
        self.move_on()

    def get_people_nearby(self):
        people_list = self.get_people_list()
        people_list_nearby = self.get_people_by_distance(3, people_list)
        return people_list_nearby

    def get_people_by_distance(self, count, people_list):
        my_position = self.aichatcfg_record.current_position
        """
        返回按与给定位置的距离排序的最近人员列表。

        Args:
            count: 要返回的最近人员数量。
            my_position: 形式为 (longitude, latitude) 的元组或列表。
            people_list: 人员字典列表，每个字典都包含一个“location”键，其值为 (longitude, latitude) 的列表。

        Returns:
            按距离排序的最近人员列表，最多包含 count 个条目。 
            如果 people_list 为空或无效，则返回一个空列表。
        """

        if not people_list or not all("location" in person and len(person["location"]) == 2 for person in people_list):
            return []  # 处理无效输入

        # 将位置转换为 (latitude, longitude) 的形式以适应 geopy
        my_position_converted = (my_position[1], my_position[0])  # 转换为 (latitude, longitude)

        # 使用 geopy 计算距离并存储在元组列表中
        distances = [
            (geopy.distance.geodesic(my_position_converted, (person["location"][1], person["location"][0])).km, person)
            for person in people_list
        ]

        # 按距离排序
        distances.sort()

        # 返回最近的人员，最多 count 个
        return [person for distance, person in distances[:count]]

    def handle_the_help_summary(self, summary):
        result = self.analyze_help_summary(summary)

        if result == "trade_skill":
            self.initiate_tool_trade(self.get_skill_list())
        elif result == "get_help":
            asyncio.create_task(self.taskmng.process_task(event="ask_people_help_success", result=summary))

        elif result == "talk_to_next_people":
            pass
        else:
            self.move_on()

    def analyze_help_summary(self, summary):
        if "trade_skill" in summary:
            result = "trade_skill"
        else:
            result = "get_help"
        return result
