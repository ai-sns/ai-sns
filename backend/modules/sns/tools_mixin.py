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


class ToolsMixin:

    def use_tools(self):
        result = ""

        result = "使用工具成功。"
        return result

    def get_ability_list(self):
        # ability_list_str = get_key_value("ability_list")
        # ability_list = json.loads(ability_list_str)
        # self.ability_list = ability_list

        result = self.ability_list

        return result

    def get_skill_list(self):
        return []
        result = """
                    [{
		"id": "001",
		"name": "get_weather",
		"description": "get weather of a city",
		"place": "Any Place",
		"lng": 0,
		"lat": 0,
		"type": "plugin_tool",
		"address": "Not needed",
		"method": "python call",
		"parameter": {
			"city": "the city to get the weather",
			"date": "the date to get the weather"
		}
	},
	{
		"id": "002",
		"name": "get_stock",
		"description": "get the stock price of a company",
		"place": "Any Place",
		"lng": 0,
		"lat": 0,
		"type": "plugin_tool",
		"address": "Not needed",
		"method": "python call",
		"parameter": {
			"company": "the company name to get the stock price"
		}

	},
	{
		"id": "003",
		"name": "Calculator",
		"description": "a calculator for number",
		"place": "Any Place",
		"lng": 0,
		"lat": 0,
		"type": "plugin_tool",
		"address": "Not needed",
		"method": "python call",
		"parameter": {
			"operator": "choose from `+ / - *` for the calculator to perform calculate",
			"first_number":"the first number",
			"second_number":"the second number"
		}
	}
]
                """

        self.skill_list = json.loads(result)  # 保存到全局变量
        self.available_skills = self.skill_list  # self.skill_list = list(self.available_skills)
        result = self.skill_list
        return result

    def update_skill(self, skill_list):
        asyncio.create_task(self.taskmng.process_task(event="skill_updated"))

    def get_plugin_tool_list(self):
        records = query_tool_list()
        default_values = {
            "place": "Any Place",
            "lng": 0,
            "lat": 0,
            "type": "plugin_tool",
            "address": "Not needed",
            "method": "python call"
        }
        # 使用列表推导式生成所需格式的记录
        formatted_records = [
            {
                "id": record.id,  # 直接访问属性
                "name": record.name,
                "description": record.description,
                **default_values  # 展开 default_values 字典以添加缺省值
            }
            for record in records
        ]

        return formatted_records

    def get_service_list(self):
        url = "http://www.ai-sns.org/api/get_service_list/"

        pos = self.aichatcfg_record.current_position

        params = {
            "lng": pos[0],
            "lat": pos[1]
        }
        service_list = self.http_request(url, params)
        return service_list

    def update_service_list(self):
        url = "http://www.ai-sns.org/api/get_service"
        params = {
            "lng": self.aichatcfg_record.current_position[0],
            "lat": self.aichatcfg_record.current_position[1]
        }
        # people={
        #     "name":"Same",
        #     "position":[121.121,23.4554]
        # }
        service_list = self.http_request(url, params)

        return service_list

    def get_tool_list(self):
        service_list = self.get_service_list()
        skill_list = self.get_skill_list()
        plugin_tool_list = self.get_plugin_tool_list()
        tool_list = service_list + skill_list + plugin_tool_list
        return tool_list

    def get_tool_list_for_trade(self):
        service_list = self.get_service_list()
        skill_list = self.get_skill_list()
        tool_list = service_list + skill_list
        return tool_list

    def get_mcp_list_for_trade(self):
        service_list = self.get_service_list()
        skill_list = self.get_skill_list()
        tool_list = service_list + skill_list
        return tool_list


    def ask_agent_to_pick_a_tool_sync(self, task_summary, provided_tool_list_str, human_objective_to_achieve=""):
        task_summary = self.taskmng.get_task_summary()
        curren_situation = self.taskmng.current_situation
        objective_to_achieve = self.taskmng.get_current_objective()
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        current_process = f"- 当前目标\n{objective_to_achieve}\n- 当前进展\n{curren_situation}"
        role_prompt = get_prompt_by_title("__pick_tool_list__")
        if self.human_take_over and self.human_instruction.startswith("!!!"):
            role_prompt = role_prompt.replace("__task_summary__", self.human_instruction)
            role_prompt = role_prompt.replace("__current_process__", "")
        else:
            role_prompt = role_prompt.replace("__task_summary__", task_summary)
            role_prompt = role_prompt.replace("__current_process__", current_process)
        role_prompt = role_prompt.replace("__provided_tool_list__", provided_tool_list_str)

        question = "请严格遵照要求评估，并严格按照格式输出。"
        asyncio.create_task(self.ask_agent_and_get_instruction(question, role_prompt))

    # 5.让agent选择一个工具
    async def ask_agent_to_pick_a_tool(self, task_summary, provided_tool_list_str, human_objective_to_achieve=""):
        task_summary = self.taskmng.get_task_summary()
        curren_situation = self.taskmng.current_situation
        objective_to_achieve = self.taskmng.get_current_objective()
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"

        current_process = f"- 当前目标\n{objective_to_achieve}\n- 当前进展\n{curren_situation}"
        role_prompt = get_prompt_by_title("__pick_tool_list__")
        if self.human_take_over and self.human_instruction.startswith("!!!"):
            role_prompt = role_prompt.replace("__task_summary__", self.human_instruction)
            role_prompt = role_prompt.replace("__current_process__", "")
        else:
            role_prompt = role_prompt.replace("__task_summary__", task_summary)
            role_prompt = role_prompt.replace("__current_process__", current_process)
        role_prompt = role_prompt.replace("__provided_tool_list__", provided_tool_list_str)

        question = "请严格遵照要求评估，并严格按照格式输出。"
        await self.ask_agent_and_get_instruction(question, role_prompt)

    # 5.1处理agent选择的工具
    def handle_agent_pick_a_tool_result(self, content):
        """
        处理代理选择云端服务的结果。

        :param content: 代理返回的结果内容
        """
        result_list = json.loads(content)
        if result_list:
            tool = result_list[0]
            id = tool["id"]
            name = tool["name"]
            type_str = tool["type"]
            reason_for_selection = tool["reason_for_selection"]
            tell_the_tool_what_to_do = tool["tell_the_tool_what_to_do"]
            match_score = tool["match_score"]

            self.taskmng.add_process_info_to_list(f"我已经选定了目标工具：name:{name},id:{id},因为{reason_for_selection}")
            flag, res = self.call_tool(tool)
            if flag == "success":
                self.taskmng.add_process_info_to_list("Use_tool使用工具成功，获得如下反馈：" + res)
                self.write_task_process_to_pane("Use_tool使用工具成功，获得如下反馈：" + res + "\n\n")
                # self.write_thinking_process_to_pane("Use_tool使用工具成功，获得如下反馈：" + res)
                self.taskmng.current_situation = "Use_tool使用工具成功，获得如下反馈：" + res
                ask_content = f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\nUse_tool使用工具成功，获得如下反馈：{res}"
                asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=ask_content))
            elif flag == "fail":
                self.taskmng.add_process_info_to_list("Use_tool使用工具失败，获得如下反馈：" + res)
                self.taskmng.current_situation = "Use_tool使用工具失败，获得如下反馈：" + res
                self.write_task_process_to_pane("Use_tool使用工具失败，获得如下反馈：" + res + "\n\n")
                # self.write_thinking_process_to_pane("Use_tool使用工具失败，获得如下反馈：" + res)
                ask_content = f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\nUse_tool使用工具失败，获得如下反馈：{res}"
                asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=ask_content))

    def call_tool(self, tool):
        tool_id = tool["id"]
        name = tool["name"]
        type_str = tool["type"]
        reason_for_selection = tool["reason_for_selection"]
        tell_the_tool_what_to_do = tool["tell_the_tool_what_to_do"]
        match_score = tool["match_score"]

        tool_list = self.get_tool_list()
        tool_full = self.get_dict_by_id(tool_list, tool_id)
        if type_str.lower() == "built_in_function":
            flag, result = self.call_built_in_function(tool_full)
            return flag, result

        elif type_str.lower() == "plugin_tool":
            flag, result = self.ask_agent_to_run_a_tool_sync(tool_id, name, tell_the_tool_what_to_do)
            return flag, result

        elif type_str.lower() == "web_service":
            flag, result = self.call_built_in_function(tool_full)
            return flag, result

        elif type_str.lower() == "map_application":
            flag, result = self.call_built_in_function(tool_full)
            return flag, result

        elif type_str.lower() == "website":
            flag, result = self.call_built_in_function(tool_full)
            return flag, result

        else:
            flag = "fail"
            result = "任务失败。"
            return flag, result

    def call_built_in_function(self, tool):
        name = tool.get("name", "")
        if name == "Check in":
            flag, result = self.check_in_at_a_place(tool)
            return flag, result

        elif name == "Get clues":
            flag, result = self.get_a_clue_at_a_place(tool)
            return flag, result

        else:
            pass


    async def ask_agent_to_run_a_tool(self, tool_id, tool_name, what_to_do):
        role_prompt = "You are a helpful assistant."


        question = f"{tool_id}__AISNS_INT_SEPARATOR__{tool_name}__AISNS_INT_SEPARATOR__{what_to_do}"
        await self.ask_agent_and_get_instruction(question, role_prompt, "tool")
        return "success", "asking the agent to run tool"


    def ask_agent_to_run_a_tool_sync(self, tool_id, tool_name, what_to_do):
        role_prompt = "You are a helpful assistant."

        question = f"{tool_id}__AISNS_INT_SEPARATOR__{tool_name}__AISNS_INT_SEPARATOR__{what_to_do}"
        asyncio.create_task(self.ask_agent_and_get_instruction(question, role_prompt, "tool"))
        return "success", "asking the agent to run tool"


    async def ask_agent_to_use_service(self, question, service_list, objective_to_achieve):
        role_prompt = get_prompt_by_title("__ask_agent_use_service__")
        role_prompt = role_prompt.replace("__service_list__", service_list)
        role_prompt = role_prompt.replace("__objective_to_achieve__", objective_to_achieve)

        question = question + "\n请根据相关的任务要求，准确选择服务，如果没有合适的服务请返回空列表。"

        self.command_status = "ask_agent_to_use_service"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    def on_ask_agent_to_use_service_return(self, content):
        command_status = self.command_status
        code = self.parse_content_to_call_service(content)
        self.call_service(code)

    def parse_content_to_call_service(self, content):
        try:
            data = json.loads(content)
            url = data["address"]
            method = data.get("method", "get").lower()  # Default to 'get' if not specified or invalid
            params = data.get("Parameter", {})  # Use "Parameter" key, handle missing key gracefully

            if not isinstance(url, str) or not url.startswith("http"):
                raise ValueError("Invalid 'address' value. Must be a valid URL.")

            if method not in ["get", "post", "put", "delete", "patch"]:  # Validate method
                raise ValueError("Invalid 'method' value. Supported methods: get, post, put, delete, patch")

            response = self.call_service(url, method, **params)
            return response  # Return the response

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error processing content: {e}")
            return None  # or raise the exception, depending on desired behavior

    def call_service(self, url, method, **params):
        try:
            if method == "get":
                response = requests.get(url, params=params)
            elif method == "post":
                response = requests.post(url, data=params)  # Use 'data' for post
            elif method == "put":
                response = requests.put(url, data=params)
            elif method == "delete":
                response = requests.delete(url, params=params)  # params can also be used with delete
            elif method == "patch":
                response = requests.patch(url, data=params)

            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            self.handle_service_called_result(response.json())  # Assuming the response is JSON, parse and return it
        except requests.exceptions.RequestException as e:
            print(f"Error calling service: {e}")
            return None  # Or handle the error as needed, e.g., retry, log, etc.

    def handle_service_called_result(self, response):
        exit_code = response["exit_code"]
        output = response["output"]
        if exit_code == 0:
            asyncio.create_task(self.taskmng.process_task(event="service_called", result=output))

        else:
            asyncio.create_task(self.taskmng.process_task(event="service_called", result=f"Execute Error,the output:{output}"))

    async def ask_agent_to_use_skill(self, question, function_name, function_description):
        role_prompt = get_prompt_by_title("__ask_agent_use_skill__")
        role_prompt = role_prompt.replace("XXXXXXXX", function_name)
        role_prompt = role_prompt + "\n" + function_description

        question = "\n" + question + "这是我建议使用的函数：" + function_name + "，请根据相关的任务要求，把相关的任务完成掉。"
        question = question + "\n请输出完整的可独立运行的代码。"
        self.command_status = "ask_agent_to_use_skill"
        await  self.ask_agent_and_get_instruction(question, role_prompt)

    def on_ask_agent_to_use_skill_return(self, content):
        command_status = self.command_status
        code = self.parse_content_to_code(content)
        self.execute_skill(code)

    def parse_content_to_code(self, content):
        code = content
        return code

    def execute_skill(self, code):
        execute_result = "waiting to impl"
        self.handle_skill_executed_result(execute_result)

    def handle_skill_executed_result(self, execute_result):
        exit_code = execute_result.exit_code
        output = execute_result.output
        code_file = execute_result.code_file
        if exit_code == 0:
            asyncio.create_task(self.taskmng.process_task(event="skill_executed", result=output))

        else:
            asyncio.create_task(self.taskmng.process_task(event="skill_executed", result=f"Execute Error,the output:{output}"))

