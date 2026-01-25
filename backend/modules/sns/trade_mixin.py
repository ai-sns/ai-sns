"""
交易和工具管理相关的 Mixin
包含工具买卖、技能交换、交易流程管理等功能
"""
import logging
import json
import re
import os
import zipfile
import time
from typing import List, Dict, Optional
from util import generate_random_id
from db.DBFactory import (add_map_trade, update_map_trade, query_single_map_trade,
                          add_map_tool, query_function_mng, query_single_tool)

logger = logging.getLogger(__name__)


class TradeMixin:
    """交易和工具管理相关功能"""

    def tool_trade_buy(self, tool) -> None:
        """
        发起购买工具的交易
        
        Args:
            tool: 要购买的工具信息字典
        """
        try:
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

            # 发送交易请求消息
            message = f"AISNS_INT_001_TN_{trade_id}_MN_{id}"
            asyncio.create_task(self.talk_to_a_people(message, nation_id, account, nick_name))

            # 记录交易
            trade_type = "B"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(
                trade_id=trade_id,
                trade_type=trade_type,
                title=title,
                detail=detail,
                trade_with_name=trade_with_name,
                trade_with_account=trade_with_account
            )

            logger.info(f"Tool trade initiated: {name} (ID: {trade_id})")

        except Exception as e:
            logger.error(f"Tool trade buy error: {str(e)}")

    def tool_trade_sell(self, trade_id, tool) -> None:
        """
        发起出售工具的交易
        
        Args:
            trade_id: 交易ID
            tool: 要出售的工具信息字典
        """
        try:
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

            # 发送交易消息
            message = f"AISNS_INT_002_TN_{trade_id}_SYS_CONTENT_SENDING_FILE"
            asyncio.create_task(self.talk_to_a_people(message, nation_id, account, nick_name))

            # 发送文件
            to_jid = account
            link = self.send_file_bg(file_path, to_jid)

            # 记录交易
            trade_type = "S"
            title = name
            trade_with_name = nick_name
            trade_with_account = account
            add_map_trade(
                trade_id=trade_id,
                trade_type=trade_type,
                title=title,
                detail=detail,
                link=link,
                trade_with_name=trade_with_name,
                trade_with_account=trade_with_account
            )

            logger.info(f"Tool trade sell initiated: {name} (ID: {trade_id})")

        except Exception as e:
            logger.error(f"Tool trade sell error: {str(e)}")

    def tool_trade_pay(self, trade_id, account) -> None:
        """
        支付交易款项
        
        Args:
            trade_id: 交易ID
            account: 收款账号
        """
        try:
            message = f"AISNS_INT_003_TN_{trade_id}"
            asyncio.create_task(self.send_message_to_jid(account, message))

            # 处理支付
            self.handle_as_coin("001", account)

            # 更新交易状态
            update_map_trade(trade_id, status=1)

            logger.info(f"Payment sent for trade: {trade_id}")

        except Exception as e:
            logger.error(f"Tool trade pay error: {str(e)}")

    def tool_trade_paid(self, trade_id) -> None:
        """
        标记交易为已支付
        
        Args:
            trade_id: 交易ID
        """
        try:
            update_map_trade(trade_id, status=1)
            logger.info(f"Trade marked as paid: {trade_id}")
        except Exception as e:
            logger.error(f"Tool trade paid error: {str(e)}")

    def tool_trade_inquiry(self, tool):
        """
        发起工具询价
        
        Args:
            tool: 工具信息字典
        """
        try:
            current_talk_people = self.current_talk_people
            account = current_talk_people["account"]

            tool_json = json.dumps(tool, ensure_ascii=False)
            message = f"AISNS_INT_005_TOOL_INQUIRY_START{tool_json}AISNS_INT_005_TOOL_INQUIRY_END"

            asyncio.create_task(self.send_message_to_jid(account, message))
            logger.info(f"Tool inquiry sent: {tool.get('name', 'Unknown')}")

        except Exception as e:
            logger.error(f"Tool trade inquiry error: {str(e)}")

    def tool_trade_send_bargain_for_buyer(self, content):
        """
        买家发送议价内容
        
        Args:
            content: 议价内容
        """
        try:
            current_talk_people = self.current_talk_people
            account = current_talk_people["account"]

            message = f"AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_START{content}AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_END"
            asyncio.create_task(self.send_message_to_jid(account, message))

            logger.info("Buyer bargain sent")

        except Exception as e:
            logger.error(f"Buyer bargain error: {str(e)}")

    def tool_trade_send_bargain_for_seller(self, content):
        """
        卖家发送议价内容
        
        Args:
            content: 议价内容
        """
        try:
            current_talk_people = self.current_talk_people
            account = current_talk_people["account"]

            message = f"AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_START{content}AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_END"
            asyncio.create_task(self.send_message_to_jid(account, message))

            logger.info("Seller bargain sent")

        except Exception as e:
            logger.error(f"Seller bargain error: {str(e)}")

    def get_tool_list_in_message(self, msg):
        """从消息中提取工具列表"""
        pattern = r'AISNS_INT_001_TOOL_DETAIL_SHOW_START(.*?)AISNS_INT_001_TOOL_DETAIL_SHOW_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_tool_inquiry_in_message(self, msg):
        """从消息中提取工具询价信息"""
        pattern = r'AISNS_INT_005_TOOL_INQUIRY_START(.*?)AISNS_INT_005_TOOL_INQUIRY_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_buyer_bargain_in_message(self, msg):
        """从消息中提取买家议价信息"""
        pattern = r'AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_START(.*?)AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_seller_bargain_in_message(self, msg):
        """从消息中提取卖家议价信息"""
        pattern = r'AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_START(.*?)AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_tool_confirm_in_message(self, msg, prefix="AISNS_INT_003_TN_"):
        """从消息中提取工具确认信息"""
        if msg.startswith(prefix):
            return msg[len(prefix):]
        return ""

    def send_skill(self, skill_id, skill_name, account, skill_type="function"):
        """
        发送技能给对方
        
        Args:
            skill_id: 技能ID
            skill_name: 技能名称
            account: 接收者账号
            skill_type: 技能类型
        """
        try:
            if skill_type == "function":
                self.create_skill_cfg(skill_id, skill_name)
                file_path = self.create_skill_zip(skill_name)
                self.send_file_bg(file_path, account)

            logger.info(f"Skill sent: {skill_name} to {account}")

        except Exception as e:
            logger.error(f"Send skill error: {str(e)}")

    def create_skill_cfg(self, skill_id, skill_name):
        """
        创建技能配置文件
        
        Args:
            skill_id: 技能ID
            skill_name: 技能名称
        
        Returns:
            str: 配置文件路径
        """
        try:
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
            with open(cfg_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(skill_cfg, json_file, ensure_ascii=False, indent=4)

            return cfg_file_path

        except Exception as e:
            logger.error(f"Create skill config error: {str(e)}")
            raise

    def create_skill_zip(self, skill_name):
        """
        创建技能压缩包
        
        Args:
            skill_name: 技能名称
        
        Returns:
            str: 压缩文件路径
        """
        try:
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
                zipf.write(python_file_path, os.path.basename(python_file_path))
                zipf.write(cfg_file_path, os.path.basename(cfg_file_path))

            return file_path

        except Exception as e:
            logger.error(f"Create skill zip error: {str(e)}")
            raise

    def check_skill(self, msg):
        """
        检查消息中是否包含技能文件
        
        Args:
            msg: 消息内容
        """
        try:
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

        except Exception as e:
            logger.error(f"Check skill error: {str(e)}")

    def received_skill(self, msg):
        """
        接收技能文件
        
        Args:
            msg: 包含技能文件链接的消息
        """
        try:
            url = self.get_url_from_msg(msg)
            file_name = os.path.basename(url)
            file_without_extension = os.path.splitext(file_name)[0]
            file_extension = os.path.splitext(file_name)[1]
            file_path = os.path.join(os.getcwd(), "download", file_name)

            if os.path.exists(file_path):
                current_timestamp = str(time.time()).replace('.', '')
                file_name = file_without_extension + current_timestamp + file_extension
                file_path = os.path.join(os.getcwd(), "download", file_name)

            self.download_file(url, file_path)
            self.skill_install(file_path)

            logger.info(f"Skill received and installed: {file_name}")

        except Exception as e:
            logger.error(f"Received skill error: {str(e)}")

    def get_tool_list(self):
        """获取工具列表"""
        # 这个方法的实现在原文件中,这里返回示例结构
        return []

    def handle_as_coin(self, amount, account):
        """处理虚拟货币交易"""
        # 实现虚拟货币交易逻辑
        pass

    def send_file_bg(self, file_path, to_jid):
        """后台发送文件"""
        # 实现文件发送逻辑
        pass

    def download_file(self, url, file_path):
        """下载文件"""
        # 实现文件下载逻辑
        pass

    def skill_install(self, file_path):
        """安装技能"""
        # 实现技能安装逻辑
        pass

    def get_url_from_msg(self, msg):
        """从消息中提取URL"""
        # 实现URL提取逻辑
        return msg
