from __future__ import annotations

import re
import time
import typing
from pathlib import Path
import shutil
import autogen
from PyQt6.QtCore import QThread
from autogen.coding import LocalCommandLineCodeExecutor
from termcolor import colored

from db.DBFactory import (add_AgentCfg, query_AgentCfg, query_AgentCfg_All, update_AgentCfg,
                          delete_AgentCfg, add_AgentTask, get_prompt_by_title, get_prompt_by_id,
                          get_agent_system_prompt, get_agent_specialization_description, query_workflow_mng, query_function_mng,
                          query_KMCfg, query_function_mng_all, query_PluginMng_All_Tool, query_workflow_mng_all,query_mcp_mng
                          )

from db.DBFactory import query_workflow_mng, add_workflow_mng, update_workflow_mng

from langchainhandler import getvectorkm_String
from datetime import datetime
import sys
from agent.llm import OpenAICompatibleLLMClient, CustomizeClient, SparkAI, OpenAICustomizeLLMClient, OpenAICustomizeV2LLMClient, AnthropicClient
import subprocess

sys.path.append("..")
sys.path.append("../..")

from globals import global_plugin_list
from util import format_string_for_run_javascript, get_content_from_attachment_content_list, generate_random_id, download_image,get_file_full_path
import json
import os
import ast

from autogen import AssistantAgent, UserProxyAgent, NoEligibleSpeaker
from typing import Annotated, Literal, List
import inspect
import logging
import sys
import uuid
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union, Literal, Annotated

from flaml.automl.logger import logger_formatter
from pydantic import BaseModel

from autogen.cache import Cache
from autogen.io.base import IOStream
from autogen.logger.logger_utils import get_current_ts
from autogen.oai.openai_utils import OAI_PRICE1K, get_key, is_valid_api_key
from autogen.runtime_logging import log_chat_completion, log_new_client, log_new_wrapper, logging_enabled
from autogen.token_count_utils import count_token
from autogen.oai.groq import GroqClient

from pathlib import Path

from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor

# IOStream处理
from autogen.io.base import IOStream
from rich.console import Console
from rich.text import Text
from typing import Any

from typing import Union, List

from agent.io import AISNSIOStream

from autogen import ConversableAgent, UserProxyAgent, config_list_from_json, register_function
from autogen import oai
from enum import Enum
import os
import requests
import json
from datetime import datetime
from agent.tools import *
from pluginsmanager.plugins_headless.plugin_mng import load_plugin as load_plugin_headless
from i18n import lt

TOOL_ENABLED = False
try:
    import openai
except ImportError:
    ERROR: Optional[ImportError] = ImportError("Please install openai>=1 and diskcache to use autogen.OpenAIWrapper.")
    OpenAI = object
    AzureOpenAI = object
else:
    # raises exception if openai>=1 is installed and something is wrong with imports
    from openai import APIError, APITimeoutError, AzureOpenAI, OpenAI
    from openai import __version__ as OPENAIVERSION
    from openai.resources import Completions
    from openai.types.chat import ChatCompletion
    from openai.types.chat.chat_completion import ChatCompletionMessage, Choice  # type: ignore [attr-defined]
    from openai.types.chat.chat_completion_chunk import (
        ChoiceDeltaFunctionCall,
        ChoiceDeltaToolCall,
        ChoiceDeltaToolCallFunction,
    )
    from openai.types.completion import Completion
    from openai.types.completion_usage import CompletionUsage

    if openai.__version__ >= "1.1.0":
        TOOL_ENABLED = True
    ERROR = None

try:
    from autogen.oai.gemini import GeminiClient
    from autogen.oai.client import OpenAIWrapper

    gemini_import_exception: Optional[ImportError] = None
except ImportError as e:
    gemini_import_exception = e

logger = logging.getLogger(__name__)
if not logger.handlers:
    # Add the console handler.
    _ch = logging.StreamHandler(stream=sys.stdout)
    _ch.setFormatter(logger_formatter)
    logger.addHandler(_ch)

LEGACY_DEFAULT_CACHE_SEED = 0  # 41
LEGACY_CACHE_DIR = ".cache"
OPEN_API_BASE_URL_PREFIX = "https://api.openai.com"

global_browser_page = None

import typing
from typing import Literal
from typing import List, Tuple

import os
import urllib
from datetime import datetime

from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog
from PyQt6.QtCore import QSettings, Qt, QUrl, QFile, QFileInfo
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem

import autogen
from autogen.agentchat.conversable_agent import ConversableAgent

from groupchat import GroupChatManager, GroupChat
from autogen.cache import Cache
from autogen.io.base import IOStream
from autogen.logger.logger_utils import get_current_ts
from autogen.oai.openai_utils import OAI_PRICE1K, get_key, is_valid_api_key
from autogen.runtime_logging import log_chat_completion, log_new_client, log_new_wrapper, logging_enabled
from autogen.token_count_utils import count_token

# IOStream处理
from autogen.io.base import IOStream

from db.DBFactory import query_MutiAgentCfg, query_AgentCfg
from db.DBFactory import add_AgentTaskMulti, query_PluginMng_All_Tool, query_mcp_mng_all, query_mcp_mng

from langchainhandler import getvectorkm_String
from agent.io import AISNSIOStream

import hashlib
import webbrowser
from db.DBFactory import add_AgentTask
import http.client
import json
from pluginsmanager import PluginEngine

import argparse

from pluginsmanager import FileSystem

import urllib.request
import re

import sys
from i18n import lt

sys.path.append("../..")
sys.path.append("../../..")

from db.DBFactory import add_KMCfg, query_KMCfg_All, update_KMCfg, delete_KMCfg, query_KMCfg
from db.DBFactory import add_PluginMng, query_PluginMng_All, update_PluginMng, delete_PluginMng, query_PluginMng,query_skill_mng
from globals import global_plugin_list
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from util import format_string_for_run_javascript
import util
from agent.llm import OpenAICompatibleLLMClient, CustomizeClient, SparkAI, OpenAICustomizeLLMClient, OpenAICustomizeV2LLMClient, AnthropicClient


# 调用了自定义的groupchat.py中的groupchat，增加了speaker_selection_agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)，原来的代码不支持自定义大模型客户端


class Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


class Calculator():
    def __init__(self):
        pass

    @staticmethod
    def calculator(a: str, b: str, operator: str) -> int:
        """
        你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格

        Args:
            a (str): 地点，比如：上海.
            b (str): 时间，比如：今天.
            operator (str): 是否获取温度，比如：是.

        Returns:
            str: 返回具体的煤炭价格.


        """
        if operator == "+":
            return a + b
        elif operator == "-":
            return a - b
        elif operator == "*":
            return a * b
        elif operator == "/":
            if b == 0:
                raise ValueError("Division by zero")
            return int(a / b)
        else:
            raise ValueError("Invalid operator")


class AgentMode(Enum):
    ChatOnly = 1
    Task = 2


from groupchat import GroupChatManager, GroupChat
from PyQt6.QtCore import QThread, pyqtSignal
from db.DBFactory import AgentCfg, MutiAgentCfg, query_PluginMng


class AgentManager(GroupChatManager):
    # GroupChatManager使用了自定义的GroupChatManager
    def __init__(
            self,
            agent_manager_cfg: AgentCfg,
            agent_group_cfg: MutiAgentCfg,
            agent_group: AgentGroup,
            groupchat: GroupChat,
            name: Optional[str] = "chat_manager",
            # unlimited consecutive auto reply by default
            max_consecutive_auto_reply: Optional[int] = sys.maxsize,
            human_input_mode: Optional[str] = "ALWAYS",
            system_message: Optional[Union[str, List]] = "Group chat manager.",
            silent: bool = True,
            **kwargs,
    ):
        self.agent_commander_cfg = agent_manager_cfg
        self.agent_group_cfg = agent_group_cfg
        self.agent_group = agent_group
        if (
                kwargs.get("llm_config")
                and isinstance(kwargs["llm_config"], dict)
                and (kwargs["llm_config"].get("functions") or kwargs["llm_config"].get("tools"))
        ):
            raise ValueError(
                "GroupChatManager is not allowed to make function/tool calls. Please remove the 'functions' or 'tools' config in 'llm_config' you passed in."
            )

        super().__init__(
            groupchat=groupchat,
            name=name,
            # unlimited consecutive auto reply by default
            max_consecutive_auto_reply=max_consecutive_auto_reply,
            human_input_mode=human_input_mode,
            system_message=system_message,
            silent=silent,
            **kwargs,
        )
        self.register_reply(Agent, AgentManager.run_chat, config=groupchat, reset_config=GroupChat.reset)
        # self.go_register_client()

    def run_chat(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[GroupChat] = None,
            is_agent_manager: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """Run a group chat."""
        iostream = IOStream.get_default()
        print("cjrok running the chat")
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speak_person = sender
        groupchat = config
        send_introductions = getattr(groupchat, "send_introductions", False)
        silent = getattr(self, "_silent", False)

        if send_introductions:
            # Broadcast the intro
            intro = groupchat.introductions_msg()
            for agent in groupchat.agents:
                self.send(intro, agent, request_reply=False, silent=True)
            # NOTE: We do not also append to groupchat.messages,
            # since groupchat handles its own introductions

        if self.client_cache is not None:
            for a in groupchat.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache
        for i in range(groupchat.max_round):
            groupchat.append(message, speak_person)
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speak_person:
                    self.send(message, agent, request_reply=False, silent=True)
            if self._is_termination_msg(message) or i == groupchat.max_round - 1:
                # The conversation is over or it's the last round
                break
            try:
                # select the next speaker
                if not is_agent_manager:
                    self.agent_group.show_group_select_agent_title()

                time.sleep(0.3)
                iostream.print(lt("👨‍🏫Group select the Agent below to process:", "👨‍🏫群主选择如下Agent来执行任务:"))
                speak_person = groupchat.select_speaker(speak_person, self)
                # if not silent:

                # iostream.print(colored(f"\ncjr get the Next speaker: {speaker.name}userid:{speaker.agent_cfg.user_id}\n", "green"), flush=True)
                iostream.print(f"Agent Manager select the next agent:{speak_person.agent_cfg.user_id if speak_person.agent_cfg else speak_person.name}", flush=True)
                # iostream.print(f"Agent Manager select the next agent:Musk", flush=True)

                # let the speaker speak
                # reply = speaker.generate_reply(sender=self)
                # print("cjr get the run chat reply of selected agent:", reply)
                self.agent_group.current_selected_agent = speak_person
                # 上面几句改成了线程模式
                self.send_msg_to_speak_person(speak_person)
                return True, None


            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speak_person = groupchat.agent_by_name(groupchat.admin_name)
                    reply = speak_person.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            except NoEligibleSpeaker:
                # No eligible speaker, terminate the conversation
                break

            if reply is None:
                # no reply is generated, exit the chat
                break

            # check for "clear history" phrase in reply and activate clear history function if found
            if (
                    groupchat.enable_clear_history
                    and isinstance(reply, dict)
                    and reply["content"]
                    and "CLEAR HISTORY" in reply["content"].upper()
            ):
                reply["content"] = self.clear_agents_history(reply, groupchat)

            # The speaker sends the message without requesting a reply
            speak_person.send(reply, self, request_reply=False, silent=silent)
            message = self.last_message(speak_person)
            # return True, None
        if self.client_cache is not None:
            for a in groupchat.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None
        return True, None


    def send_msg_to_speak_person(self, recipient: Agent):
        print("new sendmsgtospeakperson")
        agent_manager = self
        agent = recipient
        assist_agent = recipient
        # assist_agent = AssistantAgent(
        #     name=agent._name,
        #     human_input_mode=agent.human_input_mode,
        #     system_message=agent.agent_cfg.prompt,
        #     chat_messages=recipient.chat_messages,
        #     llm_config={"cache_seed": None, "config_list": [agent.llm_config]},  # 注意格式和openai不同
        # )
        #
        # assist_agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        agent_human = UserProxyAgent(
            "AgentHuman",
            human_input_mode="ALWAYS",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=10,

        )

        messages = [message for message in agent_manager.groupchat.messages]
        message = messages[-1]
        chat_result = agent_human.initiate_chat(
            assist_agent,
            silent=True,
            message=message,
            clear_history=False
        )

        print("chatresult:", chat_result)

        # reply = agent.generate_reply(messages=messages)
        # print("checking stop002-02")
        # reply = reply['content'] if isinstance(reply, dict) and 'content' in reply else reply

        reply = chat_result.summary

        agent_manager.send_me_your_feedback(assist_agent, reply)

        return True

    def send_me_your_feedback(self, speak_person, reply):
        groupchat = self.groupchat
        silent = getattr(self, "_silent", False)
        reply = reply

        if reply is None:
            # no reply is generated, exit the chat
            return None

        # check for "clear history" phrase in reply and activate clear history function if found
        if (
                groupchat.enable_clear_history
                and isinstance(reply, dict)
                and reply["content"]
                and "CLEAR HISTORY" in reply["content"].upper()
        ):
            reply["content"] = self.clear_agents_history(reply, groupchat)

        # The speaker sends the message without requesting a reply
        # 根据speaker类型设置是否silent
        if speak_person.name == "Executor":
            silent = False

        speak_person.send(reply, self, request_reply=False, silent=silent)
        # message = self.last_message(speaker)
        # groupchat.append(message, speaker)
        self.run_chat(sender=speak_person, config=self.groupchat, is_agent_manager=False)
        # return True, None



from autogen.agentchat.conversable_agent import ConversableAgent

