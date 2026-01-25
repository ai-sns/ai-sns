"""
AI Social Engine Adapter for Backend - Refactored
This module provides a backend-compatible adapter for the AI social engine
重构后的版本使用 Mixin 模式将功能模块化
"""
from sqlalchemy.orm import Session
from backend.database.models.chat import AiChatCfg
from backend.modules.sns.map_task_manager import MapTaskManager
from backend.modules.sns.js_task_manager import JsTaskManager
from backend.modules.sns.ui_adapter import UIAdapter
from backend.modules.sns.xmpp_client import XMPPClientManager
from backend.modules.agent.agent_manager import agent_manager
from backend.shared.websocket_manager import manager as websocket_manager

import os
import logging
import asyncio
from enum import Enum
from typing import List, Dict, Optional

# Import all Mixins
from .task_mixin import TaskMixin
from .map_movement_mixin import MapMovementMixin
from .communication_mixin import CommunicationMixin
from .agent_interaction_mixin import AgentInteractionMixin
from .resource_management_mixin import ResourceManagementMixin
from .trade_mixin import TradeMixin
from .ui_display_mixin import UIDisplayMixin
from .data_query_mixin import DataQueryMixin
from .event_handler_mixin import EventHandlerMixin

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """交易类型枚举"""
    SKILL_EXCHANGE = 1
    TOKEN_PURCHASE = 2


class AiChatCfgManager:
    """
    管理AiChatCfg数据库记录的类
    支持通过属性访问获取最新值，通过属性赋值更新数据库记录
    """

    def __init__(self, user_id=None):
        """
        初始化AiChatCfgManager
        
        Args:
            user_id (str, optional): 用户ID，默认为None，使用第一条记录
        """
        from db.DBFactory import query_AiChatCfg_map_setting, query_AiChatCfg_map
        
        self._user_id = user_id
        self._record = None
        self._callbacks = []  # 存储回调函数列表
        self._load_record()

    def connect(self, callback):
        """连接回调函数，当属性更新时调用"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def disconnect(self, callback):
        """断开回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit_property_updated(self, property_name):
        """触发属性更新回调"""
        for callback in self._callbacks:
            try:
                callback(property_name)
            except Exception as e:
                logger.error(f"Error in property update callback: {e}")

    def _load_record(self):
        """加载数据库记录"""
        from db.DBFactory import query_AiChatCfg_map_setting, query_AiChatCfg_map
        
        if self._user_id:
            self._record = query_AiChatCfg_map_setting(user_id=self._user_id)
        else:
            self._record = query_AiChatCfg_map()

    def _refresh_record(self):
        """刷新记录以获取最新数据"""
        self._load_record()

    def __getattr__(self, name):
        """当访问不存在的属性时调用此方法"""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        self._refresh_record()

        if self._record is None:
            raise AttributeError(f"No record found in database")

        # 特殊处理 current_position 属性
        if name == 'current_position':
            import json
            raw_position = getattr(self._record, name, None)
            return self._parse_position_data_impl(raw_position)

        # 特殊处理其他位置相关属性
        other_position_fields = ['last_position', 'home_position', 'route_start', 'route_end', 'route_current_position']
        if name in other_position_fields:
            import json
            raw_value = getattr(self._record, name, None)
            if raw_value:
                try:
                    return json.loads(raw_value)
                except (json.JSONDecodeError, TypeError):
                    return raw_value
            else:
                return None

        if hasattr(self._record, name):
            return getattr(self._record, name)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """当设置属性时调用此方法"""
        from db.DBFactory import update_AiChatCfg_by_user_id, update_AiChatCfg_map
        import json
        
        # 处理内部属性
        if name.startswith('_') or name in ['user_id']:
            super().__setattr__(name, value)
            return

        # 需要特殊处理的字段列表
        position_fields = ['current_position', 'last_position', 'home_position',
                           'route_start', 'route_end', 'route_current_position']

        # 如果是位置相关字段且值为list或dict类型，则转换为字符串
        if name in position_fields and isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)

        # 对于其他属性，更新数据库记录
        if '_record' in self.__dict__ and self._record is not None:
            if self._user_id:
                update_AiChatCfg_by_user_id(self._user_id, **{name: value})
            else:
                update_AiChatCfg_map(**{name: value})

            setattr(self._record, name, value)
            self._emit_property_updated(name)
        else:
            super().__setattr__(name, value)

    def _parse_position_data_impl(self, position_data):
        """解析位置数据"""
        import json

        if not position_data:
            return []

        if isinstance(position_data, list):
            if len(position_data) >= 2:
                return [float(position_data[0]), float(position_data[1])]
            else:
                return []

        if isinstance(position_data, str):
            try:
                parsed_data = json.loads(position_data)

                if isinstance(parsed_data, dict):
                    lat = float(parsed_data.get("lat", 0))
                    lng = float(parsed_data.get("lng", 0))
                    return [lng, lat]

                elif isinstance(parsed_data, list) and len(parsed_data) >= 2:
                    return [float(parsed_data[0]), float(parsed_data[1])]

            except json.JSONDecodeError:
                return []

        return []


