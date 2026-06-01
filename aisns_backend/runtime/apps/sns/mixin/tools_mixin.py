from sqlalchemy.orm import Session
from db.models.aisns import AISnsCfg
from runtime.apps.sns.map_task_manager import MapTaskManager
from runtime.apps.sns.js_task_manager import JsTaskManager
from runtime.apps.sns.xmpp_client import XMPPClientManager
from runtime.modules.agent.agent_manager import agent_manager
from runtime.shared.websocket_manager import manager as websocket_manager

# *********
import os
import math
# Mainly used for sending attachments
import asyncio
import zipfile
import shutil
import time

import logging

import re
from runtime.shared import debug_info

log = logging.getLogger(__name__)
from db.DBFactory import (query_AgentCfg, add_AIChatMessages, get_prompt_by_title, query_function_mng,
                          add_function_mng, add_map_visit, get_key_value,
                          update_map_trade, add_map_trade, query_single_map_trade, update_AISnsCfg_by_user_id, update_AISnsCfg_map, query_AISnsCfg_map, add_mcp_mng, query_mcp_mng,
                          delete_map_preset_msg, query_map_preset_msg_all, add_map_preset_msg, query_AISnsCfg_map_setting)

from runtime.i18n import lt
from enum import Enum
import json
import logging
import requests
import geopy.distance
from geopy.distance import distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic
import random

from runtime.shared.utils import robust_json_loads

logger = logging.getLogger(__name__)