DEFAULT_SYSTEM_MESSAGE = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply "TERMINATE" in the end when everything is done.
    """


def run_plugin(*args, **kwargs):
    """
    处理插件并运行插件的函数

    参数:
    *args: 可变参数，用于传递插件名称
    **kwargs: 关键字参数，用于传递给插件的参数
    """
    # 将args转换为列表以便使用pop方法
    args_list = list(args)

    # 从args列表中弹出最后一个元素作为插件名称
    args_list.pop()
    plugin_name = args_list.pop()
    print("plugin_name:", plugin_name)

    # 查询插件管理信息
    record = query_PluginMng(name=plugin_name)

    # 加载插件
    plugin = load_plugin_headless(None, record)

    # 运行插件，并传入剩余的参数
    result = plugin.run(*args_list, **kwargs)

    return result


def run_function(*args, **kwargs):
    """
    处理插件并运行插件的函数

    参数:
    *args: 可变参数，用于传递插件名称
    **kwargs: 关键字参数，用于传递给插件的参数
    """
    # 将args转换为列表以便使用pop方法
    args_list = list(args)

    # 从args列表中弹出最后一个元素作为插件名称
    args_list.pop()
    plugin_name = args_list.pop()
    print("plugin_name:", plugin_name)

    # 查询插件管理信息
    record = query_PluginMng(name=plugin_name)

    # 加载插件
    plugin = load_plugin_headless(None, record)

    # 运行插件，并传入剩余的参数
    result = plugin.run(*args_list, **kwargs)

    return result


class Agent(ConversableAgent):
    # class Agent:
    """在单独的线程中执行连接操作"""
    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self,
                 agent_cfg,
                 *,
                 chat_in_group: bool = False,
                 name: str = "",
                 system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
                 llm_config: Optional[Union[Dict, Literal[False]]] = None,
                 is_termination_msg: Optional[Callable[[Dict], bool]] = None,
                 max_consecutive_auto_reply: Optional[int] = None,
                 human_input_mode: Optional[str] = "ALWAYS",#NEVER,ALWAYS
                 description: Optional[str] = None,
                 **kwargs,
                 ):
        self._name = agent_cfg.name if agent_cfg is not None else name
        self.chat_in_group = chat_in_group
        self.agent_cfg = agent_cfg
        self.logger = None
        self.plugin_list = []
        self.default_llm = ""
        self.default_role = ""
        self.llm_dict = {}
        self.human_input_mode = human_input_mode

        self.llm_connector_name = ""
        self.llm_model_type = ""
        self.llm_connector_plugin = None
        self.llm_config = None

        self.system_role_id = -1
        self.system_role_prompt = ""

        self.km_path = ""
        self.speaker = None
        self.embedding_model_name = ""
        self.task_list = {}
        self.browser_page = None
        self.status = ""
        self.human_reply = ""
        self.mode = AgentMode.ChatOnly
        self.model_select_type = 'auto'
        self.reply_no_thinking_flag = False
        self.answer_no_thinking = ""
        self.is_running_workflow = False
        self.chat_mode = 'chat'
        self.history_mode = 'all'
        self.current_prompt = ""
        self.attachment_doc_content = ""
        self.attachment_content_list = []
        self.attachment_image_list = []
        self.retrieve_doc_list = []
        self.retrieve_doc_content = ""
        self.task_id = ""
        self.plugin_tool_record_selected_list = None
        self.process = None
        self.sub_process_flag = False

        if agent_cfg is not None:
            self.default_llm = agent_cfg.defaultmodel
            self.last_llm = agent_cfg.lastmodel
            use_last_model = agent_cfg.uselastmodel
            if use_last_model:
                llm = self.last_llm
            else:
                llm = self.default_llm

            self.give_it_llm(llm)  # 设置缺省模型

            self.default_role = agent_cfg.defaultrole
            self.last_role = agent_cfg.lastrole
            use_last_role = agent_cfg.uselastrole
            if use_last_role:
                role_id = self.last_role
            else:
                role_id = self.default_role

            self.give_it_role(role_id)  # 设置缺省模型

            self.set_plugin_list()

        if chat_in_group:
            if agent_cfg is not None:
                system_message = self.agent_cfg.prompt
                description = self.agent_cfg.specialization

            agent_name = self._name
            human_input_mode = self.human_input_mode
            # human_input_mode = "NEVER"
            # human_input_mode = "TERMINATE"
            llm_config = {
                "cache_seed": None,
                "temperature": 0,
                "config_list": [{"model": "gpt-4o-mini", "stream": True, "api_key": "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"}],
                "timeout": 120,
            }

            if self.agent_cfg:
                llm_full_name = self.agent_cfg.defaultmodel
                llm_connector_name = llm_full_name.split(":")[0]
                llm_model_type = llm_full_name.split(":")[1]
                llm_connector_plugin = global_plugin_list[llm_connector_name]
                llm_config = self.format_llm_config(llm_connector_plugin, llm_model_type)
            self.llm_config = llm_config



            super().__init__(
                agent_name,
                system_message,
                is_termination_msg,
                max_consecutive_auto_reply,
                human_input_mode,
                llm_config=llm_config,
                description=description,
                **kwargs,
            )

    def set_plugin_list(self):
        agent_cfg = self.agent_cfg
        if agent_cfg.plugins != "":
            self.plugin_list = agent_cfg.plugins.split(",")

    def set_mode(self, mode=AgentMode.ChatOnly):
        self.mode = mode

    def re_init(self):
        self.__init__(self.agent_cfg)

    def reload_agent_cfg(self):
        self.agent_cfg = query_AgentCfg(id=self.agent_cfg.id)

    def give_it_llm(self, llm_full_name):
        self.llm_connector_name = llm_full_name.split(":")[0]
        self.llm_model_type = llm_full_name.split(":")[1]
        self.llm_connector_plugin = global_plugin_list[self.llm_connector_name]

    def give_it_role(self, role_id, system_role_prompt=""):
        self.system_role_id = role_id
        if system_role_prompt:
            self.system_role_prompt = system_role_prompt
        else:
            self.system_role_prompt = get_prompt_by_id(role_id)

    def give_it_plugin_tool(self, plugin_tool_record_selected_list):
        self.plugin_tool_record_selected_list = plugin_tool_record_selected_list

    def give_it_km(self, km_path, embedding_model_name):
        self.km_path = km_path
        self.embedding_model_name = embedding_model_name

    def give_it_logger(self, logger):
        self.logger = logger

    def give_it_attachment_content_list(self, attachment_content_list):
        attachment_doc_content, attachment_image_list, _ = get_content_from_attachment_content_list(attachment_content_list)  # retrieve_doc_content这里还没有值
        self.attachment_content_list = attachment_content_list
        self.attachment_doc_content = attachment_doc_content
        self.attachment_image_list = attachment_image_list

    def remove_all_attachment(self):
        self.attachment_content_list = []
        self.attachment_doc_content = ""
        self.attachment_image_list = []
        self.retrieve_doc_list = []
        self.retrieve_doc_content = ""

    def give_it_speaker(self, speaker):
        self.speaker = speaker

    def give_it_answer_no_thinking(self, answer):
        self.reply_no_thinking_flag = True
        self.answer_no_thinking = answer

    def get_and_reset_answer_no_thinking(self):
        self.reply_no_thinking_flag = False
        answer = self.answer_no_thinking
        return answer

    def ask_it(self, question, messages, browser_page, task_id):
        global global_browser_page

        self.browser_page = browser_page
        self.task_id = task_id
        global_browser_page = browser_page
        # self.give_it_speaker(browser_page)
        # self.speaker.load(self.browser_page)
        if self.reply_no_thinking_flag:
            answer = self.get_and_reset_answer_no_thinking()
            speaker = self.speaker
            if speaker:
                self.speaker.speak(answer, sep="", end="")
                print("send:i will run it")
                time.sleep(1)
                self.speaker.commit_and_refresh()
                print("send:refresh")
            return answer

        retrieve_doc_content = ""
        if self.km_path != "":
            vector_path = self.km_path
            messages = messages
            persist_directory = vector_path
            embedding_model_name = self.embedding_model_name
            docs = getvectorkm_String(question, persist_directory, embedding_model_name)
            self.retrieve_doc_list = docs
            print(docs)
            print(docs[0][0].page_content)
            retrieve_doc_content = docs[0][0].page_content
            self.retrieve_doc_content = retrieve_doc_content

            docs_dict = [
                (
                    {
                        "page_content": doc[0].page_content,
                        "metadata": doc[0].metadata
                    },
                    doc[1]
                )
                for doc in docs
            ]

            self.attachment_content_list.append(("km", retrieve_doc_content, docs_dict))
        if retrieve_doc_content != "":
            messages[-1]["content"] = f'请根据后面提供的背景内容回答问题，回答只能限制在背景内容的范围内，问题是：{question};供参考的背景内容是：{retrieve_doc_content}'

        attachment_doc_content = self.attachment_doc_content

        if attachment_doc_content != "":
            messages[-1]["content"] = f'{messages[-1]["content"]};为你提供相关附件内容作为参考，具体内容是：{attachment_doc_content}'

        if self.attachment_image_list:
            # 创建新的列表以包含文本和图像内容
            new_attachment_list = []

            # 添加 message[-1]["content"] 到新列表
            new_attachment_list.append({
                "type": "text",
                "text": messages[-1]["content"],
            })

            # 将图像列表的内容添加到新列表中
            new_attachment_list.extend(self.attachment_image_list)

            messages[-1]["content"] = new_attachment_list

        # 处理插件

        #先处理工具的选择
        if question.startswith("@:"):
            type_str,question=self.think_and_pick_a_tool_to_solve_problem(question)
            print("type_str:",type_str)
            print("question:",question)
            if type_str == "skill":
                answer = f"Agent will run Computer Use,{question}"
                return answer



        if question.startswith("@"):
            # the tool
            all_plugin_tool_record_list = query_PluginMng_All_Tool()
            for record in all_plugin_tool_record_list:
                if "previous_to_ask_b" in record.plugin_event:
                    index_event = record.plugin_event.split(",").index("previous_to_ask_b")
                    instruction_list = []
                    instruction = record.instruction
                    instructed_flag = False
                    run_plugin_flag = False
                    if instruction:
                        instruction_list = instruction.split(",")

                    for inst in instruction_list:
                        if question.startswith(f"@{inst}:"):
                            instructed_flag = True
                            question = question.lstrip(f"@{inst}:")


                    if instructed_flag:
                        run_plugin_flag = True

                    if run_plugin_flag:
                        plugin = load_plugin_headless(self, record)
                        result = plugin.run(question, messages, browser_page, task_id, self.speaker)
                        how_to_handle_executed_result = record.plugin_executed.split(",")[index_event]
                        if how_to_handle_executed_result == "get_output_as_final_result":
                            answer = result[0]
                            return answer
                        else:
                            question = result[0]
                            messages = [{"content": result[1], "role": "user"}]

            # the function
            records = query_function_mng_all(function_type="1")
            for record in records:
                instruction_list = []
                instruction = record.instruction
                instructed_flag = False
                run_plugin_flag = False
                if instruction:
                    instruction_list = instruction.split(",")

                for inst in instruction_list:
                    if question.startswith(f"@{inst}:"):
                        instructed_flag = True
                        question = question.lstrip(f"@{inst}:")
                        print("cjrok111instfun")

                if instructed_flag:
                    run_plugin_flag = True

                if run_plugin_flag:
                    question = "Just run the function,no param." if question == "" else question
                    result = self.run_function(record, question, messages)
                    print("function result",result)
                    question = result[0]
                    answer = result[1]
                    messages = [{"content": result[1], "role": "user"}]
                    # print("answer:",answer)
                    # return answer

            # the workflow
            records = query_workflow_mng_all(is_delete=0)
            for record in records:
                workflow_id = ""
                instruct_str = ""
                instruction_list = []
                instruction = record.instruction
                instructed_flag = False
                run_plugin_flag = False
                if instruction:
                    instruction_list = instruction.split(",")

                for inst in instruction_list:
                    if question.startswith(f"@{inst}:"):
                        instructed_flag = True
                        question = question.lstrip(f"@{inst}:")
                        instruct_str = inst
                        workflow_id = record.workflow_id
                        print("cjrok111instwf")

                if instructed_flag:
                    run_plugin_flag = True

                if run_plugin_flag:
                    # result = self.run_function(record,question,messages)
                    result = self.run_workflow(workflow_id, question)

                    answer = result[0]
                    return answer

            # the mcp
            records = query_mcp_mng_all(is_delete=0)
            for record in records:
                mcp_id = ""
                instruct_str = ""
                instruction_list = []
                instruction = record.instruction
                instructed_flag = False
                run_plugin_flag = False
                if instruction:
                    instruction_list = instruction.split(",")

                for inst in instruction_list:
                    if question.startswith(f"@{inst}:"):
                        instructed_flag = True
                        question = question.lstrip(f"@{inst}:")
                        instruct_str = inst

                if instructed_flag:
                    run_plugin_flag = True

                if run_plugin_flag:
                    # mcp_server_name = "duckduckgo"
                    # tool_name = "search"
                    # arguments = '''{"query":"中美贸易谈判","max_results":10}'''
                    record_id_int = record.id
                    mcp_name = record.name
                    # mcp_server_name = "高德地图sse"
                    # tool_name = "maps_geo"
                    # arguments = '''{"address":"邯郸路200号","city":"上海"}'''

                    # mcp_server_name = "localserver"
                    # tool_name = "get_alerts"
                    # arguments = '''{"state":"CA"}'''
                    #
                    #
                    # mcp_server_name = "streamablestest"
                    # tool_name = "run-code"
                    # arguments = '''{"code":"print('cjrok'+',yes he is great')","languageId":"python"}'''

                    # result = self.run_mcp(mcp_server_name, tool_name, arguments)
                    result = self.think_and_run_mcp(record_id_int, mcp_name, question)
                    print("get run_mcp result:", result)

                    question = result[0]
                    answer = result[1]
                    messages = [{"content": result[1], "role": "user"}]

                    # answer = result
                    # return answer

        else:
            if self.plugin_tool_record_selected_list:
                plugin_tool_record_selected_list = self.plugin_tool_record_selected_list
            else:
                plugin_tool_record_selected_list = []
            for record in plugin_tool_record_selected_list:
                if "previous_to_ask_b" in record.plugin_event:
                    index_event = record.plugin_event.split(",").index("previous_to_ask_b")
                    plugin = load_plugin_headless(self, record)
                    result = plugin.run(question, messages, browser_page, task_id, self.speaker)
                    how_to_handle_executed_result = record.plugin_executed.split(",")[index_event]
                    if how_to_handle_executed_result == "get_output_as_final_result":
                        answer = result[0]
                        return answer
                    else:
                        question = result[0]
                        messages = [{"content": result[1], "role": "user"}]

        if question.startswith("_System_NO_Used_给我画"):
            answer = self.generate_image(question)

        elif "workflow_id:" in question:
            # workflow_id = question.replace("@@workflow_id","")

            workflow_id = ""

            # 输入字符串
            input_string = question

            # 使用正则表达式匹配'sktll_id:'后面的所有字符串
            match = re.search(r'workflow_id:(.*)', input_string)

            # 检查是否找到匹配项
            if match:
                # 提取匹配的字符串并去除前后的空格
                workflow_id = match.group(1).strip()

            answer = self.run_workflow(workflow_id, "")

        else:
            if self.chat_mode == "task":
                # answer = self.chat_with_tool(message)
                # answer = self.autogen_run_code(message)
                # answer = self.run_task(message)
                answer = self.address_task(messages)

            else:
                answer = self.chat_only(messages)
                # if self.logger:
                #     if messages:
                #         self.logger.debug("agent log:"+list(messages[0].values())[0])

        # else:
        #     speaker=self.speaker
        #
        #     if browser_page != None:
        #         self.speaker.runJavaScript('updatemaincontent()')
        #
        #     print("\n最终输出:")
        #     print(''.join(total_output))
        #     answer = ''.join(total_output)

        print("message:::::", messages)
        print("autogen will show:")
        # self.autogen_run()#等待人类回复
        # self.autogen_runv2()
        # self.autogen_run1()
        return answer

    def run_tool(self,tool_id,tool_name, question, messages, browser_page, task_id):
        global global_browser_page

        self.browser_page = browser_page
        self.task_id = task_id
        global_browser_page = browser_page
        # self.give_it_speaker(browser_page)
        # self.speaker.load(self.browser_page)
        if self.reply_no_thinking_flag:
            answer = self.get_and_reset_answer_no_thinking()
            speaker = self.speaker
            if speaker:
                self.speaker.speak(answer, sep="", end="")
                print("send:i will run it")
                time.sleep(1)
                self.speaker.commit_and_refresh()
                print("send:refresh")
            return answer

        retrieve_doc_content = ""
        if self.km_path != "":
            vector_path = self.km_path
            messages = messages
            persist_directory = vector_path
            embedding_model_name = self.embedding_model_name
            docs = getvectorkm_String(question, persist_directory, embedding_model_name)
            self.retrieve_doc_list = docs
            print(docs)
            print(docs[0][0].page_content)
            retrieve_doc_content = docs[0][0].page_content
            self.retrieve_doc_content = retrieve_doc_content

            docs_dict = [
                (
                    {
                        "page_content": doc[0].page_content,
                        "metadata": doc[0].metadata
                    },
                    doc[1]
                )
                for doc in docs
            ]

            self.attachment_content_list.append(("km", retrieve_doc_content, docs_dict))
        if retrieve_doc_content != "":
            messages[-1]["content"] = f'请根据后面提供的背景内容回答问题，回答只能限制在背景内容的范围内，问题是：{question};供参考的背景内容是：{retrieve_doc_content}'

        attachment_doc_content = self.attachment_doc_content

        if attachment_doc_content != "":
            messages[-1]["content"] = f'{messages[-1]["content"]};为你提供相关附件内容作为参考，具体内容是：{attachment_doc_content}'

        if self.attachment_image_list:
            # 创建新的列表以包含文本和图像内容
            new_attachment_list = []

            # 添加 message[-1]["content"] 到新列表
            new_attachment_list.append({
                "type": "text",
                "text": messages[-1]["content"],
            })

            # 将图像列表的内容添加到新列表中
            new_attachment_list.extend(self.attachment_image_list)

            messages[-1]["content"] = new_attachment_list

        # 处理插件

        if question:
            record_id_int = int(tool_id[1:])
            # the tool
            if tool_id.startswith("9"):
                all_plugin_tool_record_list = query_PluginMng_All_Tool()
                for record in all_plugin_tool_record_list:
                        run_plugin_flag = False
                        if record.name == tool_name:
                            run_plugin_flag = True

                        if run_plugin_flag:
                            plugin = load_plugin_headless(self, record)
                            return_value = plugin.run(question, messages, browser_page, task_id, self.speaker)
                            result = return_value[1]


            # the function
            elif tool_id.startswith("8"):
                record = query_function_mng(id = record_id_int)
                question = "Just run the function,no param." if question == "" else question
                result = self.think_and_run_function(record, question, messages)


            # the skill
            elif tool_id.startswith("7"):
                pass

            # the mcp
            elif tool_id.startswith("6"):
                mcp_server_name = tool_name
                tool_name_str = "handle_content"
                question = "content:" + question
                arguments_dict = {"content": question}
                arguments = json.dumps(arguments_dict, ensure_ascii=False)  # 将字典转换为JSON字符串

                result = self.run_mcp(mcp_server_name, tool_name_str, arguments)
                result = result.strip()
                print("get run_mcp result:", result)
                result_dict = json.loads(result)
                result = result_dict.get("result","")

                # result = self.run_mcp(mcp_name, function_name, parameters_str)
                # result[2] = self.think_and_run_mcp(record_id_int, tool_name, question)#return (question,question+mcp_result,mcp_result)


        return result


    def assign_task(self, task_id, task_content):
        self.task_list[task_id] = task_content
        print(self.name, self.task_list)

    def generate_image(self, prompt, model="dall-e-3", n=1, size="1024x1024"):
        # 更新模型和参数的说明
        """
        The size of the generated images. Must be one of 1024x1024, 1792x1024, or 1024x1792 for dall-e-3 models.
        The number of images to generate. Must be 1 for dall-e-3.
        """

        url = "https://api.chatanywhere.tech/v1/images/generations"
        api_key = "sk-SVCuk9EAqrgUEvvh31PKxVIr1fZhwt5boDB2Hexw8vs2Bl26"  # 更新为您提供的 Bearer Token

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=data)
        print("dallurl:", url)

        # 检查响应状态
        if response.status_code != 200:
            print("Error:", response.text)
            return []

        # 提取 URL 列表
        urls = [datum['url'] for datum in response.json().get('data', [])]
        print(urls)

        for i in range(len(urls)):
            image_name = generate_random_id() + ".png"

            task_id = self.task_id
            directory_path = os.path.join('resource', 'attachment', 'chat', task_id)
            os.makedirs(directory_path, exist_ok=True)

            save_path = os.path.join('resource', 'attachment', 'chat', task_id, image_name)

            save_path = os.path.join('resource', 'attachment', 'chat', image_name)
            download_image(urls[i], save_path)
            save_path = os.path.abspath(save_path).replace("\\", "/")
            urls[i] = save_path  # 直接替换 urls 列表中对应位置的值

        img_element = ''.join(f"""<br><a href="#" onclick="open_attachment('{url}');return false;" style="color:blue"><img src="file:///{url}" alt="{url}" style="width:300px;height:auto;" /></a><br>""" for url in urls)
        print(img_element)

        # 添加附件元素到页面中
        self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += `' + img_element + '`')
        self.speaker.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

        return img_element  # 返回生成的图像 URL 列表

    def generate_imagebakok2(self, prompt, model="dall-e-3", n=1, size="1024x1024"):
        # 更新模型和参数的说明
        """
        The size of the generated images. Must be one of 1024x1024, 1792x1024, or 1024x1792 for dall-e-3 models.
        The number of images to generate. Must be 1 for dall-e-3.
        """

        url = "https://dalle.feiyuyu.net/v1/images/generations"
        api_key = "ae51ca53-29b1"  # 更新为您提供的 Bearer Token

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        data = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=data)
        print("dallurl:", url)

        # 检查响应状态
        if response.status_code != 200:
            print("Error:", response.text)
            return []

        # 提取 URL 列表
        urls = [datum['url'] for datum in response.json().get('data', [])]
        print(urls)

        for i in range(len(urls)):
            image_name = generate_random_id() + ".png"

            task_id = self.task_id
            directory_path = os.path.join('resource', 'attachment', 'chat', task_id)
            os.makedirs(directory_path, exist_ok=True)

            save_path = os.path.join('resource', 'attachment', 'chat', task_id, image_name)

            save_path = os.path.join('resource', 'attachment', 'chat', image_name)
            download_image(urls[i], save_path)
            save_path = os.path.abspath(save_path).replace("\\", "/")
            urls[i] = save_path  # 直接替换 urls 列表中对应位置的值

        img_element = ''.join(f"""<br><a href="#" onclick="open_attachment('{url}');return false;" style="color:blue"><img src="file:///{url}" alt="{url}" style="width:300px;height:auto;" /></a><br>""" for url in urls)
        print(img_element)

        # 添加附件元素到页面中
        self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += `' + img_element + '`')
        self.speaker.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

        return img_element  # 返回生成的图像 URL 列表

    def generate_imagebakok(self, prompt, model="dall-e-2", n=2, size="512x512"):
        # ***dall-e-3的n必须是1，size只能是：'1024x1024', '1024x1792', '1792x1024'
        """
        The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024 for dall-e-2. Must be one of 1024x1024, 1792x1024, or 1024x1792 for dall-e-3 models.
        The number of images to generate. Must be between 1 and 10. For dall-e-3, only n=1 is supported.

        """

        openai.api_key = "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"
        response = openai.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
            response_format="url",
        )

        # 提取 URL 列表
        # urls = [data['url'] for data in response['data']]
        urls = [datum.url for datum in response.data]

        for i in range(len(urls)):
            image_name = generate_random_id() + ".png"

            task_id = self.task_id
            directory_path = os.path.join('resource', 'attachment', 'chat', task_id)
            os.makedirs(directory_path, exist_ok=True)

            save_path = os.path.join('resource', 'attachment', 'chat', task_id, image_name)
            download_image(urls[i], save_path)
            save_path = os.path.abspath(save_path).replace("\\", "/")
            # urls[i] ="file:///"+ save_path  # 直接替换 urls 列表中对应位置的值
            urls[i] = save_path  # 直接替换 urls 列表中对应位置的值

        # message = f"""<strong><em><span style='color: darkred;font-size:14px;'>{("用户")}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong>"""
        # self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '<br>"')
        # message = f"""{prompt}"""
        # self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '<br><br>"')
        # modelname = model
        # message = f"""<strong><em><span style='color: darkblue; font-size:14px;'>{(modelname)}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong><br>"""
        # self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '"')

        # 创建新的附件元素
        # attachment_element = f"""<br><br><a href="#" onclick="open_attachment('{new_file_path}');return false;" style="color:blue"><img src="file:///{image_file_path}" alt="{file_name}" style="width:300px;height:auto;" /></a><br><br>"""

        img_element = ''.join(f"""<br><a href="#" onclick="open_attachment('{url}');return false;" style="color:blue"><img src="file:///{url}" alt="{url}" style="width:300px;height:auto;" /></a><br>""" for url in urls)
        print(img_element)
        # 添加附件元素到页面中
        self.speaker.runJavaScript('document.getElementById("allcontent").innerHTML += `' + img_element + '`')
        self.speaker.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

        return img_element  # 返回生成的图像 URL 列表

    def get_human_feedback(self):
        status = self.status

        while True:
            human_reply = self.human_reply
            if human_reply != "":
                break
        self.human_reply = ""
        return human_reply

    def print_message_before_send(self, sender, message, recipient, silent):
        browser_page = self.browser_page
        # 参数都在相应的hooklist处理事件中传进来
        print("cjrok---print_message_before_send---")
        # hm=input("你要发送什么？")
        tmp = "你要发送什么？"
        self.speaker.runJavaScript('tchunks=`' + tmp + '`')
        self.speaker.runJavaScript('show_response_msg(tchunks)')
        self.speaker.runJavaScript('updatemaincontent()')
        self.human_reply = ""
        hm = self.get_human_feedback()
        print("我收到人类输入：", hm[:])
        message = hm[:]
        print("我要发送：", message)

        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + message + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return message

    def print_last_received_message(self, content: Union[str, List[dict]]):
        # 参数都在相应的hooklist处理事件中传进来
        print("cjrok---print_last_received_message---")
        hm = input("你最后收到什么？")
        print("我最后收到：", content)

        browser_page = self.browser_page
        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + content + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return content

    def print_all_messages_before_reply(self, content: Union[str, List[dict]]):
        # 参数都在相应的hooklist处理事件中传进来
        print("cjrok---print_all_messages_before_reply---")
        hm = input("收到的全部信息是什么？")
        print("我全部收到：", content)
        browser_page = self.browser_page
        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + content[0]["content"] + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return content

    def print_message_before_sendassistant(self, sender, message, recipient, silent):
        # 参数都在相应的hooklist处理事件中传进来
        print("assistantcjrok---print_message_before_send---")
        hm = input("你要发送什么？")
        print("我assistant要发送：", message)
        browser_page = self.browser_page
        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + message + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return message

    def print_last_received_messageassistant(self, content: Union[str, List[dict]]):
        # 参数都在相应的hooklist处理事件中传进来
        print("assistantcjrok---print_last_received_message---")
        hm = input("你最后收到什么？")
        print("我assistant最后收到：", content)
        browser_page = self.browser_page
        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + content + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return content

    def print_all_messages_before_replyassistant(self, content: Union[str, List[dict]]):
        # 参数都在相应的hooklist处理事件中传进来
        print("assistantcjrok---print_all_messages_before_reply---")
        hm = input("收到的全部信息是什么？")
        print("我assistant全部收到：", content)
        browser_page = self.browser_page
        if browser_page != None:
            self.speaker.runJavaScript('tchunks=`' + content[0]["content"] + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')

        return content

    def autogen_run(self):
        # Load LLM inference endpoints from an env variable or a file
        # See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
        # and OAI_CONFIG_LIST_sample.
        # For example, if you have created a OAI_CONFIG_LIST file in the current working directory, that file will be used.
        # config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
        config_list = {"model": "gpt-3.5-turbo", "api_key": "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", "seed": 42, "temperature": 0, "stream": True}

        # Create the agent that uses the LLM.
        assistant = ConversableAgent("agent", llm_config=config_list)

        # Create the agent that represents the user in the conversation.
        user_proxy = UserProxyAgent("user", code_execution_config=False)

        assistant.register_hook(hookable_method="process_message_before_send", hook=self.print_message_before_sendassistant)
        assistant.register_hook(hookable_method="process_last_received_message", hook=self.print_last_received_messageassistant)
        assistant.register_hook(hookable_method="process_all_messages_before_reply", hook=self.print_all_messages_before_replyassistant)

        user_proxy.register_hook(hookable_method="process_message_before_send", hook=self.print_message_before_send)
        user_proxy.register_hook(hookable_method="process_last_received_message", hook=self.print_last_received_message)
        user_proxy.register_hook(hookable_method="process_all_messages_before_reply", hook=self.print_all_messages_before_reply)

        # Let the assistant start the conversation.  It will end when the user types exit.
        user_proxy.initiate_chat(assistant, message="请写一首关于秋天的1000字的诗")
        # assistant.initiate_chat(user_proxy, message="你是谁?")

    def format_llm_config(self, llm=None, model_type=""):
        if not llm:
            llm = self.llm_connector_plugin
        if not model_type:
            model_type = self.llm_model_type
        config = llm.get_config()
        connection_mode = llm.connection_mode

        if config.get("custom_params", False) == False:
            llm_config = {
                "model": model_type if model_type else config.get("model", ""),
                "api_key": config.get("api_key", ""),
                "cache_seed": None,
                "seed": None,  # 42
                "temperature": config.get("temperature", 0),
                "stream": config.get("stream", False)
            }
        else:
            json_string = config.get("parameters", "")
            custom_config = json.loads(json_string)
            llm_config = {
                "model": model_type if model_type else custom_config.get("model", ""),
                "api_key": config.get("api_key", ""),
                "cache_seed": None,
                "seed": None,  # 42
                "temperature": custom_config.get("temperature", 0),
                "stream": custom_config.get("stream", False)
            }

        if model_type == "gpt-4o-mini-search-preview" or model_type == "gpt-4o-search-preview":
            llm_config.pop("seed", None)
            llm_config.pop("temperature", None)

        if connection_mode == "OpenAI-compatible":
            base_url = config.get("url", "").replace('/chat/completions', '')
            llm_config["base_url"] = base_url
            llm_config["model_client_cls"] = "OpenAICompatibleLLMClient"

        elif connection_mode == "OpenAI-customize":
            base_url = config.get("url", "").replace('/chat/completions', '')
            llm_config["base_url"] = base_url
            llm_config["model_client_cls"] = "OpenAICustomizeLLMClient"

        elif connection_mode == "OpenAI-customize-v2":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "OpenAICustomizeV2LLMClient"

        elif connection_mode == "SparkAI":
            llm_config = llm.get_config()
            # llm_config["model_client"] = llm.get_model()
            llm_config.pop("plugin_name", None)
            llm_config.pop("custom_params", None)
            llm_config.pop("description", None)
            llm_config.pop("parameters", None)
            llm_config["model_client_cls"] = "SparkAI"

        elif connection_mode == "Anthropic":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "AnthropicClient"

        elif connection_mode == "Customize":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "CustomizeClient"

        elif connection_mode == "groq":
            llm_config = llm.get_config()
            llm_config["api_type"] = "groq"
            # llm_config["model_client_cls"] = "GroqClient"

        return llm_config

    def autogen_run0(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)

        if self.llm_connector_plugin.connection_mode == "OpenAI":
            agent = ConversableAgent(
                "chatbot",
                llm_config=llm_config,
                code_execution_config=False,  # Turn off code execution, by default it is off.
                function_map=None,  # No registered functions, by default it is None.
                human_input_mode="NEVER",  # Never ask for human input.

            )

        elif self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent = ConversableAgent(
                "chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
                code_execution_config=False,  # Turn off code execution, by default it is off.
                function_map=None,  # No registered functions, by default it is None.
                human_input_mode="NEVER",  # Never ask for human input.

            )

            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent = ConversableAgent(
                "chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
                code_execution_config=False,  # Turn off code execution, by default it is off.
                function_map=None,  # No registered functions, by default it is None.
                human_input_mode="NEVER",  # Never ask for human input.

            )

            agent.register_model_client(model_client_cls=SparkAI)

        else:
            agent = ConversableAgent(
                "chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
                code_execution_config=False,  # Turn off code execution, by default it is off.
                function_map=None,  # No registered functions, by default it is None.
                human_input_mode="NEVER",  # Never ask for human input.

            )

            agent.register_model_client(model_client_cls=CustomizeClient)

        print("i ask question:", messages)
        # reply = agent.generate_reply(messages=[{"content": "介绍一下北京", "role": "user"}])
        # reply = agent.generate_reply(messages=[{"content": "我请你介绍一下潮阳", "role": "user"}])
        reply = agent.generate_reply(messages=messages)

        print("cjrok ....the reply:", reply)
        print(reply)

        if llm_config["stream"] == False:
            browser_page = self.browser_page
            self.speaker.runJavaScript('tchunks=`' + reply + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')
            # speaker.speak(reply, sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.commit_and_refresh()

        else:
            speaker.speak("", sep="", end="")
            speaker.speak("", sep="", end="")
            speaker.commit_and_refresh()
        return reply

    def run_task(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)
        message = messages[-1]["content"]

        user_proxy = UserProxyAgent(
            "user_proxy",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            max_consecutive_auto_reply=10,

        )
        system_message = "You are a helpful AI assistant. "
        "You can help with simple calculations. "
        "You are a helpful AI assistant.\nSolve tasks using your coding and language skills.\nIn the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.\n    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.\n    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.\nSolve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.\nWhen using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can\'t modify your code. So do not suggest incomplete code which requires users to modify. Don\'t use a code block if it\'s not intended to be executed by the user.\nIf you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don\'t include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use \'print\' function for the output when relevant. Check the execution result returned by the user.\nIf the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can\'t be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.\nWhen you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible."
        "Return 'TERMINATE' when the task is done."

        if self.llm_connector_plugin.connection_mode == "OpenAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message=system_message,
                llm_config=llm_config,
            )

        elif self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent = AssistantAgent(
                name="chatbot",
                system_message=system_message,
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message=system_message,
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=SparkAI)

        else:
            agent = AssistantAgent(
                name="chatbot",
                system_message=system_message,
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=CustomizeClient)

        print("i ask question:", messages)

        func_name = "calculator_tool_for_call"
        fun = globals()[func_name]
        description = "A simple calculator"

        agent.register_for_llm(name=func_name, description=description)(fun)
        user_proxy.register_for_execution(name=func_name)(fun)

        func_name = "get_weather_tool_for_call"
        fun = globals()[func_name]
        description = "get the weather of a city"

        agent.register_for_llm(name=func_name, description=description)(fun)
        user_proxy.register_for_execution(name=func_name)(fun)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        print(agent.llm_config["tools"])

        try:
            user_proxy.initiate_chat(
                agent,
                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                # message=f"""{messages[-1]["content"]}""",
                # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                message=message,
                clear_history=True
            )
        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = "任务执行完毕！"
        self.speaker.speak(reply, sep="", end="")
        self.speaker.commit_and_refresh()
        return reply

    def sort_nodes_by_connections(self, workflow_cfg):
        workflow = json.loads(workflow_cfg)
        # 提取节点和连接线
        nodes = {node['id']: node for node in workflow['nodes']}
        lines = workflow['lines']

        # 查找开始节点和结束节点
        start_node = next(node for node in nodes.values() if node['type'] == 'start')
        end_node = next(node for node in nodes.values() if node['type'] == 'end')

        # 创建连接字典
        connections = {node['id']: [] for node in nodes.values()}
        for line in lines:
            connections[line['connector1Id']].append(line['connector2Id'])

        # 按顺序遍历节点
        sorted_nodes = []
        visited = set()
        current_node_id = start_node['id']

        # 使用 BFS 进行遍历
        def bfs(start_id):
            queue = [start_id]
            while queue:
                node_id = queue.pop(0)
                if node_id not in visited:
                    visited.add(node_id)
                    sorted_nodes.append(nodes[node_id])
                    if node_id in connections:
                        queue.extend(connections[node_id])

        bfs(current_node_id)

        # 将结束节点添加到最后
        if end_node['id'] not in visited:
            sorted_nodes.append(end_node)

        return sorted_nodes

    def get_next_nodes(self, workflow_cfg, node_id):
        """
        获取指定节点的所有后继节点。

        :param workflow: 包含节点和连接线的工作流数据。
        :param node_id: 指定节点的 ID。
        :return: 指定节点的所有后继节点列表。
        """
        # 提取所有节点和连接线
        workflow = json.loads(workflow_cfg)
        nodes = {node['id']: node for node in workflow['nodes']}
        lines = workflow['lines']

        # 创建连接字典
        connections = {node['id']: [] for node in nodes.values()}
        for line in lines:
            connections[line['connector1Id']].append(line['connector2Id'])

        # 获取后继节点
        return [nodes[next_id] for next_id in connections.get(node_id, [])]

    def run_workflowbak(self, workflow_id):
        print("loading workflow")
        workflow_cfg = ""
        workflow_node_list = []

        record = query_workflow_mng(workflow_id=workflow_id)
        if record:
            workflow_cfg = record.detail
            self.workflow_title = record.title
            self.workflow_description = record.description
            self.workflow_id = record.workflow_id
            self.instruction = record.instruction
        workflow_node_list = self.sort_nodes_by_connections(workflow_cfg)

        print("workflow_node_list:", workflow_node_list)
        note_start = workflow_node_list[0]
        note_end = workflow_node_list[-1]
        print("note_start:", note_start)

        print("note_start description:", note_start.get("description", ""))
        print("note_end:", note_end)
        print("llm node:", workflow_node_list[1])

        if workflow_node_list[1].get("type", "") == "llm":
            llm_str = workflow_node_list[1].get("description", "")
            llm = json.loads(llm_str)
            print("model:", llm.get("model", ""))

        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        # message = messages[-1]["content"]
        message = note_start.get("description", "")

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        agent_human = UserProxyAgent(
            "Human",
            human_input_mode="ALWAYS",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=10,

        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )

        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        agent_task_handler = AssistantAgent(
            name="Task_Handler",
            system_message=system_message_task_handler,
            llm_config=llm_config,
        )

        # print("i ask question:", messages)

        # func_name = "calculator_tool_for_call"
        # fun = globals()[func_name]
        # description = "A simple calculator"
        #
        # agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        # agent_human.register_for_execution(name=func_name)(fun)

        try:
            cur_node = note_start
            plugin_name = ""
            plugin_type = ""
            plugin_id = ""
            while cur_node:
                print("title:", cur_node["title"])
                if cur_node["type"] == "start":
                    print("workflow start")

                    # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                    if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                        agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    elif self.llm_connector_plugin.connection_mode == "SparkAI":
                        agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                        agent_task_handler.register_model_client(model_client_cls=SparkAI)
                    elif self.llm_connector_plugin.connection_mode != "OpenAI":
                        # 其他的自定义ai连接客户端
                        agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                    use_question = message
                    chat_result = agent_human.initiate_chat(
                        agent_task_plan_scheduler,
                        message=message,
                        # max_turns=1,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)

                elif cur_node["type"] == "llm":
                    pass

                elif cur_node["type"] == "code":
                    plugin_name = cur_node["plugin"]
                    plugin_type = plugin_name[:4]
                    plugin_id = plugin_name[4:0]

                    if plugin_type == "sbi_":
                        print("tool call cur_node.plugin", cur_node["plugin"])

                        func_name = cur_node["plugin"]
                        fun = globals()[func_name]
                        # description = cur_node["description"]
                        fun_record = query_function_mng(name=cur_node["plugin"])
                        description = fun_record.description

                        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
                        agent_human.register_for_execution(name=func_name)(fun)

                        # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                        if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                            agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        elif self.llm_connector_plugin.connection_mode == "SparkAI":
                            agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                            agent_task_handler.register_model_client(model_client_cls=SparkAI)
                        elif self.llm_connector_plugin.connection_mode != "OpenAI":
                            # 其他的自定义ai连接客户端
                            agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                        print(agent_tools_wizard.llm_config["tools"])

                        message = use_question + "\n" + chat_result.summary
                        message = message + "\n请对上述总结进行分析，列出哪些是你可以用函数调用进行处理的。\n然后调用相应的函数进行处理。\n最后总结一下哪些任务是你处理好的，哪些任务需要Task_Handler进行处理"
                        chat_result = agent_human.initiate_chat(
                            agent_tools_wizard,
                            # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                            # message=f"""{messages[-1]["content"]}""",
                            # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                            # max_turns=2,
                            message=message,
                            clear_history=True
                        )
                        print("chatresult:", chat_result)
                    elif plugin_type == "sdf_":
                        print("local function cur_node.plugin", cur_node["plugin"])

                        # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                        if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                            agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        elif self.llm_connector_plugin.connection_mode == "SparkAI":
                            agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                            agent_task_handler.register_model_client(model_client_cls=SparkAI)
                        elif self.llm_connector_plugin.connection_mode != "OpenAI":
                            # 其他的自定义ai连接客户端
                            agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                        # cur_system_message = cur_node["description"]
                        o_file = os.path.join(os.getcwd(), "pluginsmanager", "plugins_function", cur_node["plugin"] + ".py")
                        t_file = os.path.join(os.getcwd(), "coding", cur_node["plugin"] + ".py")
                        shutil.copy2(o_file, t_file)

                        cur_system_message = agent_task_handler.system_message
                        fun_record = query_function_mng(name=cur_node["plugin"])
                        cur_system_message = cur_system_message + fun_record.detail
                        print("cur_system_message:", cur_system_message)
                        agent_task_handler.update_system_message(cur_system_message)

                        message = "\n" + chat_result.summary

                        if chat_result.summary != 'No Function Found****':
                            print("non function go next V2")

                            agent_human = UserProxyAgent(
                                "Human",
                                human_input_mode="ALWAYS",
                                code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                                # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                                max_consecutive_auto_reply=10,

                            )

                            message = message + "\n继续完成没有完成的任务。"

                            chat_result = agent_human.initiate_chat(
                                agent_task_handler,
                                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                                # message=f"""{messages[-1]["content"]}""",
                                # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                                message=message,
                                clear_history=True
                            )
                            print("chatresult:", chat_result)
                    elif plugin_type == "plg_":
                        pass
                    elif plugin_type == "skl":
                        pass
                    else:
                        # 现写代码
                        pass

                elif cur_node["type"] == "internet":
                    pass

                elif cur_node["type"] == "km":
                    pass

                elif cur_node["type"] == "variable":
                    pass

                elif cur_node["type"] == "condition":
                    pass

                elif cur_node["type"] == "human":
                    pass

                elif cur_node["type"] == "end":
                    # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                    if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                        agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    elif self.llm_connector_plugin.connection_mode == "SparkAI":
                        agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                        agent_task_handler.register_model_client(model_client_cls=SparkAI)
                    elif self.llm_connector_plugin.connection_mode != "OpenAI":
                        # 其他的自定义ai连接客户端
                        agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                    print("workflow end")
                    return
                    break

                next_nodes = self.get_next_nodes(workflow_cfg, cur_node["id"])
                if not next_nodes:
                    return
                    break
                cur_node = next_nodes[0]


        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = "任务执行完毕！"
        self.speaker.speak(reply, sep="", end="")
        self.speaker.commit_and_refresh()
        return reply

    def run_workflow(self, workflow_id, instruct_str=""):
        print("loading workflow")
        self.is_running_workflow = True
        workflow_cfg = ""
        workflow_node_list = []
        if workflow_id:
            record = query_workflow_mng(workflow_id=workflow_id)
        else:
            record = query_workflow_mng(instruction=instruct_str)

        if record:
            workflow_cfg = record.detail
            self.workflow_title = record.title
            self.workflow_description = record.description
            self.workflow_id = record.workflow_id
            self.instruction = record.instruction
        workflow_node_list = self.sort_nodes_by_connections(workflow_cfg)

        print("workflow_node_list:", workflow_node_list)
        note_start = workflow_node_list[0]
        note_end = workflow_node_list[-1]
        print("note_start:", note_start)

        print("note_start description:", note_start.get("description", ""))
        print("note_end:", note_end)
        print("llm node:", workflow_node_list[1])

        if workflow_node_list[1].get("type", "") == "llm":
            llm_str = workflow_node_list[1].get("description", "")
            llm = json.loads(llm_str)
            print("model:", llm.get("model", ""))

        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        # message = messages[-1]["content"]
        task_desc = note_start.get("description", "")  # 原始任务
        message = task_desc

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        system_message_er_re = get_prompt_by_title("ER_RE")
        system_message_assistant_common = get_prompt_by_title("Assiatan_Common")
        agent_human = UserProxyAgent(
            "Human",
            human_input_mode="ALWAYS",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=10,

        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )

        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        agent_task_handler = AssistantAgent(
            name="Task_Handler",
            system_message=system_message_task_handler,
            llm_config=llm_config,
        )

        # print("i ask question:", messages)

        # func_name = "calculator_tool_for_call"
        # fun = globals()[func_name]
        # description = "A simple calculator"
        #
        # agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        # agent_human.register_for_execution(name=func_name)(fun)

        # self.speaker.speak("**🟢 ➡️ 📥  🔀  🛠️ 🔄 📤 ➡️ 🔴 开始执行工作流......**\n\n", sep="", end="")
        # self.speaker.speak("**🔴 ➡️  🔀 ➡️ 开始执行工作流......**\n\n", sep="", end="")

        try:
            cur_node = note_start
            plugin_name = ""
            plugin_type = ""
            plugin_id = ""
            web_service_result = ""
            question_to_retrieve_from_km = ""
            km_doc_content = ""
            re_er_content = ""
            re_er_result = ""
            condition_content = ""
            condition_result = ""
            ask_human_content = ""
            human_feed_back = ""
            task_handle_result = ""
            step_index = 0

            while cur_node:
                print("title:", cur_node["title"])
                step_index += 1
                self.speaker.speak(f'🔷步骤-{step_index}：{cur_node["title"]}\n\n', sep="", end="")
                if cur_node["type"] == "start":
                    print("workflow start")

                    # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                    if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                        agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    elif self.llm_connector_plugin.connection_mode == "SparkAI":
                        agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                        agent_task_handler.register_model_client(model_client_cls=SparkAI)
                    elif self.llm_connector_plugin.connection_mode != "OpenAI":
                        # 其他的自定义ai连接客户端
                        agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                        agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                    instructions_to_agent = message
                    chat_result = agent_human.initiate_chat(
                        agent_task_plan_scheduler,
                        message=message,
                        # max_turns=1,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)

                elif cur_node["type"] == "llm":
                    plugin_name = cur_node["plugin"]
                    llm_id, role_id = plugin_name.split(",", 1)
                    llm_plugin_record = query_PluginMng(plugin_id=llm_id)
                    llm_plugin_name = llm_plugin_record.name
                    llm_connector = global_plugin_list[llm_plugin_name]
                    prompt_string = get_prompt_by_id(int(role_id))

                    cur_llm_config = self.format_llm_config(llm_connector, "gpt-4o-mini")

                    print("cur_llm_config", cur_llm_config)

                    if llm_connector.connection_mode != "OpenAI":
                        cur_llm_config = {"cache_seed": None, "config_list": [cur_llm_config]}  # 注意格式和openai不同

                    agent_task_handler = AssistantAgent(
                        name="Task_Handler",
                        system_message=prompt_string,
                        llm_config=cur_llm_config,
                    )

                    desc = cur_node["description"]

                    message = "我正在处理流程，以下是处理的情况：" + task_handle_result + ";请根据我如下描述进行回复：" + desc
                    chat_result = agent_human.initiate_chat(
                        agent_task_handler,
                        # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                        # message=f"""{messages[-1]["content"]}""",
                        # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                        # max_turns=2,
                        message=message,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)
                    task_handle_result = task_handle_result + "大模型的回复：" + chat_result.summary

                elif cur_node["type"] == "code":
                    plugin_name = cur_node["plugin"]
                    plugin_type = plugin_name[:4]
                    plugin_id = plugin_name[4:]

                    if plugin_type == "fun_":
                        print("local function cur_node.plugin", cur_node["plugin"])

                        # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                        if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                            agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                            agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                        elif self.llm_connector_plugin.connection_mode == "SparkAI":
                            agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                            agent_task_handler.register_model_client(model_client_cls=SparkAI)
                        elif self.llm_connector_plugin.connection_mode != "OpenAI":
                            # 其他的自定义ai连接客户端
                            agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                            agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                        # cur_system_message = cur_node["description"]
                        fun_record = query_function_mng(function_id=plugin_id)
                        o_file = os.path.join(os.getcwd(), "pluginsmanager", "plugins_function", fun_record.name + ".py")
                        t_file = os.path.join(os.getcwd(), "coding", fun_record.name + ".py")
                        shutil.copy2(o_file, t_file)

                        cur_system_message = agent_task_handler.system_message

                        cur_system_message = cur_system_message + fun_record.detail
                        print("cur_system_message:", cur_system_message)
                        agent_task_handler.update_system_message(cur_system_message)

                        message = "\n" + chat_result.summary

                        if chat_result.summary != 'No Function Found****':
                            print("non function go next V2")

                            agent_human = UserProxyAgent(
                                "Human",
                                human_input_mode="ALWAYS",
                                code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                                # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                                max_consecutive_auto_reply=10,

                            )

                            message = message + "\n继续完成没有完成的任务。"

                            chat_result = agent_human.initiate_chat(
                                agent_task_handler,
                                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                                # message=f"""{messages[-1]["content"]}""",
                                # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                                message=message,
                                clear_history=True
                            )
                            print("chatresult:", chat_result)
                    elif plugin_type == "plg_":
                        pass
                    elif plugin_type == "skl_":
                        pass
                    else:
                        # 现写代码
                        pass

                elif cur_node["type"] == "internet":
                    plugin_id = cur_node["plugin"]
                    record = query_PluginMng(plugin_id=plugin_id)
                    plugin = load_plugin_headless(self, record)
                    question = cur_node["description"]
                    result = plugin.run(question)

                    answer = result[1]
                    print("internet:", answer)

                    web_service_result = answer
                    task_handle_result = task_handle_result + web_service_result

                elif cur_node["type"] == "km":
                    km_doc_content = self.get_km_content(question_to_retrieve_from_km, plugin_id)

                elif cur_node["type"] == "variable":
                    desc = cur_node["description"]
                    agent_task_handler = AssistantAgent(
                        name="Task_Handler",
                        system_message=system_message_er_re,
                        llm_config=llm_config,
                    )

                    message = "我需要对一些文本进行变量提取，请认真阅读，并根据我后面的要求提取。我的文本是：" + re_er_content + ";我的要求是：" + desc + ";请以json格式给我返回提取的数据，并附加相应的参数说明。"
                    chat_result = agent_human.initiate_chat(
                        agent_task_handler,
                        # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                        # message=f"""{messages[-1]["content"]}""",
                        # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                        # max_turns=2,
                        message=message,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)
                    re_er_result = chat_result.summary

                elif cur_node["type"] == "condition":
                    desc = cur_node["description"]
                    agent_task_handler = AssistantAgent(
                        name="Task_Handler",
                        system_message=system_message_er_re,
                        llm_config=llm_config,
                    )

                    message = "我正在进行流程流转步骤的选择，我要在2个或2个以上的流转步骤中根据当前情况选择最合适的一个。当前情况是：" + condition_content + ";我的要求是：" + desc + ";请你以最简洁的语言告诉我所选的下一步骤的名称，不要有任何附加说明，只要步骤名称"
                    chat_result = agent_human.initiate_chat(
                        agent_task_handler,
                        # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                        # message=f"""{messages[-1]["content"]}""",
                        # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                        # max_turns=2,
                        message=message,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)
                    condition_result = chat_result.summary

                elif cur_node["type"] == "human":
                    desc = cur_node["description"]
                    ask_human_content = "当前情况如上述，请根据情况提供决策支持。" + desc
                    human_feed_back = self.speaker.input(ask_human_content)

                elif cur_node["type"] == "end":
                    desc = cur_node["description"]
                    agent_task_handler = AssistantAgent(
                        name="Task_Handler",
                        system_message=system_message_assistant_common,
                        llm_config=llm_config,
                    )

                    message = "这是整个工作流执行的情况，请你总结一下，并按用户的要求输出，工作流执行情况如下：" + task_handle_result + "用户的输出要求如下：" + desc
                    chat_result = agent_human.initiate_chat(
                        agent_task_handler,
                        # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                        # message=f"""{messages[-1]["content"]}""",
                        # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                        # max_turns=2,
                        message=message,
                        clear_history=True
                    )
                    print("chatresult:", chat_result)
                    final_result = chat_result.summary

                    # # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
                    # if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                    #     agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    #     agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    #     agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
                    # elif self.llm_connector_plugin.connection_mode == "SparkAI":
                    #     agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
                    #     agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
                    #     agent_task_handler.register_model_client(model_client_cls=SparkAI)
                    # elif self.llm_connector_plugin.connection_mode != "OpenAI":
                    #     # 其他的自定义ai连接客户端
                    #     agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
                    #     agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
                    #     agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

                    print("workflow end")
                    return
                    break

                next_nodes = self.get_next_nodes(workflow_cfg, cur_node["id"])
                if not next_nodes:
                    return
                    break
                cur_node = next_nodes[0]


        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        # self.speaker.speak(reply, sep="", end="")
        workflow_conclusion = "任务结束！"
        self.speaker.speak(f"--------------------------------------------------------------------------------", sep="", end="")
        self.speaker.speak(f"\n\n\n**✅执行完毕[■■■■■■■■■]100%  💬结果如下:**\n\n{workflow_conclusion}", sep="", end="")
        reply = self.speaker.answer_cache
        self.speaker.commit_and_refresh()

        return (reply, "")

    def get_km_content(self, question, km_id):
        retrieve_doc_content = ""
        km_record = query_KMCfg(km_id=km_id)
        vector_path = km_record.kmpath
        persist_directory = os.path.join(os.getcwd(), "km", vector_path, "vector")
        embedding_model_name = km_record.embeddingmodel
        docs = getvectorkm_String(question, persist_directory, embedding_model_name)
        self.retrieve_doc_list = docs
        print(docs)
        print(docs[0][0].page_content)
        retrieve_doc_content = docs[0][0].page_content
        return retrieve_doc_content

    def execute_code(self, code: str) -> dict:
        """
        执行给定的代码字符串，并返回执行环境中的变量字典。

        参数:
        code (str): 要执行的代码字符串。

        返回:
        dict: 包含执行后环境中的变量。
        """
        # 创建一个局部命名空间字典，用于存储执行的代码中产生的变量
        local_namespace = {}

        try:
            # 使用 exec() 动态执行代码，并将变量存储在 local_namespace 中
            exec(code, {}, local_namespace)
        except Exception as e:
            # 捕获并打印代码执行期间的异常
            print(f"代码执行时发生错误: {e}")

        # 返回包含代码执行结果的局部命名空间字典
        return local_namespace

    def get_all_function_json_list(self):
        records = query_function_mng_all()  # 获取所有记录
        formatted_records = [{"functionname": record.name, "description": record.description} for record in records]  # 格式化记录
        result_json = json.dumps(formatted_records, ensure_ascii=False)  # 转换为JSON字符串
        return result_json

    def get_all_mcp_json_list(self):
        records = query_mcp_mng_all()  # 获取所有记录
        formatted_records = [{"functionname": record.name, "description": record.description} for record in records]  # 格式化记录
        result_json = json.dumps(formatted_records, ensure_ascii=False)  # 转换为JSON字符串
        return result_json

    def address_task(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        message = messages[-1]["content"]

        if (message.startswith("@@workflow")):
            workflow_id = message[10:]
            record = query_workflow_mng(workflow_id=workflow_id)
            if (record):
                wf_cfg = record.detail
                workflow = json.loads(wf_cfg)
                print(workflow)

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        system_message_mcp_handler = get_prompt_by_title("Mcp_Handler")
        agent_human = UserProxyAgent(
            "Human",
            human_input_mode="ALWAYS",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=10,

        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )

        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        # agent_task_handler = AssistantAgent(
        #     name="Task_Handler",
        #     system_message=system_message_task_handler,
        #     llm_config=llm_config,
        # )

        print("i ask question:", messages)

        func_name = "calculator_tool_for_call"
        fun = globals()[func_name]
        description = "A simple calculator"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)
        # 动态执行文本代码的示例

        # 定义一个字符串类型的代码

        # run_plugin=self.run_plugin
        code_to_executebakok = '''
from typing import Annotated, Literal
def get_weather_tool_for_call_V2(city: str) -> str:    
    """
    this function is used to get the weather of a city
    city:a city name
    """
    plugin_name = "操作Chrome浏览器"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result
    
tmp_fun=get_weather_tool_for_call_V2("Shanghai") 
        '''

        code_to_execute = '''
from typing import Annotated, Literal
def get_stock_price_tool_for_call(companies: str) -> str:    
    """
    This function is designed to fetch the stock prices of given companies.这个函数接收一个以逗号分隔的字符串参数companies,You can provide multiple company at one time.For example: "Google,Meta"

    参数:
    companies (str): 这个函数接收一个以逗号分隔的字符串参数companies,以逗号分隔的公司名称字符串。例如: "CompanyA,CompanyB"

    Returns:
    str: The result from the 'run_plugin' function, which presumably contains 
         the stock prices of the specified companies.
    """
    plugin_name = "操作Chrome浏览器"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        # first_key = next(iter(execution_result))
        # first_value = execution_result[first_key]
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t
        #         # 定义一个字符串类型的代码
        #         code_to_execute = '''
        # def get_weather_tool_for_call_V2(city: str) -> str:
        #     """
        #     this function is used to get the weather of a city
        #     city:a city name
        #     """
        #     return f"The weather forecast for {city} at {datetime.now()} is Rainy."
        # tmp_fun=get_weather_tool_for_call_V2("Shanghai")
        #     '''
        #
        #         # 使用 exec() 动态执行代码
        #         t=exec(code_to_execute)

        func_name = "get_stock_price_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "get the stock price of a list of company,这个函数接收一个以逗号分隔的字符串参数companies"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def save_data_as_excel_tool_for_call(data_json: str) -> str:    
    """
    This function is designed to save data in a excel file

    参数:
    data_json (str): 这是一个json结构的文本字符串,它的结构是{"names":["meta","google"],"prices":[100,200],"currencys":["USD","RMB"]}

    Returns:
    str: The file path that the excel file is saved.
    """
    plugin_name = "生成Excel"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                        '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "save_data_as_excel_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "This function is designed to save data in a excel file"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def save_data_as_ppt_tool_for_call(data_json: str) -> str:    
    """
    This function is designed to save data in a ppt file

    参数:
    data_json (str): 这是一个json结构的文本字符串,它的结构是{"names":["meta","google"],"prices":[100,200],"currencys":["USD","RMB"]}

    Returns:
    str: The file path that the ppt file is saved.
    """
    plugin_name = "生成PPT"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "save_data_as_ppt_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "This function is designed to save data in a ppt file"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def send_file_to_wechat_tool_for_call(file_path: str,friend_name: str) -> str:    
    """
    这个函数被设计用来向微信好友发送文件

    参数:
    file_path (str): 要发送的文件的文件路径
    friend_name (str): 微信好友的名称

    Returns:
    str: 是否发送成功.
    """
    plugin_name = "操作微信"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        # first_key = next(iter(execution_result))
        # first_value = execution_result[first_key]
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "send_file_to_wechat_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "这个函数被设计用来向微信好友发送文件"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
        if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            # agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
            agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
            # agent_task_handler.register_model_client(model_client_cls=SparkAI)
        elif self.llm_connector_plugin.connection_mode == "Anthropic":
            agent_tools_wizard.register_model_client(model_client_cls=AnthropicClient)
            agent_task_plan_scheduler.register_model_client(model_client_cls=AnthropicClient)
            # agent_task_handler.register_model_client(model_client_cls=AnthropicClient)
        elif self.llm_connector_plugin.connection_mode != "OpenAI":
            # 其他的自定义ai连接客户端
            agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
            agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
            # agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

        print(agent_tools_wizard.llm_config["tools"])

        try:
            use_question = message
            chat_result = agent_human.initiate_chat(
                agent_task_plan_scheduler,
                message=message,
                silent=True,
                # max_turns=1,
                clear_history=True
            )
            print("chatresult:", chat_result)

            message = use_question + "\n" + chat_result.summary
            message = message + "\n请对上述总结进行分析，列出哪些是你可以用函数调用进行处理的。\n然后调用相应的函数进行处理。\n最后总结一下哪些任务是你处理好的，哪些任务需要Task_Handler进行处理"
            chat_result = agent_human.initiate_chat(
                agent_tools_wizard,
                silent=True,
                message=message,
                clear_history=True
            )
            print("chatresult:", chat_result)

            function_json_list = self.get_all_function_json_list()
            print("function_json_list:", function_json_list)

            message = use_question + "\n" + chat_result.summary
            message = message + "\n请对上述内容进行分析，看看任务是否都完成了，如果还有任务没有完成，请看一下，我下面的提供的函数列表是否可以用来完成任务，如果有合适的函数请明确指出它的名词，并按如下格式返回该函数名称【*函数名称*】。我的函数列表如下:" + function_json_list

            chat_result = agent_human.initiate_chat(
                agent_task_plan_scheduler,
                message=message,
                silent=True,
                # max_turns=1,
                clear_history=True
            )
            print("chatresult:", chat_result)

            propose_function = ""
            start = chat_result.summary.find('【*') + 2  # 找到起始索引，并跳过 '【*'
            end = chat_result.summary.find('*】', start)  # 找到结束索引
            if start >= 2 and end != -1:
                propose_function = chat_result.summary[start:end]

            print("propose_function；", propose_function)

            if propose_function:
                message = "\n" + chat_result.summary + "这是我建议使用的函数：" + propose_function + "，请根据相关的任务要求，把相关的任务完成掉。"
            else:
                message = "\n" + chat_result.summary

            system_message_task_handler = system_message_task_handler.replace("XXXXXXXX", propose_function)

            function_record = query_function_mng(name=propose_function)
            function_desc = function_record.detail

            system_message_task_handler = system_message_task_handler + "\n" + function_desc

            print("the system_message_task_handler:", system_message_task_handler)

            agent_task_handler = AssistantAgent(
                name="Task_Handler",
                system_message=system_message_task_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_task_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_task_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端

                agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

            if chat_result.summary != 'No Function Found****':

                agent_human = UserProxyAgent(
                    "Human",
                    human_input_mode="ALWAYS",
                    code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                    # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                    max_consecutive_auto_reply=10,

                )

                message = message + "\n继续完成没有完成的任务。"

                chat_result = agent_human.initiate_chat(
                    agent_task_handler,
                    silent=True,
                    message=message,
                    clear_history=True
                )
                print("chatresult:", chat_result)


            #go with mcp
            mcp_json_list = self.get_all_mcp_json_list()
            print("mcp_json_list:", mcp_json_list)

            message = use_question + "\n" + chat_result.summary
            message = message + "\n请对上述内容进行分析，看看任务是否都完成了，如果还有任务没有完成，请看一下，我下面的提供的函数列表是否可以用来完成任务，如果有合适的函数请明确指出它的名词，并按如下格式返回该函数名称【*函数名称*】。我的函数列表如下:" + mcp_json_list

            chat_result = agent_human.initiate_chat(
                agent_task_plan_scheduler,
                message=message,
                silent=True,
                # max_turns=1,
                clear_history=True
            )
            print("chatresult:", chat_result)

            propose_function = ""
            start = chat_result.summary.find('【*') + 2  # 找到起始索引，并跳过 '【*'
            end = chat_result.summary.find('*】', start)  # 找到结束索引
            if start >= 2 and end != -1:
                propose_function = chat_result.summary[start:end]

            print("propose_function；", propose_function)



            mcp_record = query_mcp_mng(name=propose_function)
            mcp_desc = mcp_record.detail

            mcp_handler_content = get_prompt_by_title("Mcp_Handler_Content")
            mcp_handler_content = mcp_handler_content.replace("_task_desc_", chat_result.summary)
            mcp_handler_content = mcp_handler_content.replace("_tools_desc_", mcp_desc)



            print("the mcp_handler_content:", mcp_handler_content)

            agent_mcp_handler = AssistantAgent(
                name="Mcp_Handler",
                system_message=system_message_mcp_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_mcp_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_mcp_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_mcp_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端

                agent_mcp_handler.register_model_client(model_client_cls=CustomizeClient)

            if chat_result.summary != 'No Function Found****':
                agent_human = UserProxyAgent(
                    "Human",
                    human_input_mode="ALWAYS",
                    code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                    # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                    max_consecutive_auto_reply=10,

                )

                message = mcp_handler_content

                chat_result = agent_human.initiate_chat(
                    agent_mcp_handler,
                    silent=True,
                    message=message,
                    clear_history=True
                )
                print("chatresult:", chat_result)
                print("chatresult summary:", chat_result.summary)
                content = chat_result.summary
                if "```json" in content:
                    content = re.sub(r'^\s*```json\s*|\s*```\s*$', '', content, flags=re.DOTALL)
                content_json = json.loads(content)
                function_name = content_json.get("function_name","")
                parameters = content_json.get("parameters",None)
                if parameters:
                    parameters_str = json.dumps(parameters)
                mcp_result=self.run_mcp(propose_function,function_name,parameters_str)

                message = use_question + "\n" + mcp_result
                message = message + "\n请对上述内容进行总结，看看任务是否都完成了。"

                chat_result = agent_human.initiate_chat(
                    agent_task_plan_scheduler,
                    message=message,
                    silent=True,
                    # max_turns=1,
                    clear_history=True
                )




        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = "任务执行完毕！"
        self.speaker.speak(reply, sep="", end="")
        self.speaker.commit_and_refresh()
        return reply

    def run_function(self, record, question, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        message = ""

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        agent_human = UserProxyAgent(
            "Human",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            # human_input_mode="TERMINATE",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=1,
        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )
        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        try:
            self.speaker.speak("**🤔🛠️开始使用工具处理您的问题......**\n\n", sep="", end="")
            propose_function = record.name
            if propose_function:
                message = "这是用户的问题:" + question + "\n这是我建议使用的函数：" + propose_function + "，请根据相关的问题，把相关的问题完成掉。"
            else:
                message = "这是用户的问题:" + question

            system_message_task_handler = system_message_task_handler.replace("XXXXXXXX", propose_function)

            function_record = record
            function_desc = function_record.detail

            system_message_task_handler = system_message_task_handler + "\n" + function_desc

            print("the system_message_task_handler:", system_message_task_handler)

            agent_task_handler = AssistantAgent(
                name="Task_Handler",
                system_message=system_message_task_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_task_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_task_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端
                agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

            message = message + "\n继续完成没有完成的任务。"

            chat_result = agent_human.initiate_chat(
                agent_task_handler,
                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                # message=f"""{messages[-1]["content"]}""",
                # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                silent=True,
                message=message,
                # summary_method="reflection_with_llm",
                summary_method='last_msg',  # 缺省的
                clear_history=True
            )
            print("chatresult:", chat_result)



        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = chat_result.summary
        reply = f"""
        - 用户的问题如下:{question}
        - 我通过工具处理用户问题获得了如下的反馈:{reply}
        - 请你在工具的反馈内容中识别出工具处理的最终结果，把你识别出来的这个结果告诉用户，请不要回顾，不要解释，不要输出其他无关的内容
        - 格式要求，输出的内容请以如下语句开头:
          \n**✅处理完毕[■■■■■■■■■]100%  💬总结如下:**\n\n\n
        """
        # self.speaker.speak(reply, sep="", end="")
        # self.speaker.speak("\n**✅处理完毕[■■■■■■■■■]100%  💬总结如下:**\n\n", sep="", end="")
        # reply = chat_result.summary
        # self.speaker.speak(reply)
        # self.speaker.commit_and_refresh()
        return (question, reply)

    def think_and_run_function(self, record, question, messages):
        try:

            propose_function = record.name


            code = f'''
from {propose_function} import {propose_function}
markdown_content = """{question}"""
output = {propose_function}(markdown_content)
print(output)
                            '''
            work_dir = Path("coding")
            work_dir.mkdir(exist_ok=True)

            # executor = LocalCommandLineCodeExecutor(work_dir=work_dir, functions=[add_two_numbers, load_data])#使用codebakok这种徐娅有functions
            executor = LocalCommandLineCodeExecutor(work_dir=work_dir)  # 使用code这种直接指明functions文件的就不需要这里写functions这个参数了

            execute_result = executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code=code),
                ]
            )
            print(execute_result)
            print("exit_code", execute_result.exit_code)
            print("output", execute_result.output)
            print("code_file", execute_result.code_file)


        except Exception as e:
            print(f"发生如下错误: {e}")
            reply = f"发生如下错误: {e}"


        reply = execute_result.output
        return reply

    def think_and_run_functionbak(self, record, question, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        message = ""

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        agent_human = UserProxyAgent(
            "Human",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            # human_input_mode="TERMINATE",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=1,
        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )
        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        try:
            self.speaker.speak("**🤔🛠️开始使用工具处理您的问题......**\n\n", sep="", end="")
            propose_function = record.name
            # if propose_function:
            #     message = "这是用户的问题:" + question + "\n这是我建议使用的函数：" + propose_function + "，请根据相关的问题，把相关的问题完成掉。\n将用户问题的全部内容作为参数传入要调用的函数。"
            # else:
            #     message = "这是用户的问题:" + question

            message = "1.使用的函数：" + propose_function + "\n2.输出格式：{'result_of_function':'the function result'}\n3.参数请使用两个__system__字符串中间的内容：\n__system__"+question+"__system__"

            system_message_task_handler = system_message_task_handler.replace("XXXXXXXX", propose_function)

            function_record = record
            function_desc = function_record.detail

            system_message_task_handler = system_message_task_handler + "\n" + function_desc

            print("the system_message_task_handler:", system_message_task_handler)

            agent_task_handler = AssistantAgent(
                name="Task_Handler",
                system_message=system_message_task_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_task_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_task_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端
                agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

            # message = message + "\n继续完成没有完成的任务。\n输出要求：仅返回函数调用后返回的内容，不允许添加任何说明，不允许添加任何字符。"
            print("run tool message:",message)
            chat_result = agent_human.initiate_chat(
                agent_task_handler,
                silent=True,
                message=message,
                # summary_method="reflection_with_llm",
                summary_method='last_msg',  # 缺省的
                clear_history=True
            )
            print("chatresult:", chat_result)



        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as reqex:
            print(f"请求异常: {reqex}")
            reply = f"请求异常: {reqex}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = chat_result.summary
        data = chat_result.chat_history
        result_str = None

        # for item in data:
        #     match = re.search(r"\{.*'result_of_function'.*\}", item["content"])
        #     if match:
        #         result_dict = ast.literal_eval(match.group())  # 转成字典
        #         result_str = result_dict["result_of_function"]  # 直接取字符串值

        for item in data:
            match = re.search(r"'result_of_function':\s*'([^']+)'", item["content"])
            if match:
                result_str = match.group(1)  # 直接取出括号里的内容

        reply = result_str
        return reply


    def think_and_run_mcp(self, record_id_int, mcp_name, question):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        message = ""

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        system_message_mcp_handler = get_prompt_by_title("Mcp_Handler")
        agent_human = UserProxyAgent(
            "Human",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            # human_input_mode="TERMINATE",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=1,
        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )
        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        try:
            self.speaker.speak("**🤔🛠️开始使用工具处理您的问题......**\n\n", sep="", end="")
            mcp_record = query_mcp_mng(id=record_id_int)
            mcp_desc = mcp_record.detail

            mcp_handler_content = get_prompt_by_title("Mcp_Handler_Content")
            mcp_handler_content = mcp_handler_content.replace("_task_desc_", question)
            mcp_handler_content = mcp_handler_content.replace("_tools_desc_", mcp_desc)

            print("the mcp_handler_content:", mcp_handler_content)

            agent_mcp_handler = AssistantAgent(
                name="Mcp_Handler",
                system_message=system_message_mcp_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_mcp_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_mcp_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_mcp_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端

                agent_mcp_handler.register_model_client(model_client_cls=CustomizeClient)


            agent_human = UserProxyAgent(
                "Human",
                human_input_mode="ALWAYS",
                code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                max_consecutive_auto_reply=10,

            )

            message = mcp_handler_content

            # chat_result = agent_human.initiate_chat(
            #     agent_mcp_handler,
            #     silent=True,
            #     message=message,
            #     clear_history=True
            # )

            self.speaker.speak(f"\n\n根据您的问题，我将使用mcp:{mcp_name}来处理，下面是即将调用的具体工具名和参数:\n\n", sep="", end="")

            messages = [{"content": mcp_handler_content, "role": "user"}]
            reply = agent_mcp_handler.generate_reply(messages=messages)
            reply = reply['content'] if isinstance(reply, dict) and 'content' in reply else reply




            print("reply:", reply)

            content = reply
            if "```json" in content:
                content = re.sub(r'^\s*```json\s*|\s*```\s*$', '', content, flags=re.DOTALL)
            content_json = json.loads(content)
            function_name = content_json.get("function_name", "")
            parameters = content_json.get("parameters", None)
            if parameters:
                parameters_str = json.dumps(parameters)
            mcp_result = self.run_mcp(mcp_name, function_name, parameters_str)



            # self.speaker.speak("\n**✅处理完毕[■■■■■■■■■]100%  💬总结如下:**\n\n", sep="", end="")
            #
            # self.speaker.speak(mcp_result)
            # self.speaker.commit_and_refresh()

            # return mcp_result



        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()#todo
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = mcp_result
        reply = f"""
                - 用户的问题如下:{question}
                - 我通过工具处理用户问题获得了如下的反馈:{reply}
                - 请你在工具的反馈内容中识别出工具处理的最终结果，把你识别出来的这个结果告诉用户，请不要回顾，不要解释，不要输出其他无关的内容
                - 格式要求，输出的内容请以如下语句开头:
                  \n**✅处理完毕[■■■■■■■■■]100%  💬总结如下:**\n\n\n
                """
        # self.speaker.speak(reply, sep="", end="")
        # self.speaker.speak("\n**✅处理完毕[■■■■■■■■■]100%  💬总结如下:**\n\n", sep="", end="")
        # reply = chat_result.summary
        # self.speaker.speak(reply)
        # self.speaker.commit_and_refresh()
        return (question, reply,mcp_result)

    def think_and_pick_a_tool_to_solve_problem(self,question):
        self.current_ask_agent_to_instruct_flag = "ask_agent_to_select_tool"
        role_prompt = get_prompt_by_title("__select_a_tool__")

        provided_tool_list = util.get_tool_list()

        provided_tool_list_str = json.dumps(provided_tool_list, indent=4, ensure_ascii=False)

        role_prompt = role_prompt.replace("__provided_tool_list__", provided_tool_list_str)
        print(provided_tool_list_str)

        question = question.lstrip("@:")
        system_message_tool_handler = role_prompt

        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同


        try:
            self.speaker.speak("**🔍️❓正在查找工具来处理您的的问题......**\n\n", sep="", end="")

            agent_tool_handler = AssistantAgent(
                name="Tool_Handler",
                system_message=system_message_tool_handler,
                llm_config=llm_config,
            )

            # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
            if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
                agent_tool_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            elif self.llm_connector_plugin.connection_mode == "SparkAI":
                agent_tool_handler.register_model_client(model_client_cls=SparkAI)
            elif self.llm_connector_plugin.connection_mode == "Anthropic":
                agent_tool_handler.register_model_client(model_client_cls=AnthropicClient)
            elif self.llm_connector_plugin.connection_mode != "OpenAI":
                # 其他的自定义ai连接客户端
                agent_tool_handler.register_model_client(model_client_cls=CustomizeClient)




            messages = [{"content": question, "role": "user"}]
            reply = agent_tool_handler.generate_reply(messages=messages)
            reply = reply['content'] if isinstance(reply, dict) and 'content' in reply else reply

            print("reply:", reply)

            content = reply
            content = re.sub(r'^\s*```json\s*|\s*```\s*$', '', content, flags=re.DOTALL)
            result_list = json.loads(content)
            if result_list:
                # 使用max函数与lambda表达式来获取match_score最高的工具
                tool = max(result_list, key=lambda x: x["match_score"])
                print("get the tool:", tool)
                id = tool["id"]
                name = tool["name"]
                type_str = tool["type"]
                reason_for_selection = tool["reason_for_selection"]
                match_score = tool["match_score"]

                if type_str == "workflow":
                    record = query_workflow_mng(workflow_id=id)
                    instruction_content = record.instruction
                    result=f"@{instruction_content}:{question}"


                elif type_str == "plugin":
                    record = query_PluginMng(plugin_id=id)
                    instruction_content = record.instruction
                    result=f"@{instruction_content}:{question}"


                elif type_str == "function":
                    record = query_function_mng(function_id=id)
                    instruction_content = record.instruction
                    result=f"@{instruction_content}:{question}"


                elif type_str == "mcp":
                    record = query_mcp_mng(mcp_id=id)
                    instruction_content = record.instruction
                    result=f"@{instruction_content}:{question}"


                elif type_str == "skill":
                    print("in skill:",id)
                    record = query_skill_mng(skill_id=id)
                    instruction_content = record.instruction
                    result=f"@{instruction_content}:{question}"

        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True
        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as reqexce:
            print(f"请求异常: {reqexce}")
            reply = f"请求异常: {reqexce}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tool_handler.client._clients[0]._oai_client.close()  # todo
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        time.sleep(0.5)
        speaker.commit_and_refresh()
        return (type_str,result)

    def start_process(self):
        """启动子进程"""
        try:
            # Starting a subprocess with pipes configured for communication
            # 设置数据库目录及文件路径
            file_path = get_file_full_path('mcp','client_subprocess.py')

            self.process = subprocess.Popen(
                [sys.executable,file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # 改为无缓冲
                universal_newlines=True,
                encoding='utf-8'
            )
            return True
        except Exception as e:
            self.error_occurred.emit(f"启动子进程失败: {str(e)}")
            return False

    def send_command(self, process, command, timeout=30):
        """发送命令并读取响应，添加超时控制"""
        try:
            print(f"发送命令: {command.strip()}")

            # 写入命令
            process.stdin.write(command)
            process.stdin.flush()

            # 使用非阻塞方式读取输出
            output_lines = []
            error_lines = []

            start_time = time.time()
            json_response_found = False

            # 读取stdout，直到找到JSON响应
            while time.time() - start_time < timeout:
                # 检查进程是否还活着
                if process.poll() is not None:
                    print("子进程已结束")
                    break

                try:
                    # Windows系统的处理方式
                    try:
                        line = process.stdout.readline()
                        if line:
                            line_stripped = line.strip()
                            output_lines.append(line)
                            print(f"读取输出行: {line_stripped}")

                            # 检查是否是JSON响应（命令的最终结果）
                            if line_stripped.startswith('{') and line_stripped.endswith('}'):
                                try:
                                    json.loads(line_stripped)  # 验证是否为有效JSON
                                    json_response_found = True
                                    print(f"找到JSON响应: {line_stripped}")
                                    break  # 找到JSON响应，结束读取
                                except json.JSONDecodeError:
                                    pass  # 不是有效JSON，继续读取

                        else:
                            # 没有更多输出，等待一下
                            time.sleep(0.1)
                    except Exception as read_error:
                        print(f"读取stdout时出错: {read_error}")
                        time.sleep(0.1)

                except Exception as e:
                    print(f"读取过程中出错: {e}")
                    break

            # 如果没有找到JSON响应，再等待一点时间
            if not json_response_found:
                print("未找到JSON响应，继续等待...")
                additional_wait = 2  # 额外等待2秒
                additional_start = time.time()

                while time.time() - additional_start < additional_wait:
                    try:
                        line = process.stdout.readline()
                        if line:
                            line_stripped = line.strip()
                            output_lines.append(line)
                            print(f"额外读取: {line_stripped}")

                            if line_stripped.startswith('{') and line_stripped.endswith('}'):
                                try:
                                    json.loads(line_stripped)
                                    json_response_found = True
                                    print(f"找到延迟JSON响应: {line_stripped}")
                                    break
                                except json.JSONDecodeError:
                                    pass
                        else:
                            time.sleep(0.1)
                    except:
                        time.sleep(0.1)

            output = ''.join(output_lines)
            errors = ''.join(error_lines)

            print(f"命令执行完成，输出长度: {len(output)}, 错误长度: {len(errors)}, JSON响应: {json_response_found}")

            return output, errors

        except Exception as e:
            error_msg = f"发送命令时出错: {str(e)}"
            print(error_msg)
            return "", error_msg

    def run_mcp(self,mcp_name, tool_name, schema):
        """主执行方法"""
        try:
            # 启动子进程
            if not self.start_process():
                return

            print("子进程启动成功")

            # 等待子进程初始化
            time.sleep(1)

            # 发送连接命令
            connect_command = '{"command": "connect", "args": {"path":"'+mcp_name+'"}}\n'
            # connect_command = '{"command": "connect", "args": {"path":"server.py"}}\n'
            print("准备发送连接命令...")

            connect_output, connect_errors = self.send_command(self.process, connect_command)

            print("Connect Output:", connect_output)
            print("Connect Errors:", connect_errors)

            if connect_errors:
                print(f"连接错误: {connect_errors}")
            else:
                print(f"连接输出: {connect_output}")

                # 等待子进程初始化
            time.sleep(1)

            # 发送查询命令
            query_command = '{"command": "'+tool_name+'", "args": '+schema+'}\n'
            # query_command = '{"command": "query", "args": {"text":"CA"}}\n'
            print("准备发送查询命令...")

            query_output, query_errors = self.send_command(self.process, query_command)

            print("Query Output:", query_output)
            print("Query Errors:", query_errors)

            if query_errors:
                print(f"查询错误: {query_errors}")
            else:
                print(f"查询输出: {query_output}")

            return query_output

        except Exception as e:
            error_msg = f"线程执行错误: {str(e)}"
            print(error_msg)
            # self.error_occurred.emit(error_msg)

    def query(self):
        """主执行方法"""
        try:
            # 等待子进程初始化
            time.sleep(1)

            # 发送查询命令
            query_command = '{"command": "query", "args": {"text":"CA"}}\n'
            print("准备发送查询命令...")

            query_output, query_errors = self.send_command(self.process, query_command)

            print("Query Output:", query_output)
            print("Query Errors:", query_errors)

            if query_errors:
                print(f"查询错误: {query_errors}")
            else:
                print(f"查询输出: {query_output}")

        except Exception as e:
            error_msg = f"线程执行错误: {str(e)}"
            print(error_msg)
            # self.error_occurred.emit(error_msg)

        finally:
            # 清理子进程
            if self.process:
                try:
                    print("正在清理子进程...")
                    if self.process.stdin:
                        self.process.stdin.close()
                    if self.process.stdout:
                        self.process.stdout.close()
                    if self.process.stderr:
                        self.process.stderr.close()

                    # 等待进程结束
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    print("子进程清理完成")
                except Exception as e:
                    print(f"清理子进程时出错: {e}")
                    # 强制杀死进程
                    try:
                        self.process.kill()
                    except:
                        pass

    def address_tasknew(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        if self.llm_connector_plugin.connection_mode != "OpenAI":
            llm_config = {"cache_seed": None, "config_list": [llm_config]}  # 注意格式和openai不同

        message = messages[-1]["content"]

        if (message.startswith("@@workflow")):
            workflow_id = message[10:]
            record = query_workflow_mng(workflow_id=workflow_id)
            if (record):
                wf_cfg = record.detail
                workflow = json.loads(wf_cfg)
                print(workflow)

        system_message_task_plan_scheduler = get_prompt_by_title("Task_Plan_Scheduler")
        system_message_tools_wizard = get_prompt_by_title("Tools_Wizard")
        system_message_task_handler = get_prompt_by_title("Task_Handler")
        agent_human = UserProxyAgent(
            "Human",
            human_input_mode="ALWAYS",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
            max_consecutive_auto_reply=10,

        )

        agent_task_plan_scheduler = AssistantAgent(
            name="Task_Plan_Scheduler",
            system_message=system_message_task_plan_scheduler,
            llm_config=llm_config,
        )

        agent_tools_wizard = AssistantAgent(
            name="Tools_Wizard",
            system_message=system_message_tools_wizard,
            llm_config=llm_config,
        )

        agent_task_handler = AssistantAgent(
            name="Task_Handler",
            system_message=system_message_task_handler,
            llm_config=llm_config,
        )

        print("i ask question:", messages)

        func_name = "calculator_tool_for_call"
        fun = globals()[func_name]
        description = "A simple calculator"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)
        # 动态执行文本代码的示例

        # 定义一个字符串类型的代码

        # run_plugin=self.run_plugin
        code_to_executebakok = '''
from typing import Annotated, Literal
def get_weather_tool_for_call_V2(city: str) -> str:    
    """
    this function is used to get the weather of a city
    city:a city name
    """
    plugin_name = "操作Chrome浏览器"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

tmp_fun=get_weather_tool_for_call_V2("Shanghai") 
        '''

        code_to_execute = '''
from typing import Annotated, Literal
def get_stock_price_tool_for_call(companies: str) -> str:    
    """
    This function is designed to fetch the stock prices of given companies.这个函数接收一个以逗号分隔的字符串参数companies,You can provide multiple company at one time.For example: "Google,Meta"

    参数:
    companies (str): 这个函数接收一个以逗号分隔的字符串参数companies,以逗号分隔的公司名称字符串。例如: "CompanyA,CompanyB"

    Returns:
    str: The result from the 'run_plugin' function, which presumably contains 
         the stock prices of the specified companies.
    """
    plugin_name = "操作Chrome浏览器"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        # first_key = next(iter(execution_result))
        # first_value = execution_result[first_key]
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t
        #         # 定义一个字符串类型的代码
        #         code_to_execute = '''
        # def get_weather_tool_for_call_V2(city: str) -> str:
        #     """
        #     this function is used to get the weather of a city
        #     city:a city name
        #     """
        #     return f"The weather forecast for {city} at {datetime.now()} is Rainy."
        # tmp_fun=get_weather_tool_for_call_V2("Shanghai")
        #     '''
        #
        #         # 使用 exec() 动态执行代码
        #         t=exec(code_to_execute)

        func_name = "get_stock_price_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "get the stock price of a list of company,这个函数接收一个以逗号分隔的字符串参数companies"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def save_data_as_excel_tool_for_call(data_json: str) -> str:    
    """
    This function is designed to save data in a excel file

    参数:
    data_json (str): 这是一个json结构的文本字符串,它的结构是{"names":["meta","google"],"prices":[100,200],"currencys":["USD","RMB"]}

    Returns:
    str: The file path that the excel file is saved.
    """
    plugin_name = "生成Excel"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                        '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "save_data_as_excel_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "This function is designed to save data in a excel file"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def save_data_as_ppt_tool_for_call(data_json: str) -> str:    
    """
    This function is designed to save data in a ppt file

    参数:
    data_json (str): 这是一个json结构的文本字符串,它的结构是{"names":["meta","google"],"prices":[100,200],"currencys":["USD","RMB"]}

    Returns:
    str: The file path that the ppt file is saved.
    """
    plugin_name = "生成PPT"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "save_data_as_ppt_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "This function is designed to save data in a ppt file"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        code_to_execute = '''
from typing import Annotated, Literal
def send_file_to_wechat_tool_for_call(file_path: str,friend_name: str) -> str:    
    """
    这个函数被设计用来向微信好友发送文件

    参数:
    file_path (str): 要发送的文件的文件路径
    friend_name (str): 微信好友的名称

    Returns:
    str: 是否发送成功.
    """
    plugin_name = "操作微信"    
    from Agent import run_plugin
    params=list(locals().values())    
    result=run_plugin(*params)
    return result

                                '''

        # 执行代码并获取结果
        execution_result = self.execute_code(code_to_execute)
        # first_key = next(iter(execution_result))
        # first_value = execution_result[first_key]
        first_key = list(execution_result.keys())
        first_value = list(execution_result.values())
        fun_t = first_value[2]

        # 从返回的执行结果中获取我们关心的变量
        if 'tmp_fun' in execution_result:
            print(execution_result['tmp_fun'])  # 输出: Hello, World!
        else:
            print("未找到预期的结果变量。")

        tmp_fun = fun_t

        func_name = "send_file_to_wechat_tool_for_call"
        # fun = globals()[func_name]
        fun = tmp_fun
        description = "这个函数被设计用来向微信好友发送文件"

        agent_tools_wizard.register_for_llm(name=func_name, description=description)(fun)
        agent_human.register_for_execution(name=func_name)(fun)

        # 如果不是openai的模式要再所有的工具登记之后把model client登记一下，前面登记的没有用，必须放在后面
        if self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent_tools_wizard.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            agent_task_plan_scheduler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
            agent_task_handler.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent_tools_wizard.register_model_client(model_client_cls=SparkAI)
            agent_task_plan_scheduler.register_model_client(model_client_cls=SparkAI)
            agent_task_handler.register_model_client(model_client_cls=SparkAI)
        elif self.llm_connector_plugin.connection_mode != "OpenAI":
            # 其他的自定义ai连接客户端
            agent_tools_wizard.register_model_client(model_client_cls=CustomizeClient)
            agent_task_plan_scheduler.register_model_client(model_client_cls=CustomizeClient)
            agent_task_handler.register_model_client(model_client_cls=CustomizeClient)

        print(agent_tools_wizard.llm_config["tools"])

        try:
            use_question = message
            chat_result = agent_human.initiate_chat(
                agent_task_plan_scheduler,
                message=message,
                # max_turns=1,
                clear_history=True
            )
            print("chatresult:", chat_result)

            message = use_question + "\n" + chat_result.summary
            message = message + "\n请对上述总结进行分析，列出哪些是你可以用函数调用进行处理的。\n然后调用相应的函数进行处理。\n最后总结一下哪些任务是你处理好的，哪些任务需要Task_Handler进行处理"
            chat_result = agent_human.initiate_chat(
                agent_tools_wizard,
                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                # message=f"""{messages[-1]["content"]}""",
                # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                # max_turns=2,
                message=message,
                clear_history=True
            )
            print("chatresult:", chat_result)

            message = "\n" + chat_result.summary

            if chat_result.summary != 'No Function Found****':
                print("non function go next V2")

                # work_dir = Path("coding")
                # work_dir.mkdir(exist_ok=True)
                #
                # executor = LocalCommandLineCodeExecutor(work_dir=work_dir, functions=[convert_rmb_to_usd])#使用codebakok这种徐娅有functions
                #
                # user_proxy = UserProxyAgent(
                #     "User_Proxy",
                #     code_execution_config={"executor": executor},
                #     # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                #     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                #     max_consecutive_auto_reply=10,
                #
                # )

                print(agent_task_handler.llm_config["tools"])

                agent_human = UserProxyAgent(
                    "Human",
                    human_input_mode="ALWAYS",
                    code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
                    # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
                    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE") or x.get("content", "").rstrip().endswith("No Function Found"),
                    max_consecutive_auto_reply=10,

                )

                message = message + "\n继续完成没有完成的任务。"

                chat_result = agent_human.initiate_chat(
                    agent_task_handler,
                    # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                    # message=f"""{messages[-1]["content"]}""",
                    # message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",
                    message=message,
                    clear_history=True
                )
                print("chatresult:", chat_result)


        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent_tools_wizard.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误a: {e}"
            print(f"发生如下错误b: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        reply = "任务执行完毕！"
        self.speaker.speak(reply, sep="", end="")
        self.speaker.commit_and_refresh()
        return reply

    def autogen_run_code(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        autogen.Completion.set_cache(False)

        user_proxy = UserProxyAgent(
            "user_proxy",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            max_consecutive_auto_reply=2,

        )

        if self.llm_connector_plugin.connection_mode == "OpenAI":
            agent = AssistantAgent(
                name="chatbot",
                llm_config=llm_config,
            )

        elif self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent = AssistantAgent(
                name="chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent = AssistantAgent(
                name="chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=SparkAI)

        else:
            agent = AssistantAgent(
                name="chatbot",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=CustomizeClient)

        print("i ask question:", messages)
        # reply = agent.generate_reply(messages=[{"content": "介绍一下北京", "role": "user"}])
        # reply = agent.generate_reply(messages=[{"content": "我请你介绍一下潮阳", "role": "user"}])

        try:
            user_proxy.initiate_chat(
                agent,
                # message="""analyse my file, the file location is  C:\\dev\\ai-sns\\autogen\\MieruData\\data\\inputData\\Mytest.csv""",
                # message=f"""{messages[-1]["content"]}""",
                message="""hi,can you draw a 唐老鸭 and 米老鼠 for me.and you must execute the code""",

                clear_history=True
            )
        except:
            pass

        reply = agent.generate_reply(messages=messages)

        print("cjrok ....the reply:", reply)
        print(reply)

        if llm_config["stream"] == False:
            browser_page = self.browser_page
            self.speaker.runJavaScript('tchunks=`' + reply + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')
            # speaker.speak(reply, sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.commit_and_refresh()

        else:
            speaker.speak("", sep="", end="")
            speaker.speak("", sep="", end="")
            speaker.commit_and_refresh()
        return reply

    def chat_only(self, messages):
        speaker = self.speaker

        IOStream.set_global_default(AISNSIOStream(speaker))

        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)
        # 出来system角色的提示词
        system_role_prompt = self.system_role_prompt

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
        )

        if self.llm_connector_plugin.connection_mode == "OpenAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config=llm_config,
            )



        elif self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif self.llm_connector_plugin.connection_mode == "OpenAI-customize":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=OpenAICustomizeLLMClient)


        elif self.llm_connector_plugin.connection_mode == "OpenAI-customize-v2":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=OpenAICustomizeV2LLMClient)


        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=SparkAI)

        elif self.llm_connector_plugin.connection_mode == "Anthropic":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=AnthropicClient)

        elif self.llm_connector_plugin.connection_mode == "groq":
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},
            )
            # agent.register_model_client(model_client_cls=GroqClient)

        else:
            agent = AssistantAgent(
                name="chatbot",
                system_message=f"{system_role_prompt}",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            agent.register_model_client(model_client_cls=CustomizeClient)

        print("i ask question in chatonly:", messages)

        # reply = agent.generate_reply(messages=messages)
        error_occur = False
        try:
            # 假设 agent.generate_reply 使用 requests 库进行 HTTP 请求

            reply = agent.generate_reply(messages=messages)
            reply = reply['content'] if isinstance(reply, dict) and 'content' in reply else reply

        except requests.exceptions.ConnectionError as ce:
            print(f"连接错误: {ce}")
            reply = f"连接错误: {ce}"
            error_occur = True

        except requests.exceptions.Timeout as te:
            print(f"请求超时: {te}")
            reply = f"请求超时: {te}"
            error_occur = True
        except requests.exceptions.HTTPError as he:
            print(f"HTTP 错误: {he}")
            reply = f"HTTP 错误: {he}"
            error_occur = True
        except requests.exceptions.RequestException as re:
            print(f"请求异常: {re}")
            reply = f"请求异常: {re}"
            error_occur = True
        except Exception as e:
            error_str = f"{e}"

            if error_str == "用户中断":
                agent.client._clients[0]._oai_client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            elif error_str == "spark用户中断":
                # agent.client._clients[0].spark_client.client.close()
                reply = self.speaker.answer_cache + f"\n\n*****用户进行了中断输出操作!*****"
                self.speaker.answer_cache = ""
            else:
                reply = f"发生如下错误: {e}"
            print(f"发生如下错误: {e}")
            # reply = f"发生如下错误: {e}"
            error_occur = True

        print("cjrok ....the reply:", reply)
        print(reply)

        if error_occur:
            speaker.runJavaScript('tchunks=`' + reply + '`')
            speaker.runJavaScript('show_response_msg(tchunks)')
            speaker.runJavaScript('updatemaincontent()')
            speaker.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

        if llm_config["stream"] == False:
            speaker.runJavaScript('tchunks=`' + reply + '`')
            speaker.runJavaScript('show_response_msg(tchunks)')
            speaker.runJavaScript('updatemaincontent()')
            speaker.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
            # speaker.speak(reply, sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.commit_and_refresh()

        else:
            # speaker.speak("", sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.speak("__end_speak__", sep="", end="")
            if speaker:
                time.sleep(1)
                speaker.commit_and_refresh()

        return reply

    def chat_with_tool(self, messages):
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))
        # config_list = {"model": "gpt-4o", "api_key": "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", "cache_seed": None, "seed": 42, "temperature": 0, "stream": True}
        # config_list = {"model": "glm-4", "api_type": "chatglm", "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7", "temperature": 0.7, "cache_seed": None,"base_url": "https://open.bigmodel.cn/api/paas/v4","stream": True}
        # ********注意，注意，注意有些大模型的temprature不能为0***************
        # Create the agent that uses the LLM.
        llm_config = self.format_llm_config()
        print("llm_config", llm_config)

        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
        )

        if self.llm_connector_plugin.connection_mode == "OpenAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config=llm_config,
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )

        elif self.llm_connector_plugin.connection_mode == "OpenAI-compatible":
            agent = ConversableAgent(
                name="Assistant",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )
            agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif self.llm_connector_plugin.connection_mode == "OpenAI-customize":
            agent = ConversableAgent(
                name="Assistant",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )
            agent.register_model_client(model_client_cls=OpenAICustomizeLLMClient)


        elif self.llm_connector_plugin.connection_mode == "OpenAI-customize-v2":
            agent = ConversableAgent(
                name="Assistant",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )
            agent.register_model_client(model_client_cls=OpenAICustomizeV2LLMClient)


        elif self.llm_connector_plugin.connection_mode == "SparkAI":
            agent = AssistantAgent(
                name="chatbot",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )
            agent.register_model_client(model_client_cls=SparkAI)

        else:
            agent = AssistantAgent(
                name="chatbot",
                system_message="You are a helpful AI assistant. "
                               "You can help with simple calculations. "
                               "Return 'TERMINATE' when the task is done.",
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )
            cal = Calculator()
            t = cal.calculator
            register_function(
                t,
                caller=agent,
                executor=user_proxy,
                name="calculator",
                description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。",
            )
            agent.register_model_client(model_client_cls=CustomizeClient)

        print("i ask question:", messages)

        reply = agent.generate_reply(messages=messages)

        print("cjrok ....the reply:", reply)
        print(reply)

        if llm_config["stream"] == False:
            browser_page = self.browser_page
            self.speaker.runJavaScript('tchunks=`' + reply + '`')
            self.speaker.runJavaScript('show_response_msg(tchunks)')
            self.speaker.runJavaScript('updatemaincontent()')
            # speaker.speak(reply, sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.speak("", sep="", end="")
            # speaker.commit_and_refresh()

        else:
            speaker.speak("", sep="", end="")
            speaker.speak("", sep="", end="")
            speaker.commit_and_refresh()

        # try:

        # Register the tool signature with the assistant agent.
        # agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        # agent.register_for_llm(name="calculator", description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。")(t)
        #
        # # Register the tool function with the user proxy agent.
        # # user_proxy.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        # user_proxy.register_for_execution(name="calculator")(t)

        # agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        # chat_result = user_proxy.initiate_chat(agent, message="What is (44232 + 13312 / (232 - 32)) * 5 *1?")
        # chat_result = user_proxy.initiate_chat(agent, message="给我计算一下这个算式等于多少：44232 + 13312 / 232 - 32 * 5 * 1?")
        # chat_result = user_proxy.initiate_chat(agent, message="给我计算一下这个算式等于多少：44232和13312相除等于多少")
        chat_result = user_proxy.initiate_chat(agent, message="给我查询一下上海今天的煤炭价格")
        # # except:
        # #     pass

        return reply

    def autogen_run_toolbak(self, messages):
        # Let's first define the assistant agent that suggests tool calls.
        assistant = ConversableAgent(
            name="Assistant",
            system_message="You are a helpful AI assistant. "
                           "You can help with simple calculations. "
                           "Return 'TERMINATE' when the task is done.",
            llm_config={"config_list": [{"model": "gpt-4o", "api_key": "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"}]},
        )

        # The user proxy agent is used for interacting with the assistant agent
        # and executes tool calls.
        user_proxy = ConversableAgent(
            name="User",
            llm_config=False,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER",
        )

        cal = Calculator()
        t = cal.calculator

        # Register the tool signature with the assistant agent.
        assistant.register_for_llm(name="calculator", description="你是一个可以用来获取煤炭价格的工具，可以根据城市和时间获取相应的煤炭价格。")(t)

        # Register the tool function with the user proxy agent.
        user_proxy.register_for_execution(name="calculator")(t)

        chat_result = user_proxy.initiate_chat(assistant, message="What is (44232 + 13312 / (232 - 32)) * 5 *1?")

    def autogen_run1(self):
        browser_page = self.browser_page
        IOStream.set_global_default(AISNSIOStream("我是参数"))
        config_list = {"model": "gpt-3.5-turbo", "api_key": "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", "seed": 42, "temperature": 0, "stream": True}

        # Create the agent that uses the LLM.
        assistant = ConversableAgent("chatbot", llm_config=config_list)

        agent = ConversableAgent(
            "chatbot",
            llm_config=config_list,
            code_execution_config=False,  # Turn off code execution, by default it is off.
            function_map=None,  # No registered functions, by default it is None.
            human_input_mode="NEVER",  # Never ask for human input.
        )

        reply = agent.generate_reply(messages=[{"content": "给我详细介绍一下奥巴马.", "role": "user"}])
        print("cjrok ....the reply:", reply)
        print(reply)

    def autogen_runv2(self):
        config_list_claude = [
            {
                # Choose your model name.
                "model": "glm-4",
                # You need to provide your API key here.
                "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "stream": True,
                "api_type": "ChatGLM",
                "model_client_cls": "CustomOpenAIClient",
            }
        ]

        config_list_zhipu = [
            {
                # Choose your model name.
                "model": "glm-4",
                # You need to provide your API key here.
                "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "stream": True,
                # "api_type": "baichuan",
                # "model_client_cls": "CustomOpenAIClient",
            }
        ]

        config_list_baichuan = [
            {
                # Choose your model name.
                "model": "Baichuan4",
                # You need to provide your API key here.
                "api_key": "sk-b9911fafe7f5e2d96dc6be3f38a7710e",
                "base_url": "https://api.baichuan-ai.com/v1",
                "stream": True,
                # "api_type": "baichuan",
                # "model_client_cls": "CustomOpenAIClient",
            }
        ]

        assistant = AssistantAgent(
            "assistant",
            llm_config={
                "config_list": config_list_claude,
            },
        )

        user_proxy = UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,
            },
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            max_consecutive_auto_reply=1,
        )

        # @user_proxy.register_for_execution()
        # @assistant.register_for_llm(name="get_traffic", description="Get the current traffic in a given location.")
        # def apreprocessa(location: str) -> str:
        #     return "Absolutely cloudy and rainy"

        # @user_proxy.register_for_execution()
        # @assistant.register_for_llm(name="get_weather", description="Get the current weather in a given location.")
        # def preprocess(location: str) -> str:
        #     return "Absolutely cloudy and rainy"

        assistant.register_model_client(model_client_cls=CustomOpenAIClient)

        user_proxy.initiate_chat(
            assistant,
            # message="What's the weather in Toronto?",
            message="介绍一下特朗普",
        )

        return ""

    def autogen_runv3(self):
        # 打印语言默认编码
        print(f"defaultencoding--{sys.getdefaultencoding()}")
        # 打印系统配置的编码
        print(f"filesystemencoding--{sys.getfilesystemencoding()}")

        # 最后尝试打印中文
        print("中文")
        env = os.environ.copy()
        env['encoding'] = 'utf-8'

        IOStream.set_global_default(AISNSIOStream("我是参数"))

        config_list_claude = [
            {
                # Choose your model name.
                "model": "glm-4",
                # You need to provide your API key here.
                "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "stream": True,
                "api_type": "ChatGLM",
                "model_client_cls": "CustomOpenAIClient",
            }
        ]

        config_list_zhipu = [
            {
                # Choose your model name.
                "model": "glm-4",
                # You need to provide your API key here.
                "api_key": "7381c942a00d9419873da0f978afa822.TCmepxaLAPIV7pO7",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "stream": True,
                # "api_type": "baichuan",
                # "model_client_cls": "CustomOpenAIClient",
            }
        ]

        config_list_baichuan = [
            {
                # Choose your model name.
                "model": "Baichuan4",
                # You need to provide your API key here.
                "api_key": "sk-b9911fafe7f5e2d96dc6be3f38a7710e",
                "base_url": "https://api.baichuan-ai.com/v1",
                "stream": True,
                # "api_type": "baichuan",
                # "model_client_cls": "CustomOpenAIClient",
            }
        ]

        assistant = AssistantAgent(
            "assistant",
            llm_config={
                "config_list": config_list_claude,
            },
        )

        user_proxy = UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": "coding",
                "use_docker": False,
            },
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            max_consecutive_auto_reply=1,
        )

        # @user_proxy.register_for_execution()
        # @assistant.register_for_llm(name="get_traffic", description="Get the current traffic in a given location.")
        # def apreprocessa(location: str) -> str:
        #     return "Absolutely cloudy and rainy"

        # @user_proxy.register_for_execution()
        # @assistant.register_for_llm(name="get_weather", description="Get the current weather in a given location.")
        # def preprocess(location: str) -> str:
        #     return "Absolutely cloudy and rainy"

        assistant.register_model_client(model_client_cls=CustomOpenAIClient)
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        user_proxy.initiate_chat(
            assistant,
            message="What is the weather in Qinyang?",
            clear_history=True,
            cache=None
        )


class AgentGroup:
    def __init__(self, agent_group_cfg):
        self.agent_group_cfg = agent_group_cfg
        self.name = agent_group_cfg.name
        self.current_selected_agent = None
        self.plugin_name = ""
        self.km_path = ""
        self.embedding_model_name = ""
        self.agent_commander_id = agent_group_cfg.agentcommander
        self.agent_id_list = agent_group_cfg.agents.split(",") if agent_group_cfg.agents else None
        self.agent_list_to_run_task = {}
        self.task_list_to_run = []
        self.task_id = ""
        self.speaker = None

    def show_group_select_agent_title(self):
        output = self.speaker.answer_cache
        if output:
            topic = ""
            content = output
            memo = self.speaker.memo
            # 定义前缀
            prefix = "Agent Manager select the next agent:"

            agent_userid = memo[len(prefix):].strip()  # strip() 去掉前后空格

            selected_agent_cfg = query_AgentCfg(user_id=agent_userid)
            if selected_agent_cfg:
                modelname = selected_agent_cfg.name + " Powered by (" + selected_agent_cfg.defaultmodel + ")"
            else:
                modelname = agent_userid

            add_AgentTaskMulti(self.task_id, topic, content, modelname, self.agent_group_cfg.group_id, False)

        self.speaker.commit_and_refresh()
        self.speaker.show_group_select_agent_title()

    def give_it_plugin(self, plugin_name):
        self.plugin_name = plugin_name

    def give_it_km(self, km_path, embedding_model_name):
        self.km_path = km_path
        self.embedding_model_name = embedding_model_name

    def give_it_speaker(self, speaker):
        self.speaker = speaker

    def start_chat(self, messages, agent_list_to_run_task, browser_page=None, task_id=""):
        test_flag = False
        self.task_id = task_id
        speaker = self.speaker
        IOStream.set_global_default(AISNSIOStream(speaker))

        agent_id_list = self.agent_id_list
        agent_list = []
        agent_dict = {}

        agent_manager_cfg = query_AgentCfg(user_id=self.agent_commander_id)

        for agent_id in agent_id_list:
            agent_cfg = query_AgentCfg(user_id=agent_id)
            default_llm_full_name = agent_cfg.defaultmodel
            default_role = agent_cfg.defaultrole

            llm_full_name = agent_cfg.defaultmodel
            llm_connector_name = llm_full_name.split(":")[0]
            llm_model_type = llm_full_name.split(":")[1]
            llm_connector_plugin = global_plugin_list[llm_connector_name]

            llm_config = self.format_llm_config(llm_connector_plugin, llm_model_type)

            assist_agent = AssistantAgent(
                name=agent_cfg.name,
                human_input_mode="NEVER",
                system_message=agent_cfg.prompt,
                llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同
            )

            assist_agent.agent_cfg = agent_cfg
            assist_agent.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

            agent=assist_agent

            agent_list.append(agent)
            agent_dict[agent_id] = agent

        # *1.Admin 使用内置的*****
        agent_human_admin = Agent(
            agent_cfg=None,
            chat_in_group=True,
            name=lt("Agent_Human_Admin", "Agent_Human_Admin"),
            human_input_mode="ALWAYS",
            silent=True,
            system_message="You are a human administrator. Your role is to review all code written by the Engineer before execution. Ensure that the code meets the required standards and conforms to the approved plan.",
            code_execution_config=False,
            # description="An attentive HUMAN user who can answer questions about the task and perform tasks such as running Python code or inputting command line commands at a Linux terminal and reporting back the execution results."
        )

        agent_list.append(agent_human_admin)

        # *2.代码执行器，使用一个内置的就行了，不用使用专门的Agent对象*********
        executor = Agent(
            agent_cfg=None,
            chat_in_group=True,
            name="Executor",
            # silent=True,
            system_message="You are the Executor. Execute the code provided by the Engineer only after Admin approval and report the results.",
            human_input_mode="NEVER",
            code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")},
        )

        agent_list.append(executor)

        groupchat = GroupChat(
            # agents=[user_proxy, engineer, scientist, planner, executor, critic],
            admin_name=lt("Agent_Human_Admin", "Agent_Human_Admin"),
            agents=agent_list,
            messages=[],
            max_round=50,
            # send_introductions=True#we set the description of the agents to help the Group Chat Manager select the next agent. This only helps the Group Chat Manager, however, does not help the participating agents to know about each other. Sometimes it is useful have each agent introduce themselves to other agents in the group chat. This can be done by setting the send_introductions=True
        )
        # 7.使用群主的大模型，后面再考虑，manager就是选择下一用户的管理者，是由它背后的大模型来决定的，使用群主的llm配置以及界面上的大模型切换
        llm_full_name = agent_manager_cfg.defaultmodel
        llm_connector_name = llm_full_name.split(":")[0]
        llm_model_type = llm_full_name.split(":")[1]
        llm_connector_plugin = global_plugin_list[llm_connector_name]

        llm_config = self.format_llm_config(llm_connector_plugin, llm_model_type)

        agent_manager = AgentManager(
            agent_manager_cfg=agent_manager_cfg,
            agent_group_cfg=self.agent_group_cfg,
            agent_group=self,
            name="Group_Head",
            groupchat=groupchat,
            human_input_mode="ALWAYS",
            llm_config={"cache_seed": None, "config_list": [llm_config]},  # 注意格式和openai不同

        )
        # agent_commander = GroupChatManager(group_chat)

        if llm_connector_plugin.connection_mode == "OpenAI":
            pass

        elif llm_connector_plugin.connection_mode == "OpenAI-compatible":
            pass
            # agent_commander.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        elif llm_connector_plugin.connection_mode == "OpenAI-customize":
            agent_manager.register_model_client(model_client_cls=OpenAICustomizeLLMClient)


        elif llm_connector_plugin.connection_mode == "OpenAI-customize-v2":
            agent_manager.register_model_client(model_client_cls=OpenAICustomizeV2LLMClient)


        elif llm_connector_plugin.connection_mode == "SparkAI":
            agent_manager.register_model_client(model_client_cls=SparkAI)

        elif llm_connector_plugin.connection_mode == "Anthropic":
            agent_manager.register_model_client(model_client_cls=AnthropicClient)

        elif llm_connector_plugin.connection_mode == "groq":
            pass
        else:
            agent_manager.register_model_client(model_client_cls=CustomizeClient)

        message = messages[-1]["content"]
        agent_manager.register_model_client(model_client_cls=OpenAICompatibleLLMClient)
        agent_human_admin.initiate_chat(
            agent_manager,
            message=message,
        )
        # agent_commander.register_model_client(model_client_cls=OpenAICompatibleLLMClient)

        answer = "The task is done."
        return answer

    def format_llm_config(self, llm=None, model_type=""):
        if not llm:
            llm = self.llm_connector_plugin
        if not model_type:
            model_type = self.llm_model_type
        config = llm.get_config()
        connection_mode = llm.connection_mode

        if config.get("custom_params", False) == False:
            llm_config = {
                "model": model_type if model_type else config.get("model", ""),
                "api_key": config.get("api_key", ""),
                "cache_seed": None,
                "seed": None,  # 42
                "temperature": config.get("temperature", 0),
                "stream": config.get("stream", False)
            }
        else:
            json_string = config.get("parameters", "")
            custom_config = json.loads(json_string)
            llm_config = {
                "model": model_type if model_type else custom_config.get("model", ""),
                "api_key": config.get("api_key", ""),
                "cache_seed": None,
                "seed": None,  # 42
                "temperature": custom_config.get("temperature", 0),
                "stream": custom_config.get("stream", False)
            }

        if connection_mode == "OpenAI-compatible":
            base_url = config.get("url", "").replace('/chat/completions', '')
            llm_config["base_url"] = base_url
            llm_config["model_client_cls"] = "OpenAICompatibleLLMClient"

        elif connection_mode == "OpenAI-customize":
            base_url = config.get("url", "").replace('/chat/completions', '')
            llm_config["base_url"] = base_url
            llm_config["model_client_cls"] = "OpenAICustomizeLLMClient"

        elif connection_mode == "OpenAI-customize-v2":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "OpenAICustomizeV2LLMClient"

        elif connection_mode == "SparkAI":
            llm_config = llm.get_config()
            # llm_config["model_client"] = llm.get_model()
            llm_config.pop("plugin_name", None)
            llm_config.pop("custom_params", None)
            llm_config.pop("description", None)
            llm_config.pop("parameters", None)
            llm_config["model_client_cls"] = "SparkAI"

        elif connection_mode == "Anthropic":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "AnthropicClient"

        elif connection_mode == "Customize":
            llm_config = llm.get_config()
            llm_config["model_client_cls"] = "CustomizeClient"

        elif connection_mode == "groq":
            llm_config = llm.get_config()
            llm_config["api_type"] = "groq"
            # llm_config["model_client_cls"] = "GroqClient"

        return llm_config


class CustomOpenAIClient:
    """Follows the Client protocol and wraps the OpenAI client."""

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self.model = config["model"]
        customllm_kwargs = set(inspect.getfullargspec(OpenAI.__init__).kwonlyargs)
        # customllm_kwargs = set(inspect.getfullargspec(Anthropic.__init__).kwonlyargs)
        filter_dict = {k: v for k, v in config.items() if k in customllm_kwargs}
        self._client = OpenAI(**filter_dict)
        self._oai_client = self._client
        self._last_tooluse_status = {}
        global global_browser_page
        self.browser_page = global_browser_page

    def message_retrieval(
            self, response: Union[ChatCompletion, Completion]
    ) -> Union[List[str], List[ChatCompletionMessage]]:
        """Retrieve the messages from the response."""
        choices = response.choices
        if isinstance(response, Completion):
            return [choice.text for choice in choices]  # type: ignore [union-attr]

        if TOOL_ENABLED:
            return [  # type: ignore [return-value]
                (
                    choice.message  # type: ignore [union-attr]
                    if choice.message.function_call is not None or choice.message.tool_calls is not None  # type: ignore [union-attr]
                    else choice.message.content
                )  # type: ignore [union-attr]
                for choice in choices
            ]
        else:
            return [  # type: ignore [return-value]
                choice.message if choice.message.function_call is not None else choice.message.content  # type: ignore [union-attr]
                for choice in choices
            ]

    def create(self, params: Dict[str, Any]) -> ChatCompletion:
        """Create a completion for a given config using openai's client.

        Args:
            client: The openai client.
            params: The params for the completion.

        Returns:
            The completion.
        """
        iostream = IOStream.get_default()

        completions: Completions = self._oai_client.chat.completions if "messages" in params else self._oai_client.completions  # type: ignore [attr-defined]
        # If streaming is enabled and has messages, then iterate over the chunks of the response.
        if params.get("stream", False) and "messages" in params:
            response_contents = [""] * params.get("n", 1)
            finish_reasons = [""] * params.get("n", 1)
            completion_tokens = 0

            # Set the terminal text color to green
            iostream.print("\033[32m", end="")

            # Prepare for potential function call
            full_function_call: Optional[Dict[str, Any]] = None
            full_tool_calls: Optional[List[Optional[Dict[str, Any]]]] = None

            # Send the chat completion request to OpenAI's API and process the response in chunks
            params.pop("model_client_cls")
            chunks = ""
            browser_page = self.browser_page
            for chunk in completions.create(**params):
                if chunk.choices:
                    for choice in chunk.choices:
                        content = choice.delta.content

                        print("cjrv2 get the content:", content)

                        chunks += content
                        tchunks = format_string_for_run_javascript(chunks)

                        if browser_page != None:
                            self.speaker.runJavaScript('tchunks=`' + tchunks + '`')
                            self.speaker.runJavaScript('show_response_msg(tchunks)')

                        tool_calls_chunks = choice.delta.tool_calls
                        finish_reasons[choice.index] = choice.finish_reason

                        # todo: remove this after function calls are removed from the API
                        # the code should work regardless of whether function calls are removed or not, but test_chat_functions_stream should fail
                        # begin block
                        function_call_chunk = (
                            choice.delta.function_call if hasattr(choice.delta, "function_call") else None
                        )
                        # Handle function call
                        if function_call_chunk:
                            # Handle function call
                            if function_call_chunk:
                                full_function_call, completion_tokens = OpenAIWrapper._update_function_call_from_chunk(
                                    function_call_chunk, full_function_call, completion_tokens
                                )
                            if not content:
                                continue
                        # end block

                        # Handle tool calls
                        if tool_calls_chunks:
                            for tool_calls_chunk in tool_calls_chunks:
                                # the current tool call to be reconstructed
                                ix = tool_calls_chunk.index
                                if full_tool_calls is None:
                                    full_tool_calls = []
                                if ix >= len(full_tool_calls):
                                    # in case ix is not sequential
                                    full_tool_calls = full_tool_calls + [None] * (ix - len(full_tool_calls) + 1)

                                full_tool_calls[ix], completion_tokens = OpenAIWrapper._update_tool_calls_from_chunk(
                                    tool_calls_chunk, full_tool_calls[ix], completion_tokens
                                )
                                if not content:
                                    continue

                        # End handle tool calls

                        # If content is present, print it to the terminal and update response variables
                        if content is not None:
                            iostream.print(content, end="", flush=True)
                            response_contents[choice.index] += content
                            completion_tokens += 1
                        else:
                            # iostream.print()
                            pass
            if browser_page != None:
                self.speaker.runJavaScript('updatemaincontent()')
            # Reset the terminal text color
            iostream.print("\033[0m\n")

            # Prepare the final ChatCompletion object based on the accumulated data
            model = chunk.model.replace("gpt-35", "gpt-3.5")  # hack for Azure API
            prompt_tokens = 10  # chatglm没有这个参数，所以要把它先写死
            # prompt_tokens = count_token(params["messages"], model)
            response = ChatCompletion(
                id=chunk.id,
                model=chunk.model,
                created=chunk.created,
                object="chat.completion",
                choices=[],
                usage=CompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
            )
            for i in range(len(response_contents)):
                if OPENAIVERSION >= "1.5":  # pragma: no cover
                    # OpenAI versions 1.5.0 and above
                    choice = Choice(
                        index=i,
                        finish_reason=finish_reasons[i],
                        message=ChatCompletionMessage(
                            role="assistant",
                            content=response_contents[i],
                            function_call=full_function_call,
                            tool_calls=full_tool_calls,
                        ),
                        logprobs=None,
                    )
                else:
                    # OpenAI versions below 1.5.0
                    choice = Choice(  # type: ignore [call-arg]
                        index=i,
                        finish_reason=finish_reasons[i],
                        message=ChatCompletionMessage(
                            role="assistant",
                            content=response_contents[i],
                            function_call=full_function_call,
                            tool_calls=full_tool_calls,
                        ),
                    )

                response.choices.append(choice)
        else:
            # If streaming is not enabled, send a regular chat completion request
            params = params.copy()
            params["stream"] = False
            response = completions.create(**params)

        return response

    def cost(self, response: Union[ChatCompletion, Completion]) -> float:
        """Calculate the cost of the response."""
        model = response.model
        if model not in OAI_PRICE1K:
            # TODO: add logging to warn that the model is not found
            logger.debug(f"Model {model} is not found. The cost will be 0.", exc_info=True)
            return 0

        n_input_tokens = response.usage.prompt_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        n_output_tokens = response.usage.completion_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        if n_output_tokens is None:
            n_output_tokens = 0
        tmp_price1K = OAI_PRICE1K[model]
        # First value is input token rate, second value is output token rate
        if isinstance(tmp_price1K, tuple):
            return (tmp_price1K[0] * n_input_tokens + tmp_price1K[1] * n_output_tokens) / 1000  # type: ignore [no-any-return]
        return tmp_price1K * (n_input_tokens + n_output_tokens) / 1000  # type: ignore [operator]

    @staticmethod
    def get_usage(response: Union[ChatCompletion, Completion]) -> Dict:
        return {
            "prompt_tokens": response.usage.prompt_tokens if response.usage is not None else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage is not None else 0,
            "total_tokens": response.usage.total_tokens if response.usage is not None else 0,
            "cost": response.cost if hasattr(response, "cost") else 0,
            "model": response.model,
        }