class AISocialEngine(
    TaskMixin,
    MapMovementMixin,
    CommunicationMixin,
    AgentInteractionMixin,
    ResourceManagementMixin,
    TradeMixin,
    UIDisplayMixin,
    DataQueryMixin,
    EventHandlerMixin
):
    """
    Backend adapter for AI Social Engine
    重构后使用 Mixin 组合模式，将不同功能分离到不同的 Mixin 类中
    """

    def __init__(self, db: Session):
        """初始化 AI Social Engine"""
        self.db = db
        self.started_flag = False
        self.map_task_status = ""
        self.current_place = None
        self.process_list = []
        self.ability_list = []
        self.task_runner = None
        
        # 初始化任务管理器
        self.taskmng_js = JsTaskManager(self)
        self.taskmng = MapTaskManager(self)
        self.ui_adapter = UIAdapter(self)

        # 初始化 XMPP 客户端管理器
        self.xmpp_manager = XMPPClientManager.get_instance()

        # 从数据库加载配置
        self.config = self.db.query(AiChatCfg).filter(
            AiChatCfg.is_delete == False
        ).first()

        self.ai_chat_cfg = self.config

        # 初始化配置管理器
        self.aichatcfg_record = AiChatCfgManager()
        self.aichatcfg_record.connect(self.handle_aichatcfg_property_updated)

        # 初始化状态标志
        self.human_take_over = False
        self.human_instruction = ""
        self.stopping_ai_process_flag = False
        self.pause_flag = False
        self.agent_replying_flag = False
        
        self.conversation_id = ""
        self.messages = []
        self.messages_command = []
        self.page_index = 0
        self.map_mode = 'org'

        self.personList = ["My_Agent", "wangwang"]
        self.agent = None
        self.kmselectedList = []
        self.pluginselectedList = []
        self.current_received_msg = ""

        self.is_browser_page_loaded = False
        self.first_event = None
        self.first_reply = ""

        # plugin相关
        self.chess_role = None
        self.chinese_chess_role = None
        self.system_role_prompt = "You are a helpful assistant who provides concise and accurate information."

        # 初始化全局变量
        self.user_map_setting = None
        self.current_place = ""
        self.current_position = []
        self.last_position = []

        self.target_position = None
        self.target_place = ""
        self.move_by_route_flag = False
        self.route_position_list = []
        
        # 能力列表
        self.ability_list = [
            {
                "function_name": "【activity_find_people_from_list_to_talk】",
                "function_description": "从人员名单中查找合适的人进行沟通，当你需要别人的帮助，需要别人给你指引的时候可以选择该功能，筛选人员不允许分多步骤筛选",
                "status": "enabled"
            },
            {
                "function_name": "【activity_find_place_from_list_to_move】",
                "function_description": "从地点列表中查找合适的地方作为目的地，当你需要去某个地方的时候可以选择该功能，筛选地方不允许分多步骤筛选",
                "status": "enabled"
            },
            {
                "function_name": "【activity_find_tool_from_list_to_use】",
                "function_description": "使用该功能可以从工具列表中查找合适的工具来调用系统服务、使用AI技能，解决其他功能解决不了的问题。筛选工具不允许分多步骤筛选。",
                "status": "enabled"
            }
        ]
        
        self.skill_list = []
        logger.info("AISocialEngine initialized successfully")

    async def async_init(self):
        """异步初始化方法"""
        logger.info("Async initializing AISocialEngine...")
        
        self.command_status = ""
        self.required_skills = []
        self.available_skills = []
        self.route_flag = False
        self.token_balance = 0

        self.taskmng_js = JsTaskManager(self)
        self.taskmng = MapTaskManager(self)

        self.people_list_to_ask_for_help = []
        self.current_talk_people = None
        self.asking_people_for_help_flag = False
        self.talk_history = {}
        self.current_talk_history = []
        self.people_talking_list = []

        self.thinking_step_index = 0
        self.process_step_index = 0
        self.place_selected = None
        
        # 配置参数
        self.max_tool_usage = 4
        self.max_people_comm = 4
        self.max_rounds_per_person = 6
        self.max_place_arrived = 3
        self.min_place_move_score = 80
        self.search_radius = 10000
        
        self.place_arrived_count = {}
        self.wait_for_trade_download_flag = False
        self.wait_for_trade_download_trade_id = ""
        self.command_list = []
        self.current_command_index = -1
        self.updown_message_index = -1
        self.temp_index = 0
        self.temp_index_2 = 0
        self.current_action = ""
        self.action_result = ""
        self.current_task_list = ""
        self.current_ongoing_content = ""

        # 初始化资源
        self.life_point = 100
        self.energy_point = 100
        self.move_point = 100
        self.exp_point = 0
        self.iq_point = 60
        self.money = 1000
        self.credit = 100
        self.level = 1

        self.talk_type = ""
        self.route_total_distance = 0
        self.route_move_distance = 0
        self.route_target_place = ""
        self.route_target_position = None
        self.map_task_status = ""
        self.current_trade_price = -1
        self.wait_for_send_good = False
        
        # 加载用户数据
        self.load_all_user_data()
        
        logger.info("AISocialEngine async initialization complete")

    async def _send_to_frontend(self, tab_type, content, section=None):
        """
        发送内容到前端指定的页签
        
        Args:
            tab_type: 页签类型 ('think', 'process', 'resource', 'map', 'trade', 'chat')
            content: 要发送的内容
            section: 可选的章节/部分标识
        """
        try:
            from backend.shared.websocket_manager import manager as websocket_manager
            import json
            
            # 构建消息
            message = {
                "type": "tab_update",
                "tab": tab_type,
                "content": content
            }
            
            # 如果有section参数，添加到消息中
            if section:
                message["section"] = section
            
            # 通过WebSocket发送到前端
            await websocket_manager.broadcast(message)
            logger.debug(f"Sent content to frontend tab '{tab_type}': {content[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to send content to frontend tab '{tab_type}': {e}")

    def __repr__(self):
        """对象的字符串表示"""
        return f"<AISocialEngine(started={self.started_flag}, place={self.current_place})>"
