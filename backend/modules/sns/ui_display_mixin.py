"""
UI 和显示相关的 Mixin
包含状态显示、资源显示、地图更新等 UI 相关功能
"""
import logging
import json
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class UIDisplayMixin:
    """UI 和显示相关功能"""

    def show_status_on_map(self, status):
        """
        在地图上显示状态
        
        Args:
            status: 状态字符串 (thinking/moving/talking等)
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.show_status(status)
            logger.debug(f"Status shown on map: {status}")
        except Exception as e:
            logger.error(f"Failed to show status on map: {e}")

    def show_alert_on_map(self, message):
        """
        在地图上显示警告消息
        
        Args:
            message: 警告消息内容
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.show_alert(message)
            logger.debug(f"Alert shown on map: {message}")
        except Exception as e:
            logger.error(f"Failed to show alert on map: {e}")

    def write_on_going_process_to_pane(self, process_text):
        """
        将正在进行的过程写入面板
        
        Args:
            process_text: 过程描述文本
        """
        try:
            self.current_ongoing_content = process_text
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_ongoing_process(process_text)
            logger.debug(f"Ongoing process updated: {process_text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to write ongoing process: {e}")

    def write_task_process_to_pane(self, process_text):
        """
        将任务过程写入面板
        
        Args:
            process_text: 任务过程描述文本
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.append_task_process(process_text)
            logger.debug(f"Task process appended: {process_text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to write task process: {e}")

    def update_resource_display(self):
        """更新资源显示"""
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_resource_display()
            logger.debug("Resource display updated")
        except Exception as e:
            logger.error(f"Failed to update resource display: {e}")

    def update_map_charts(self):
        """更新地图图表"""
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_charts()
            logger.debug("Map charts updated")
        except Exception as e:
            logger.error(f"Failed to update map charts: {e}")

    def update_current_location_display(self, position):
        """
        更新当前位置显示
        
        Args:
            position: 位置坐标 [lng, lat]
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_current_location(position)
            logger.debug(f"Current location display updated: {position}")
        except Exception as e:
            logger.error(f"Failed to update location display: {e}")

    def clear_task_display(self):
        """清空任务显示"""
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.clear_task_display()
            logger.debug("Task display cleared")
        except Exception as e:
            logger.error(f"Failed to clear task display: {e}")

    def show_notification(self, title, message, notification_type="info"):
        """
        显示通知
        
        Args:
            title: 通知标题
            message: 通知消息
            notification_type: 通知类型 (info/warning/error/success)
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.show_notification(title, message, notification_type)
            logger.info(f"Notification shown: [{notification_type}] {title}: {message}")
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

    def update_people_list_display(self, people_list):
        """
        更新人员列表显示
        
        Args:
            people_list: 人员列表数据
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_people_list(people_list)
            logger.debug(f"People list updated with {len(people_list)} people")
        except Exception as e:
            logger.error(f"Failed to update people list display: {e}")

    def update_place_list_display(self, place_list):
        """
        更新地点列表显示
        
        Args:
            place_list: 地点列表数据
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_place_list(place_list)
            logger.debug(f"Place list updated with {len(place_list)} places")
        except Exception as e:
            logger.error(f"Failed to update place list display: {e}")

    def update_tool_list_display(self, tool_list):
        """
        更新工具列表显示
        
        Args:
            tool_list: 工具列表数据
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_tool_list(tool_list)
            logger.debug(f"Tool list updated with {len(tool_list)} tools")
        except Exception as e:
            logger.error(f"Failed to update tool list display: {e}")

    def show_conversation_window(self, person_info):
        """
        显示对话窗口
        
        Args:
            person_info: 对话人员信息
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.show_conversation_window(person_info)
            logger.debug(f"Conversation window shown for {person_info.get('nick_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to show conversation window: {e}")

    def close_conversation_window(self):
        """关闭对话窗口"""
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.close_conversation_window()
            logger.debug("Conversation window closed")
        except Exception as e:
            logger.error(f"Failed to close conversation window: {e}")

    def update_task_progress_bar(self, progress_percentage):
        """
        更新任务进度条
        
        Args:
            progress_percentage: 进度百分比 (0-100)
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.update_progress_bar(progress_percentage)
            logger.debug(f"Progress bar updated: {progress_percentage}%")
        except Exception as e:
            logger.error(f"Failed to update progress bar: {e}")

    def highlight_location_on_map(self, position, label=""):
        """
        在地图上高亮显示位置
        
        Args:
            position: 位置坐标 [lng, lat]
            label: 位置标签
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.highlight_location(position, label)
            logger.debug(f"Location highlighted on map: {position} - {label}")
        except Exception as e:
            logger.error(f"Failed to highlight location: {e}")

    def draw_route_on_map(self, route_positions, route_info=None):
        """
        在地图上绘制路线
        
        Args:
            route_positions: 路线位置列表 [[lng, lat], ...]
            route_info: 路线信息字典
        """
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.draw_route(route_positions, route_info)
            logger.debug(f"Route drawn on map with {len(route_positions)} points")
        except Exception as e:
            logger.error(f"Failed to draw route on map: {e}")

    def clear_map_highlights(self):
        """清除地图上的所有高亮标记"""
        try:
            if hasattr(self, 'ui_adapter'):
                self.ui_adapter.clear_highlights()
            logger.debug("Map highlights cleared")
        except Exception as e:
            logger.error(f"Failed to clear map highlights: {e}")