class ToolsMixin:

    _WEB_SERVICE_TIMEOUT = (3, 15)
    _WEB_SERVICE_MAX_RETRIES = 3
    _WEB_SERVICE_RETRY_BACKOFF = (0.5, 1.0, 2.0)

    def _get_ai_sns_server_base(self):
        try:
            from db.DBFactory import query_SystemCfg
            cfg = query_SystemCfg(is_delete=False)
            v = getattr(cfg, 'ai_sns_server', None)
            v = (v or '').strip()
            return v.rstrip('/') if v else ''
        except Exception:
            return ''

    def use_service(self, action_str, instrunction):
        asyncio.create_task(
            self.ask_agent_to_use_service(
                action_str,
                human_objective_to_achieve=instrunction,
            )
        )

    def get_service_list(self):
        url = f"{self._get_ai_sns_server_base()}/api/get_service_list/"

        pos = self.aisns_cfg_record.current_position

        try:
            lng_val = float(pos[0])
            lat_val = float(pos[1])
            pos_key = f"{round(lng_val, 6)},{round(lat_val, 6)}"
        except Exception:
            pos_key = ""

        try:
            cached_key = getattr(self, "_cached_service_list_pos_key", None)
            cached_value = getattr(self, "_cached_service_list_value", None)
            if pos_key and cached_key == pos_key and cached_value is not None:
                return cached_value
        except Exception:
            pass

        params = {
            "lng": pos[0],
            "lat": pos[1]
        }
        service_list = self.http_request(url, params)

        if isinstance(service_list, list) and pos_key:
            try:
                setattr(self, "_cached_service_list_pos_key", pos_key)
                setattr(self, "_cached_service_list_value", service_list)
            except Exception:
                pass
        return service_list

    def update_service_list(self):
        url = f"{self._get_ai_sns_server_base()}/api/get_service"
        params = {
            "lng": self.aisns_cfg_record.current_position[0],
            "lat": self.aisns_cfg_record.current_position[1]
        }
        # people={
        #     "name":"Same",
        #     "position":[121.121,23.4554]
        # }
        service_list = self.http_request(url, params)

        return service_list

    async def ask_agent_to_use_service(self, objective_to_achieve, human_objective_to_achieve=""):
        service_list = json.dumps(self.get_service_list(), indent=4, ensure_ascii=False)
        objective_to_achieve = f"{human_objective_to_achieve}{objective_to_achieve}"
        role_prompt = get_prompt_by_title("__ask_agent_use_service__") or ""
        role_prompt = role_prompt.replace("__service_list__", service_list)
        # role_prompt = role_prompt.replace("__objective_to_achieve__", objective_to_achieve)


        question = (get_prompt_by_title("__ask_agent_use_service_question__") or "").strip()
        if not question:
            question = (
                "The current objective is: __objective__. Based on the task requirements, "
                "select the appropriate services. If no suitable service is available, return an empty list."
            )
        question = question.replace("__objective__", objective_to_achieve)

        # Memory recall: inject past service usage experience
        try:
            from runtime.apps.sns.memory.memory_types import MemoryType
            from runtime.apps.sns.memory.memory_config import MemoryConfig
            mm = getattr(self, "memory_manager", None)
            if mm and MemoryConfig.ENABLED:
                memory_section = mm.get_memory_prompt_section(
                    query=objective_to_achieve,
                    memory_types=[MemoryType.EPISODE.value, MemoryType.OBSERVATION.value],
                    max_results=3,
                    max_chars=800,
                )
                if memory_section:
                    question += "\n\n" + memory_section
        except Exception as _mem_err:
            logger.warning("Memory recall failed for service selection: %s", _mem_err)

        self.command_status = "ask_agent_to_use_service"
        await self.ask_agent_and_get_instruction(question, role_prompt)

    def on_ask_agent_to_use_service_return(self, content):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._handle_service_selection_and_call_async(content))
        except RuntimeError:
            asyncio.run(self._handle_service_selection_and_call_async(content))


    def parse_content_to_call_service(self, content):
        try:
            url, method, params = self._parse_service_call_payload(content)
            response = self.call_service(url, method, **params)
            return response
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error processing content: {e}")
            return None

    def _parse_service_call_payload(self, content):
        data = robust_json_loads(content, default=None)
        if not isinstance(data, dict):
            raise ValueError("Invalid service selection payload (not a JSON object)")

        url = data.get("address")
        method = (data.get("method") or "get").lower()
        params = data.get("parameter")
        if params is None:
            params = data.get("Parameter", {})
        if params is None:
            params = {}

        if not isinstance(url, str) or not url.startswith("http"):
            raise ValueError("Invalid 'address' value. Must be a valid URL.")

        if method not in ["get", "post", "put", "delete", "patch"]:
            raise ValueError("Invalid 'method' value. Supported methods: get, post, put, delete, patch")

        if not isinstance(params, dict):
            raise ValueError("Invalid 'parameter' value. Must be a JSON object.")

        return url, method, params

    async def _handle_service_selection_and_call_async(self, content: str):
        url = ""
        method = ""
        params = {}
        try:
            try:
                url, method, params = self._parse_service_call_payload(content)
            except Exception as e:
                msg = f"Invalid service payload: {e}"
                try:
                    self.show_alert_on_map(msg)
                except Exception:
                    pass
                try:
                    self.taskmng.add_process_info_to_list(f"system: {msg}")
                except Exception:
                    pass
                try:
                    self.write_thinking_process_to_pane("Service selection parse failed", msg)
                except Exception:
                    pass
                try:
                    self.show_status_on_map("idle")
                except Exception:
                    pass
                try:
                    if bool(getattr(self, "_human_command_inflight", False)) and hasattr(self, "_maybe_finish_human_command_if_idle"):
                        self._maybe_finish_human_command_if_idle(ask_content="")
                    else:
                        asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=""))
                except Exception:
                    pass
                return

            try:
                self.command_status = ""
            except Exception:
                pass

            response_text = await self._call_web_service_with_retry_async(url, method, params)
            if response_text is not None:
                try:
                    self.handle_service_called_result(response_text)
                except Exception as e:
                    msg = f"Service call returned but handling failed: {e}"
                    try:
                        self.show_alert_on_map(msg, is_error=True)
                    except Exception:
                        pass
                    try:
                        self.taskmng.add_process_info_to_list(f"system: {msg}")
                    except Exception:
                        pass
                    try:
                        self.write_thinking_process_to_pane("Service call handling failed", msg)
                    except Exception:
                        pass
                    try:
                        self.show_status_on_map("idle")
                    except Exception:
                        pass
                    try:
                        if bool(getattr(self, "_human_command_inflight", False)) and hasattr(self, "_maybe_finish_human_command_if_idle"):
                            self._maybe_finish_human_command_if_idle(ask_content="")
                        else:
                            asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=""))
                    except Exception:
                        pass
                return

            final_msg = f"Web service call failed after retries: {method.upper()} {url}"
            try:
                self.show_alert_on_map(final_msg, is_error=True)
            except Exception:
                pass
            try:
                self.taskmng.add_process_info_to_list(f"system: {final_msg}")
            except Exception:
                pass
            try:
                self.write_thinking_process_to_pane("Web service call failed", final_msg)
            except Exception:
                pass
            try:
                self.show_status_on_map("idle")
            except Exception:
                pass

            try:
                if bool(getattr(self, "_human_command_inflight", False)) and hasattr(self, "_maybe_finish_human_command_if_idle"):
                    self._maybe_finish_human_command_if_idle(ask_content="")
                else:
                    asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=""))
            except Exception:
                pass
        except Exception as e:
            msg = f"Unexpected error while handling service selection: {e}"
            try:
                self.show_alert_on_map(msg, is_error=True)
            except Exception:
                pass
            try:
                self.taskmng.add_process_info_to_list(f"system: {msg}")
            except Exception:
                pass
            try:
                self.write_thinking_process_to_pane("Service selection failed", msg)
            except Exception:
                pass
            try:
                self.show_status_on_map("idle")
            except Exception:
                pass
            try:
                if bool(getattr(self, "_human_command_inflight", False)) and hasattr(self, "_maybe_finish_human_command_if_idle"):
                    self._maybe_finish_human_command_if_idle(ask_content="")
                else:
                    asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=""))
            except Exception:
                pass

    async def _call_web_service_with_retry_async(self, url: str, method: str, params: dict):
        max_retries = int(getattr(self, "_WEB_SERVICE_MAX_RETRIES", self._WEB_SERVICE_MAX_RETRIES) or 3)
        backoffs = getattr(self, "_WEB_SERVICE_RETRY_BACKOFF", self._WEB_SERVICE_RETRY_BACKOFF) or (0.5, 1.0, 2.0)
        timeout = getattr(self, "_WEB_SERVICE_TIMEOUT", self._WEB_SERVICE_TIMEOUT) or (3, 15)

        try:
            self.show_status_on_map("using-tool")
        except Exception:
            pass

        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                def _do_request():
                    m = (method or "get").lower()
                    if m in ["get", "delete"]:
                        resp = requests.request(m, url, params=params, timeout=timeout)
                    else:
                        resp = requests.request(m, url, json=params, timeout=timeout)
                    resp.raise_for_status()
                    return resp.text

                if hasattr(asyncio, "to_thread"):
                    result = await asyncio.to_thread(_do_request)
                else:
                    loop = asyncio.get_running_loop()
                    result = await loop.run_in_executor(None, _do_request)
                try:
                    self.show_status_on_map("idle")
                except Exception:
                    pass
                return result
            except requests.exceptions.RequestException as e:
                last_err = e
                msg = f"Web service call failed (attempt {attempt}/{max_retries}): {e}"
                try:
                    self.taskmng.add_process_info_to_list(f"system: {msg}")
                except Exception:
                    pass
                try:
                    self.write_thinking_process_to_pane("Web service call failed", msg)
                except Exception:
                    pass
            except Exception as e:
                last_err = e
                msg = f"Web service call error (attempt {attempt}/{max_retries}): {e}"
                try:
                    self.taskmng.add_process_info_to_list(f"system: {msg}")
                except Exception:
                    pass
                try:
                    self.write_thinking_process_to_pane("Web service call error", msg)
                except Exception:
                    pass

            if attempt < max_retries:
                try:
                    backoff = float(backoffs[attempt - 1]) if attempt - 1 < len(backoffs) else float(backoffs[-1])
                except Exception:
                    backoff = 0.5
                await asyncio.sleep(max(0.0, backoff))

        try:
            self.show_status_on_map("idle")
        except Exception:
            pass

        try:
            if last_err is not None:
                logger.warning("Web service call failed after retries: %s %s, last_err=%s", method, url, last_err)
        except Exception:
            pass
        return None

    def call_service(self, url, method, **params):
        try:
            timeout = getattr(self, "_WEB_SERVICE_TIMEOUT", None) or (3, 15)
            if method == "get":
                response = requests.get(url, params=params, timeout=timeout)
            elif method == "post":
                response = requests.post(url, json=params, timeout=timeout)  # Use 'data' for post
            elif method == "put":
                response = requests.put(url, json=params, timeout=timeout)
            elif method == "delete":
                response = requests.delete(url, params=params, timeout=timeout)
            elif method == "patch":
                response = requests.patch(url, json=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            self.handle_service_called_result(response.text)  # Assuming the response is JSON, parse and return it
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error calling service: {e}")
            return None  # Or handle the error as needed, e.g., retry, log, etc.
        except ValueError as e:
            print(f"Error calling service: {e}")
            return None

    def run_agent_delivery_prompt_sync(
        self,
        user_prompt: str,
        chat_history_str: str,
        *,
        conversation_suffix: str = "trade_delivery",
    ):
        """Schedule generate_text_with_agent_prompt as an async task; return the Task."""
        try:
            return asyncio.create_task(
                self.generate_text_with_agent_prompt(
                    user_prompt,
                    chat_history_str,
                    conversation_suffix=conversation_suffix,
                )
            )
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(
                    self.generate_text_with_agent_prompt(
                        user_prompt,
                        chat_history_str,
                        conversation_suffix=conversation_suffix,
                    )
                )
            finally:
                loop.close()

    # Friendly notice returned to the buyer when delivery cannot be completed.
    DELIVERY_FALLBACK_MESSAGE = "Delivery encountered an issue. Please wait for follow-up handling."

    # Neutral system prompt used ONLY for the post-payment delivery turn. This
    # deliberately overrides the SNS "select communication target -> JSON"
    # persona so the agent fulfils the seller's delivery instruction instead of
    # leaking a candidate-selection JSON when a tool/skill fails.
    _DELIVERY_SYSTEM_PROMPT = (
        "You are fulfilling a post-payment delivery task on behalf of the seller. "
        "The buyer has already paid, so you must deliver what the seller promised. "
        "Follow the seller's delivery instruction below exactly and reply with ONLY "
        "the delivered content (for example: the generated image URL, the requested "
        "text, or a file link). Do NOT output candidate-selection JSON, sales pitches, "
        "role/persona JSON, or any extra commentary. "
        "If you cannot complete the delivery (for example a tool or skill fails), reply "
        "with exactly this sentence and nothing else: " + DELIVERY_FALLBACK_MESSAGE
    )

    async def generate_text_with_agent_prompt(
        self,
        user_prompt: str,
        chat_history_str: str,
        *,
        conversation_suffix: str = "trade_delivery",
    ) -> str:
        """Send user prompt + chat history to the agent LLM and return the reply.

        For local agents, use_tools=True allows the LLM to invoke any
        configured tool based on the prompt. For remote agents, the
        prompt is forwarded via the remote RPC path automatically by
        AgentAdapter.chat.

        Delivery is best-effort and must never break or hang the engine: any
        failure (missing agent, LLM/RPC error, empty output) is converted into a
        friendly fallback notice so the buyer always receives a reply.
        """
        try:
            agent = self.get_agent_for_current_chat()
        except Exception as e:
            log.error("trade delivery: failed to resolve agent: %s", e, exc_info=True)
            return self.DELIVERY_FALLBACK_MESSAGE

        if agent is None:
            log.error("trade delivery: agent not configured for current user")
            return self.DELIVERY_FALLBACK_MESSAGE

        prompt = f"{user_prompt}\n\n## Chat history\n{chat_history_str}"

        # Temporarily force a neutral delivery system prompt. Both local agents
        # (AgentInstance.get_system_prompt) and remote agents
        # (AgentAdapter._remote_send_message) read role_config['system_prompt'],
        # so this single override covers both agent types.
        role_config = getattr(agent, "role_config", None)
        overrode_prompt = False
        original_system_prompt = None
        if isinstance(role_config, dict):
            original_system_prompt = role_config.get("system_prompt")
            role_config["system_prompt"] = self._DELIVERY_SYSTEM_PROMPT
            overrode_prompt = True

        try:
            reply = await self.chat_with_agent(
                prompt,
                conversation_suffix=conversation_suffix,
                use_tools=True,
                use_memory=False,
                use_knowledge_base=False,
                agent=agent,
            )
        except Exception as e:
            log.error("trade delivery: agent chat failed: %s", e, exc_info=True)
            return self.DELIVERY_FALLBACK_MESSAGE
        finally:
            if overrode_prompt:
                try:
                    if original_system_prompt is None:
                        role_config.pop("system_prompt", None)
                    else:
                        role_config["system_prompt"] = original_system_prompt
                except Exception:
                    pass

        reply_text = (reply or "").strip()
        if not reply_text:
            log.warning("trade delivery: agent returned empty reply, using fallback notice")
            return self.DELIVERY_FALLBACK_MESSAGE
        return reply_text

    def handle_service_called_result(self, response_text):
        action_result = response_text
        self.action_result = action_result
        self.taskmng.add_process_info_to_list(f"system: Web service called and returned: {action_result}")
        self.write_task_process_to_pane(action_result + "\n\n")
        self.show_alert_on_map(action_result)
        ask_content = ""
        try:
            if bool(getattr(self, "_human_command_inflight", False)) and hasattr(self, "_maybe_finish_human_command_if_idle"):
                self._maybe_finish_human_command_if_idle(ask_content=ask_content)
            else:
                asyncio.create_task(self.taskmng.process_task(action="process_activity", ask_content=ask_content))
        except Exception:
            pass

