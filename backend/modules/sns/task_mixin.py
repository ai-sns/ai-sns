"""
任务管理相关的 Mixin
包含任务的启动、停止、暂停、恢复等核心任务管理功能
"""
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)


class TaskMixin:
    """任务管理相关功能"""

    async def start(self):
        """
        Start the AI social engine
        This is the backend-compatible version of the start() method
        """
        try:
            logger.info("Starting AI Social Engine...")

            self.started_flag = True
            self.map_task_status = ""  # Reset to empty string to allow start_task() to execute

            # Initialize ability list
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

            logger.info("AI Social Engine started successfully")
            return {"status": "success", "message": "AI Social Engine started"}

        except Exception as e:
            logger.error(f"Failed to start AI Social Engine: {e}")
            return {"status": "error", "message": str(e)}

    async def stop(self):
        """
        Stop the AI social engine
        This is the backend-compatible version of the stop() method
        """
        try:
            logger.info("Stopping AI Social Engine...")

            # Set flags to stop ongoing processes
            self.started_flag = False
            self.stopping_ai_process_flag = True

            # Cancel any running tasks
            if self.task_runner:
                self.task_runner.cancel()
                self.task_runner = None

            logger.info("AI Social Engine stopped successfully")
            return {"status": "success", "message": "AI Social Engine stopped"}

        except Exception as e:
            logger.error(f"Failed to stop AI Social Engine: {e}")
            return {"status": "error", "message": str(e)}

    def pause_task(self):
        """暂停任务"""
        try:
            self.pause_flag = True
            logger.info("Task paused")
            return {"status": "success", "message": "Task paused"}
        except Exception as e:
            logger.error(f"Failed to pause task: {e}")
            return {"status": "error", "message": str(e)}

    def resume_task(self):
        """恢复任务"""
        try:
            self.pause_flag = False
            logger.info("Task resumed")
            return {"status": "success", "message": "Task resumed"}
        except Exception as e:
            logger.error(f"Failed to resume task: {e}")
            return {"status": "error", "message": str(e)}

    async def start_task(self):
        """启动任务执行"""
        try:
            if self.map_task_status:
                logger.warning(f"Task already running with status: {self.map_task_status}")
                return {"status": "warning", "message": "Task already running"}

            logger.info("Starting task execution...")
            # 任务执行逻辑
            await self.taskmng.run_task()

            return {"status": "success", "message": "Task started"}
        except Exception as e:
            logger.error(f"Failed to start task: {e}")
            return {"status": "error", "message": str(e)}

    def get_task_status(self):
        """获取当前任务状态"""
        return {
            "started": self.started_flag,
            "status": self.map_task_status,
            "paused": self.pause_flag,
            "stopping": self.stopping_ai_process_flag
        }
