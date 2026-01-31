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


class TransactionType(Enum):
    """交易类型枚举"""
    SKILL_EXCHANGE = 1
    TOKEN_PURCHASE = 2

class TradeMixin:

    async def ask_agent_to_pick_a_tool_to_buy(self, provided_tool_list_str, human_objective_to_achieve="", human_want_to_buy_str=""):
        task_summary = self.taskmng.get_task_summary()
        curren_situation = self.taskmng.current_situation
        objective_to_achieve = self.taskmng.get_current_objective()
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"
        my_tool_list = json.dumps(self.get_tool_list(), ensure_ascii=False)

        current_process = f"- 当前目标\n{objective_to_achieve}\n- 当前进展\n{curren_situation}"
        role_prompt = get_prompt_by_title("__pick_tools_to_buy__")
        role_prompt = role_prompt.replace("__task_summary__", task_summary)
        role_prompt = role_prompt.replace("__current_process__", current_process)
        role_prompt = role_prompt.replace("__human_want_to_buy__", human_want_to_buy_str)
        role_prompt = role_prompt.replace("__provided_tool_list__", provided_tool_list_str)
        role_prompt = role_prompt.replace("__my_tool_list__", my_tool_list)

        question = "请严格遵照要求评估，并严格按照格式输出。"
        await self.ask_agent_and_get_instruction(question, role_prompt)

    def handle_agent_pick_a_tool_to_buy_result(self, content):
        """
        处理代理选择云端服务的结果。

        :param content: 代理返回的结果内容
        """
        result_list = json.loads(content)
        if result_list:
            tool = result_list[0]
            self.tool_trade_inquiry(tool)
            # self.taskmng.add_process_info_to_list(f"我已经选定了要购买的目标工具：name:{name},id:{id},因为{reason_for_selection}")

    def sell_to_a_people(self, action_str, instrunction):
        human_object = ""
        self.talk_type = "sell"
        self.ask_agent_start_to_sell_to_a_people_sync(action_str, human_object)

    def buy_from_a_people(self, action_str, instrunction):
        human_object = ""
        self.talk_type = "buy"
        self.ask_agent_start_to_buy_from_a_people_sync(action_str, human_object)

    def pay_to_a_people(self, target_nation_id, target_person_name, count):
        nation_id = self.user_map_setting.get("nationid", "")
        # send_request_pay
        self.money = self.money - count
        result = f"已经成功付款{count}元给{target_person_name}。"
        return result

    def send_good(self):
        good_content = get_key_value("__good_content__")
        result = ""
        job = "医生"
        if job == "doctor":
            pass
        elif job == "driver":
            pass
        elif job == "seller":
            pass
        else:
            pass

        result = "交货成功。"
        return result

    def get_guidance(self):
        user_list_stra = """
        - J宝:是个律师,坐标[116.30375329461533,40.049108567364904],距离7公里\n
        - W宝:是个医生,坐标[116.30690718139134,40.06259235539735],距离8公里\n
                """
        user_list_str = """
暂时没有更多人员
                """
        place_list_str = """
- 北京天安门:很多人在此看升旗。坐标[116.3975,39.9087],距离40公里。\n
- 八达岭长城:著名旅游景点。坐标[116.0204,40.3606],距离60公里。\n
                """

        result = f"""
        您支付了10元费用，获得了如下信息：
        ### 人员列表：
        {user_list_str}
        ### 地址列表：
        {place_list_str}
        """""
        self.money = self.money - 10

        return result

    def set_food_order(self):
        result = ""
        self.aichatcfg_record.energy_point = self.aichatcfg_record.energy_point + 25
        self.aichatcfg_record.move_point = 100 * (self.aichatcfg_record.life_point / 100) * (self.aichatcfg_record.energy_point / 100)
        self.aichatcfg_record.money = self.aichatcfg_record.money - 30
        result = f"你支付了30元购买食物，你的体力值已经恢复为{self.aichatcfg_record.energy_point}%，当前行动力为{self.aichatcfg_record.move_point}%"
        return result

    def set_taxi_order(self, current_position, target_position, target_place):
        point1 = (current_position[1], current_position[0])  # 转换成 (纬度, 经度)
        point2 = (target_position[1], target_position[0])  # 转换成 (纬度, 经度)

        # 使用 geopy 计算距离
        dist = distance(point1, point2).kilometers
        fee = dist * 2.5

        self.aichatcfg_record.money = self.aichatcfg_record.money - fee

        self.aichatcfg_record.last_position = current_position
        self.aichatcfg_record.current_position = target_position
        new_pos = self.aichatcfg_record.current_position
        command = ("move_to_a_place", str(new_pos[0]), str(new_pos[1]))
        self.send_msg_to_map(command)

        result = f"你支付了{fee:.2f}元车费，你已经到达{target_place}，坐标为{target_position}"
        return result

    def call_a_doctor(self):
        result = ""

        self.aichatcfg_record.life_point = self.aichatcfg_record.life_point + 25
        self.aichatcfg_record.move_point = 100 * (self.aichatcfg_record.life_point / 100) * (self.aichatcfg_record.energy_point / 100)
        self.aichatcfg_record.money = self.aichatcfg_record.money - 210
        result = f"你支付了210元远程治疗服务，你的生命值已经恢复为{self.aichatcfg_record.life_point}%，当前行动力为{self.aichatcfg_record.move_point}%"
        return result


    def ask_agent_start_to_sell_to_a_people_sync(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_sell_to_a_people__")

        content_prompt = get_prompt_by_title("__start_to_sell_to_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_start_to_sell_to_a_people"
        asyncio.create_task(self.ask_agent_and_get_instruction(content_prompt, role_prompt))

    def ask_agent_start_to_buy_from_a_people_sync(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_buy_from_a_people__")

        content_prompt = get_prompt_by_title("__start_to_buy_from_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_start_to_buy_from_a_people"
        asyncio.create_task(self.ask_agent_and_get_instruction(content_prompt, role_prompt))

    # 6.让agent选择人员

    async def ask_agent_start_to_sell_to_a_people(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_sell_to_a_people__")

        content_prompt = get_prompt_by_title("__start_to_sell_to_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_start_to_sell_to_a_people"
        await  self.ask_agent_and_get_instruction(content_prompt, role_prompt)

    async def ask_agent_start_to_buy_from_a_people(self, objective_to_achieve, human_objective_to_achieve=""):
        provided_profile_list = json.dumps(self.get_people_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        role_prompt = get_prompt_by_title("__start_to_buy_from_a_people__")

        content_prompt = get_prompt_by_title("__start_to_buy_from_a_people_content__")
        content_prompt = content_prompt.replace("__action_desc__", objective_to_achieve)
        content_prompt = content_prompt.replace("__people__to__select__", provided_profile_list)

        self.command_status = "ask_agent_start_to_buy_from_a_people"
        await  self.ask_agent_and_get_instruction(content_prompt, role_prompt)

    # 6.处理agent选择的人员

    def handle_ask_agent_start_to_sell_to_a_people_result(self, content):
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

    def handle_ask_agent_start_to_buy_from_a_people_result(self, content):
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
            message = "[AISNS_INT_003_INQUIRY]" + message
            self.talk_to_a_people(message, nation_id, account, nick_name)

        else:
            description = "我未找到目标人员。"

            asyncio.create_task(self.taskmng.process_task(event="agent_pick_people_list_fail"))

    async def ask_agent_to_review_conversation_sell(self, conversation_target, messages_history):
        role_prompt = get_prompt_by_title("__review_conversation_sell__")
        role_prompt = role_prompt.replace("__messages_history__", messages_history)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    async def ask_agent_to_review_conversation_buy(self, conversation_target, messages_history):
        role_prompt = get_prompt_by_title("__review_conversation_buy__")
        role_prompt = role_prompt.replace("__messages_history__", messages_history)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    def handle_agent_review_conversation_sell_result(self, content):
        if self.ai_chat_cfg.event_before_send_msg:
            if self.ai_chat_cfg.event_before_send_msg != "N/A":
                tool_name = self.ai_chat_cfg.event_before_send_msg
                self.handle_event_before_send_msg(tool_name, content, "sell")
                return

        self.handle_agent_review_conversation_sell_result_final(content)

    def handle_agent_review_conversation_sell_result_final(self, content):
        content = content.strip()
        result = json.loads(content)
        continue_chat = result["continue_chat"]
        current_chat_summary = result["summary"]
        message = result["next_message"]

        if not continue_chat:
            self.taskmng.add_process_info_to_list(f"和朋友沟通后得到如下情况：{current_chat_summary}")
            self.write_task_process_to_pane(f"和朋友沟通后得到如下情况：{current_chat_summary}\n\n")
            self.taskmng.current_situation = f"和别人沟通后，得到如下情况:{current_chat_summary}"
            asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n和别人沟通后，得到如下情况:{current_chat_summary}"))

        else:
            if self.taskmng.current_process["rounds_current_person"] < self.max_rounds_per_person:
                self.taskmng.current_process["rounds_current_person"] = self.taskmng.current_process["rounds_current_person"] + 1
                self.talk_to_a_people(message, self.current_talk_people["nation_id"], self.current_talk_people["account"], self.current_talk_people["nick_name"])
            else:
                self.taskmng.add_process_info_to_list(f"和朋友沟通后得到如下情况：{current_chat_summary}")
                self.taskmng.current_situation = f"和别人沟通后，得到如下情况:{current_chat_summary}"
                asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\n和别人沟通后，得到如下情况:{current_chat_summary}"))

    async def ask_agent_to_bargain_for_buyer(self, tool_list):
        messages_history = json.dumps(self.current_talk_history, ensure_ascii=False)
        conversation_target = self.taskmng.current_objective
        role_prompt = get_prompt_by_title("__buyer_bargain_content__")
        role_prompt = role_prompt.replace("__conversation_target__", conversation_target)
        role_prompt = role_prompt.replace("__messages_history__", messages_history)
        role_prompt = role_prompt.replace("__tool_list__", tool_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    def handle_ask_agent_to_bargain_for_buyer_result(self, content):
        result = json.loads(content)
        goal_achieved = result["goal_achieved"]
        continue_chat = result["continue_chat"]
        current_chat_summary = result["summary"]
        message = result["next_message"]
        self.tool_trade_send_bargain_for_buyer(content)

    async def ask_agent_to_bargain_for_seller(self, tool_list):
        messages_history = json.dumps(self.current_talk_history, ensure_ascii=False)
        conversation_target = self.taskmng.current_objective
        role_prompt = get_prompt_by_title("__seller_bargain_content__")
        role_prompt = role_prompt.replace("__conversation_target__", conversation_target)
        role_prompt = role_prompt.replace("__messages_history__", messages_history)
        role_prompt = role_prompt.replace("__tool_list__", tool_list)
        question = "请严格遵照要求评估，并严格按照格式输出。"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    def handle_ask_agent_to_bargain_for_seller_result(self, content):
        result = json.loads(content)
        goal_achieved = result["goal_achieved"]
        continue_chat = result["continue_chat"]
        current_chat_summary = result["summary"]
        message = result["next_message"]

        self.tool_trade_send_bargain_for_seller(content)


    def tool_trade_show(self, content, nationid, account, user_name):
        # self.write_thinking_process_to_pane(lt(f"Show tool detail to a people with {user_name} acount:{account},nationid:{nationid},content:{content}", f"向别人展现工具详情 with {user_name} acount:{account},nationid:{nationid},content:{content}"), "tool_trade_show")
        tool_list_str = f"AISNS_INT_001_TOOL_DETAIL_SHOW_START\n{json.dumps(self.get_mcp_list_for_trade(), indent=4, ensure_ascii=False)}\nAISNS_INT_001_TOOL_DETAIL_SHOW_END"
        content = f"{content}\n{tool_list_str}"
        command = ("start_talk_to_it", nationid, content)
        self.send_msg_to_map(command)
        self.sendMessage(content, False, account, user_name)
        if account not in self.talk_history:
            self.talk_history[account] = []
        self.talk_history[account].append("Me:" + content)
        self.current_talk_history.append("Me:" + content)

    def tool_trade_order(self, tool_list_str) -> None:
        trade_id = generate_random_id()

        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool_list_str:
            tool = json.loads(tool_list_str)
            name = tool["name"]
            mcp_record = query_mcp_mng(name=name)
            detail = mcp_record.description
            price = 6

        try:
            content = {
                "trade_id": trade_id,
                "name": name,
                "detail": detail,
                "price": price
            }

            message = f"AISNS_INT_002_TOOL_ORDER_START\n{json.dumps(content, indent=4, ensure_ascii=False)}\nAISNS_INT_002_TOOL_ORDER_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

        except Exception as e:
            print(f"Tool trade buy error: {str(e)}")

    def tool_trade_order_confirm(self, tool) -> None:
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        try:
            content = tool

            message = f"AISNS_INT_003_TOOL_ORDER_CONFIRM_START\n{json.dumps(content, indent=4, ensure_ascii=False)}\nAISNS_INT_003_TOOL_ORDER_CONFIRM_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

        except Exception as e:
            print(f"tool_trade_order_confirm error: {str(e)}")

    def tool_trade_send_tool(self, tool_list_str) -> None:
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        try:
            tool = json.loads(tool_list_str)
            id = tool.get("id", "")
            name = tool.get("name", "")
            price = tool["price"]
            detail = tool["detail"]
            mcp_record = query_mcp_mng(name=name)
            file_path = mcp_record.file_path

            filename = os.path.join(os.getcwd(), "mcp", file_path + ".json")
            if filename:
                with open(filename, "rt", encoding='utf-8') as file:
                    content = file.read()
            tool["mcp"] = json.loads(content)
            tool_str = json.dumps(tool, ensure_ascii=False, indent=4)
            message = f"AISNS_INT_004_TOOL_SEND_START\n{tool_str}\nAISNS_INT_004_TOOL_SEND_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

            trade_id = generate_random_id()
            trade_type = "S"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, pay=price, trade_with_name=trade_with_name, trade_with_account=trade_with_account)
            self.add_money(price)
            self.money = self.money + price
        except Exception as e:
            print(f"Tool trade sell error: {str(e)}")

    def send_pay(self, price) -> None:
        trade_id = generate_random_id()
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]
        try:
            message = f"AISNS_INT_001_PAY_SEND_START\n{trade_id}__AISNS_INT_SEPARATOR__{price}\nAISNS_INT_001_PAY_SEND_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

            self.money = self.money - price
            self.add_money(0 - price)
            trade_type = "B"
            title = f"Trade with {nick_name}"
            detail = "Waiting for goods"
            trade_with_name = nick_name
            trade_with_account = account

            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, pay=price, trade_with_name=trade_with_name, trade_with_account=trade_with_account)
        except Exception as e:
            print(f"Tool trade sell error: {str(e)}")

    def handle_pay_received(self, price_str) -> None:
        good_str = ""
        trade_id = ""
        talk_history_str = json.dumps(self.current_talk_history, ensure_ascii=False)
        if "__AISNS_INT_SEPARATOR__" in price_str:
            price_str = price_str.strip()
            trade_id = price_str.split("__AISNS_INT_SEPARATOR__")[0]
            trade_price = price_str.split("__AISNS_INT_SEPARATOR__")[1]

        self.current_trade_price = float(trade_price)

        try:
            record = query_AiChatCfg_map()
            profession = record.profession
            handle_after_trade = record.handle_after_trade
            handle_content = record.handle_content
            if profession == "doctor":
                good_str = handle_content
            elif profession == "driver":
                good_str = handle_content
            if profession == "seller":
                good_str = handle_content
            else:
                if handle_after_trade == "发送消息":
                    good_str = handle_content
                else:
                    tool_name = handle_content
                    tool_record = query_single_tool(name=tool_name)
                    tool_id = tool_record.id
                    what_to_do = "## 聊天记录 \n" + talk_history_str
                    print("run tool:", handle_content)
                    print("talk_history_str for run tool", talk_history_str)
                    self.command_status = "run_tool_before_send_good"
                    good_str = self.ask_agent_to_run_a_tool_sync(tool_id, tool_name, what_to_do)
                    return

            self.handle_send_goods(good_str, trade_id)


        except Exception as e:
            print(f"Tool trade sell error: {str(e)}")

    def handle_send_goods(self, good_str, trade_id):
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]
        price = self.current_trade_price

        try:
            if not trade_id:
                trade_id = generate_random_id()

            message = f"AISNS_INT_002_GOOD_SEND_START\n{trade_id}__AISNS_INT_SEPARATOR__{good_str}\nAISNS_INT_002_GOOD_SEND_END"
            self.talk_to_a_people(message, nation_id, account, nick_name)
            trade_type = "S"
            title = f"Trade with {nick_name}"
            detail = good_str
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, pay=price, trade_with_name=trade_with_name, trade_with_account=trade_with_account)
            self.add_money(price)
            self.money = self.money + price

        except Exception as e:
            print(f"Tool trade sell error: {str(e)}")

    def handle_good_received(self, goods_str) -> None:
        trade_id = ""
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if "__AISNS_INT_SEPARATOR__" in goods_str:
            goods_str = goods_str.strip()
            trade_id = goods_str.split("__AISNS_INT_SEPARATOR__")[0]
            goods_detail = goods_str.split("__AISNS_INT_SEPARATOR__")[1]

        try:
            update_map_trade(trade_id, detail=goods_detail)
        except Exception as e:
            print(f"Tool trade sell error: {str(e)}")

    def tool_trade_receive_tool(self, tool_list_str) -> None:
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        try:
            tool = json.loads(tool_list_str)
            name = tool["name"]
            price = tool["price"]
            detail = tool.get("detail", "")
            mcp = tool.get("mcp", "")
            content = json.dumps(mcp, ensure_ascii=False, indent=4)

            mcp_id = generate_random_id()
            instruction = ""
            file_path = mcp_id
            requirement = ""
            parameter = ""
            description = detail
            detail = detail
            mcp_type = "0"
            mcp_event = ""
            creator = ""

            add_mcp_mng(mcp_id, name, instruction, file_path, requirement, parameter, description, detail, mcp_type, mcp_event, creator)

            filename = os.path.join(os.getcwd(), "mcp", file_path + ".json")
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)  # 将文本写入文件

            trade_id = generate_random_id()
            trade_type = "B"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, pay=price, trade_with_name=trade_with_name, trade_with_account=trade_with_account)
            self.add_money(0 - price)
            self.money = self.money - price

        except Exception as e:
            print(f"tool_trade_receive_tool error: {str(e)}")

    def tool_trade_inquiry(self, tool) -> None:
        trade_id = generate_random_id()

        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool:
            tool.pop("reason_for_selection", None)  # 删除 'reason_for_selection' 键，如果不存在则不抛出异常
            tool.pop("match_score", None)

        try:
            content = tool

            message = f"AISNS_INT_005_TOOL_INQUIRY_START\n{json.dumps(content, indent=4, ensure_ascii=False)}\nAISNS_INT_005_TOOL_INQUIRY_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

        except Exception as e:
            print(f"Tool trade inquiry error: {str(e)}")

    def tool_trade_bargain_for_buyer(self, tool_list_str):
        self.command_status = "ask_agent_to_bargain_for_buyer"
        self.ask_agent_to_bargain_for_buyer(tool_list_str)

    def tool_trade_bargain_for_seller(self, tool_list_str):
        self.command_status = "ask_agent_to_bargain_for_seller"
        self.ask_agent_to_bargain_for_seller(tool_list_str)

    def tool_trade_send_bargain_for_buyer(self, tool_str) -> None:
        tool = json.loads(tool_str)
        trade_id = generate_random_id()

        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool:
            tool.pop("reason_for_selection", None)  # 删除 'reason_for_selection' 键，如果不存在则不抛出异常
            tool.pop("match_score", None)

        try:
            content = tool

            message = f"AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_START\n{json.dumps(content, indent=4, ensure_ascii=False)}\nAISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

        except Exception as e:
            print(f"Tool trade inquiry error: {str(e)}")

    def tool_trade_send_bargain_for_seller(self, tool_str) -> None:
        tool = json.loads(tool_str)
        trade_id = generate_random_id()

        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool:
            tool.pop("reason_for_selection", None)  # 删除 'reason_for_selection' 键，如果不存在则不抛出异常
            tool.pop("match_score", None)

        try:
            content = tool

            message = f"AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_START\n{json.dumps(content, indent=4, ensure_ascii=False)}\nAISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_END"

            self.talk_to_a_people(message, nation_id, account, nick_name)

        except Exception as e:
            print(f"Tool trade inquiry error: {str(e)}")

    def add_money(self, count):
        record = query_AiChatCfg_map()
        if record.money:
            money = record.money
        else:
            money = 0

        money = money + count

        update_AiChatCfg_map(money=money)

    def tool_trade_buy(self, tool) -> None:
        trade_id = generate_random_id()

        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool:
            id = tool["id"]
            name = tool["name"]
            type_str = tool["type"]
            detail = tool.get("description", "No Description")
        try:
            message = f"AISNS_INT_001_TN_{trade_id}_MN_{id}"

            self.talk_to_a_people(message, nation_id, account, nick_name)

            trade_type = "B"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, trade_with_name=trade_with_name, trade_with_account=trade_with_account)


        except Exception as e:
            print(f"Tool trade buy error: {str(e)}")

    def tool_trade_sell(self, trade_id, tool) -> None:
        current_talk_people = self.current_talk_people
        nation_id = current_talk_people["nation_id"]
        account = current_talk_people["account"]
        nick_name = current_talk_people["nick_name"]

        if tool:
            id = tool["id"]
            name = tool["name"]
            type_str = tool["type"]
            detail = tool.get("description", "No Description")
            file_path = tool.get("file_path", "")
        try:
            message = f"AISNS_INT_002_TN_{trade_id}_SYS_CONTENT_SENDING_FILE"

            self.talk_to_a_people(message, nation_id, account, nick_name)
            to_jid = account
            link = self.send_file_bg(self, file_path, to_jid)

            trade_type = "S"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(trade_id=trade_id, trade_type=trade_type, title=title, detail=detail, link=link, trade_with_name=trade_with_name, trade_with_account=trade_with_account)
        except Exception as e:
            logger.error(f"Tool trade initiate error: {str(e)}")

    def tool_trade_pay(self, trade_id, account) -> None:
        message = f"AISNS_INT_003_TN_{trade_id}"

        self.sendMessage(message, by_click=False, to_jid=account, to_name=None, back_ground=True)

        self.handle_as_coint("001", account)

        update_map_trade(trade_id, status=1)

    def tool_trade_paid(self, trade_id) -> None:
        update_map_trade(trade_id, status=1)

    def handle_as_coint(amount, type_str):
        pass


    def get_tool_list_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_001_TOOL_DETAIL_SHOW_START(.*?)AISNS_INT_001_TOOL_DETAIL_SHOW_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_tool_order_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_002_TOOL_ORDER_START(.*?)AISNS_INT_002_TOOL_ORDER_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_order_confirm_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_003_TOOL_ORDER_CONFIRM_START(.*?)AISNS_INT_003_TOOL_ORDER_CONFIRM_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_tool_mcp_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_004_TOOL_SEND_START(.*?)AISNS_INT_004_TOOL_SEND_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_tool_inquiry_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_005_TOOL_INQUIRY_START(.*?)AISNS_INT_005_TOOL_INQUIRY_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_buyer_bargain_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_START(.*?)AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_seller_bargain_in_message(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_START(.*?)AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            tool_list_string = match.group(1).strip()  # 提取并去除首尾空白
            return tool_list_string
        else:
            return None  # 如果没有匹配，返回 None

    def get_tool_url_in_message(self, msg):
        # 使用正则表达式提取需要的部分
        match = re.search(r'AISNS_INT_002_TN_(.*?)_SYS_CONTENT_(.*)', msg)

        if match:
            tn_value = match.group(1)  # 提取JC值
            url_value = match.group(2)  # 提取URL值
            return tn_value, url_value
        else:
            return None  # 未找到匹配，返回None

    def get_tool_url_in_message_v2(self, msg):
        # 使用正则表达式提取需要的部分

        match = re.search(r'AISNS_INT_002_TN_(.*?)_SYS_CONTENT_SENDING_FILE', msg)

        if match:
            tn_value = match.group(1)  # 提取JC值
            return tn_value
        else:
            return None  # 未找到匹配，返回None

    def get_tool_confirm_in_message(self, msg, prefix="AISNS_INT_003_TN_"):
        if msg.startswith(prefix):
            # 返回去掉前缀后的部分
            return msg[len(prefix):]
        else:
            # 如果前缀不匹配，返回原字符串
            return ""


    def check_skill(self, msg):
        if self.wait_for_trade_download_flag:
            if ".zip" in msg:
                self.received_skill(msg)
                trade_id = self.wait_for_trade_download_trade_id
                url = msg
                update_map_trade(trade_id, link=url)
                record_trade = query_single_map_trade(trade_id=trade_id)
                self.wait_for_trade_download_trade_id = ""
                self.wait_for_trade_download_flag = False
                tool_id = generate_random_id()
                add_map_tool(plugin_id=tool_id, name=record_trade.title, description=record_trade.detail)

    def received_skill(self, msg):
        url = self.get_url_from_msg(msg)
        file_name = os.path.basename(url)
        file__without_extension = os.path.splitext(file_name)[0]
        file_extension = os.path.splitext(file_name)[1]
        file_path = os.path.join(os.getcwd(), "download", file_name)

        if os.path.exists(file_path):
            current_timestamp = str(time.time()).replace('.', '')
            file_name = file__without_extension + current_timestamp + file_extension
            file_path = os.path.join(os.getcwd(), "download", file_name)
        self.download_file(url, file_path)
        self.skill_install(file_path)

    def check_tool_for_buy(self, msg):
        tool_list_str = self.get_tool_list_in_message(msg)
        return tool_list_str

    def check_tool_for_buyer_bargain(self, msg):
        tool_list_str = self.get_buyer_bargain_in_message(msg)
        return tool_list_str

    def check_tool_for_seller_bargain(self, msg):
        tool_list_str = self.get_seller_bargain_in_message(msg)
        return tool_list_str

    def check_tool_for_inquiry(self, msg):
        tool_list_str = self.get_tool_inquiry_in_message(msg)
        return tool_list_str

    def check_tool_for_order(self, msg):
        tool_list_str = self.get_tool_order_in_message(msg)
        return tool_list_str

    def check_tool_for_order_confirm(self, msg):
        tool_list_str = self.get_order_confirm_in_message(msg)
        return tool_list_str

    def check_tool_for_receive(self, msg):
        tool_list_str = self.get_tool_mcp_in_message(msg)
        return tool_list_str

    def check_tool_for_trade(self, msg):
        tool_list_str = self.get_tool_list_in_message(msg)
        if tool_list_str:
            tool_list = json.loads(tool_list_str)
            self.tool_trade_buy(tool_list[0])

    def check_tool_for_download(self, msg):
        trade_id = self.get_tool_url_in_message_v2(msg)
        if trade_id:
            self.wait_for_trade_download_flag = True
            self.wait_for_trade_download_trade_id = trade_id

        # result = self.get_tool_url_in_message(msg)
        # if result:
        #     trade_id = result[0]
        #     url = result[1]
        #     update_map_trade(trade_id, link=url)

    def check_tool_for_end(self, msg):
        trade_id = self.get_tool_confirm_in_message(msg)
        update_map_trade(trade_id, status=1)

    def check_pay_in_received(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_001_PAY_SEND_START(.*?)AISNS_INT_001_PAY_SEND_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            result = match.group(1).strip()  # 提取并去除首尾空白
            return result
        else:
            return None  # 如果没有匹配，返回 None

    def check_good_in_received(self, msg):
        """
            从输入字符串中提取 JSON 字符串，位于特定的起始和结束标记之间。

            :param msg: 包含 JSON 字符串的原始输入
            :return: 提取的 JSON 字符串，如果未找到则返回 None
            """
        # 定义正则表达式模式，使用原始字符串以避免转义字符的问题
        pattern = r'AISNS_INT_002_GOOD_SEND_START(.*?)AISNS_INT_002_GOOD_SEND_END'

        # 使用 re.search 查找符合模式的部分
        match = re.search(pattern, msg, re.DOTALL)  # DOTALL 使 . 可以匹配换行符

        # 检查是否找到匹配，并返回提取的内容
        if match:
            result = match.group(1).strip()  # 提取并去除首尾空白
            return result
        else:
            return None  # 如果没有匹配，返回 None

    def check_buy_in_received(self, msg):
        pattern = '[AISNS_INT_003_INQUIRY]'

        if pattern in msg:
            return True
        else:
            return False

    def get_url_from_msg(self, msg):
        url = msg
        return url


    def create_skill_cfg(skill_id, skill_name):
        """创建技能配置文件并将其写入指定路径。

        参数:
            skill_id (int): 技能的唯一标识符。
            skill_name (str): 技能的名称，用于生成配置文件名。

        返回:
            str: 配置文件的路径。
        """
        # 查询技能记录
        record = query_function_mng(function_id=skill_id)

        # 构建技能配置字典
        skill_cfg = {
            "name": record.name,
            "description": record.description,
            "detail": record.detail
        }

        # 构建配置文件路径
        cfg_file_path = os.path.join(os.getcwd(), "coding", f"{skill_name}.json")

        # 将配置写入 JSON 文件
        try:
            with open(cfg_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(skill_cfg, json_file, ensure_ascii=False, indent=4)
        except IOError as e:
            raise IOError(f"Failed to write config file: {cfg_file_path}. Error: {e}")

        return cfg_file_path

    def create_skill_zip(skill_name):
        """将指定技能的 Python 文件和配置文件压缩成一个 ZIP 文件。

        参数:
            skill_name (str): 技能名称，用于构建文件路径。

        返回:
            str: 压缩文件的路径。
        """
        # 构造文件路径
        python_file_path = os.path.join(os.getcwd(), "coding", f"{skill_name}.py")
        cfg_file_path = os.path.join(os.getcwd(), "coding", f"{skill_name}.json")
        file_path = os.path.join(os.getcwd(), "coding", f"{skill_name}.zip")

        # 确保要压缩的文件存在
        if not os.path.exists(python_file_path):
            raise FileNotFoundError(f"Python file does not exist: {python_file_path}")

        if not os.path.exists(cfg_file_path):
            raise FileNotFoundError(f"Config file does not exist: {cfg_file_path}")

        # 创建 ZIP 文件并写入文件
        with zipfile.ZipFile(file_path, 'w') as zipf:
            # 将 Python 文件添加到 ZIP
            zipf.write(python_file_path, os.path.basename(python_file_path))
            # 将配置文件添加到 ZIP
            zipf.write(cfg_file_path, os.path.basename(cfg_file_path))

        return file_path

    def download_file(self, url, file_path):
        # 发送 GET 请求并获取响应对象
        response = requests.get(url)

        # 检查响应状态码是否为成功
        if response.status_code == 200:
            # 打开文件并写入响应内容
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"文件 '{file_path}' 下载成功！")
        else:
            print(f"下载失败，状态码：{response.status_code}")

    def skill_install(self, zip_file_path):
        """
        Installs a skill from a zip file by extracting its contents,
        processing a JSON file for database entry, and moving a Python
        file to a specified directory.

        Parameters:
        zip_file_path (str): Path to the zip file containing the skill.
        """
        # Obtain the base name of the zip file without the extension
        file_without_extension = os.path.splitext(os.path.basename(zip_file_path))[0]
        # Define the extraction path for the zip contents
        extract_to_path = os.path.join(os.getcwd(), "download", "temp", file_without_extension)

        # Unzip the file to the specified directory
        self.unzip_file(zip_file_path, extract_to_path)

        # Define the directory to move Python files to
        python_files_dest = os.path.join(os.getcwd(), "coding")

        # Iterate over all files in the extracted path
        for root, dirs, files in os.walk(extract_to_path):
            for file in files:
                # Get full file path
                file_path = os.path.join(root, file)

                # Check if the file is a JSON file
                if file.endswith('.json'):
                    # Open and load the JSON file
                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)
                    # Assuming `record` is the parsed data
                    add_function_mng(
                        function_id=generate_random_id(),  # Assuming you generate or fetch this ID elsewhere
                        name=data["name"],
                        file_path=None,  # Assuming you set this path elsewhere, possibly `python_file_path`
                        requirement=None,  # Placeholder, set appropriately
                        parameter=None,  # Placeholder, set appropriately
                        description=data["description"],
                        detail=data["detail"],
                        function_type=None,  # Placeholder, set appropriately
                        function_event=None,  # Placeholder, set appropriately
                        creator=None  # Placeholder, set appropriately
                    )

                # Check if the file is a Python file
                elif file.endswith('.py'):
                    # Define destination path for the Python file
                    python_file_dest = os.path.join(python_files_dest, file)
                    # Copy the Python file to the destination directory
                    shutil.copy(file_path, python_file_dest)

        self.ask_human_to_check_skill()

    def unzip_file(self, zip_file_path, extract_to_path):
        # 创建一个ZipFile对象，并打开要解压的zip文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 解压缩到指定位置
            zip_ref.extractall(extract_to_path)

        print("解压缩完成！")

    def on_agent_make_deal_finished(self, content: str) -> None:
        """
        处理大模型返回的决策结果
        Args:
            content: 大模型返回的决策内容
        """
        try:
            decision_data = self._parse_decision(content)
            if not decision_data:
                logger.warning("无法解析大模型返回结果")
                return

            # 根据决策类型处理交易
            if decision_data["decision"] == TransactionType.SKILL_EXCHANGE:
                self._handle_skill_exchange(
                    target_skill=decision_data["target_skill"],
                    offer_skill=decision_data["offer_skill"]
                )
            elif decision_data["decision"] == TransactionType.TOKEN_PURCHASE:
                self._handle_token_purchase(
                    target_skill=decision_data["target_skill"]
                )
        except Exception as e:
            logger.error(f"交易处理失败: {str(e)}")

    def _parse_decision(self, content: str) -> Optional[Dict]:
        """
        解析大模型的决策结果
        Returns:
            dict: 包含decision_type, target_skill, offer_skill的字典
        """
        try:
            decision = json.loads(content)
            if not all(key in decision for key in ["decision", "target_skill"]):
                raise ValueError("无效的决策格式")

            decision["decision"] = TransactionType.SKILL_EXCHANGE if decision["decision"] == "exchange" else TransactionType.TOKEN_PURCHASE

            if decision["decision"] == TransactionType.SKILL_EXCHANGE and decision["offer_skill"] not in self.available_skills:
                raise ValueError("无法提供的技能不在可交换列表中")

            return decision
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"决策解析失败: {str(e)}")
            return None

    def _handle_skill_exchange(self, target_skill: dict, offer_skill: dict) -> None:
        """处理技能交换逻辑"""
        if offer_skill not in self.available_skills:
            logger.warning("技能交换请求缺少提供技能")
            return

        logger.info(f"执行技能交换：用 [{offer_skill}] 交换 [{target_skill}]")
        self.available_skills = self.remove_dict_from_list(self.available_skills, offer_skill)
        self.required_skills = self.remove_dict_from_list(self.required_skills, target_skill)
        self.available_skills.append(target_skill)

    def remove_dict_from_list(self, dict_list, t_dict):
        """
        从 available_skills 中移除 offer_skill 字典。

        参数:
        offer_skill (dict): 需要移除的字典
        """
        # 过滤列表，保留不等于 offer_skill 的字典
        dict_list = [dict_item for dict_item in dict_list if dict_item != t_dict]
        return dict_list

    def _handle_token_purchase(self, target_skill: dict) -> None:
        """处理Token购买逻辑"""
        if self.token_balance < 100:
            logger.warning("Token余额不足，无法购买技能")
            return

        logger.info(f"使用100 Token购买技能 [{target_skill}]")
        self.token_balance -= 100
        self.required_skills = self.remove_dict_from_list(self.required_skills, target_skill)
        self.available_skills.append(target_skill)

    def on_human_confirm_skill(self):
        skill_list = self.get_skill_list()
        self.update_skill(skill_list)

    def on_human_reject_skill(self):
        self.move_on()
