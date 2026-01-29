"""
资源和状态管理相关的 Mixin
包含生命值、体力、金钱、经验值等资源管理功能
"""
import logging
import json
from typing import List, Dict, Optional
from db.DBFactory import update_AiChatCfg_map

logger = logging.getLogger(__name__)


class ResourceManagementMixin:
    """资源和状态管理相关功能"""

    def load_all_user_data(self):
        """从数据库加载所有用户数据"""
        try:
            # 加载位置信息
            self.current_place = self.aichatcfg_record.current_place or ""
            self.current_position = self.aichatcfg_record.current_position or []
            self.last_position = self.aichatcfg_record.last_position or []

            # 加载资源数据
            self.life_point = self.aichatcfg_record.life_point or 100
            self.energy_point = self.aichatcfg_record.energy_point or 100
            self.move_point = self.aichatcfg_record.move_point or 100
            self.exp_point = self.aichatcfg_record.exp_point or 0
            self.iq_point = self.aichatcfg_record.iq_point or 60
            self.money = self.aichatcfg_record.money or 1000
            self.credit = self.aichatcfg_record.credit or 100
            self.level = self.aichatcfg_record.level or 1

            # 更新UI显示
            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info("User data loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load user data: {e}")

    def save_all_user_data(self):
        """保存所有用户数据到数据库"""
        try:
            update_data = {
                "current_place": self.current_place,
                "current_position": json.dumps(self.current_position, ensure_ascii=False),
                "last_position": json.dumps(self.last_position, ensure_ascii=False),
                "life_point": self.life_point,
                "energy_point": self.energy_point,
                "move_point": self.move_point,
                "exp_point": self.exp_point,
                "iq_point": self.iq_point,
                "money": self.money,
                "credit": self.credit,
                "level": self.level
            }

            update_AiChatCfg_map(**update_data)
            logger.info("User data saved successfully")

        except Exception as e:
            logger.error(f"Failed to save user data: {e}")

    def decline_life(self):
        """降低生命值"""
        try:
            self.life_point = max(0, self.life_point - 10)
            self.aichatcfg_record.life_point = self.life_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Life point decreased to {self.life_point}")

            # 检查是否需要触发生命值过低事件
            if self.life_point <= 20:
                logger.warning("Life point is critically low!")
                # 可以在这里触发相关事件

        except Exception as e:
            logger.error(f"Failed to decline life: {e}")

    def increase_life(self, amount=10):
        """增加生命值"""
        try:
            self.life_point = min(100, self.life_point + amount)
            self.aichatcfg_record.life_point = self.life_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Life point increased to {self.life_point}")

        except Exception as e:
            logger.error(f"Failed to increase life: {e}")

    def decline_energy(self):
        """降低体力值"""
        try:
            self.energy_point = max(0, self.energy_point - 10)
            self.aichatcfg_record.energy_point = self.energy_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Energy point decreased to {self.energy_point}")

            # 检查是否需要触发体力过低事件
            if self.energy_point <= 20:
                logger.warning("Energy point is critically low!")

        except Exception as e:
            logger.error(f"Failed to decline energy: {e}")

    def increase_energy(self, amount=10):
        """增加体力值"""
        try:
            self.energy_point = min(100, self.energy_point + amount)
            self.aichatcfg_record.energy_point = self.energy_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Energy point increased to {self.energy_point}")

        except Exception as e:
            logger.error(f"Failed to increase energy: {e}")

    def decline_move_point(self, amount=5):
        """降低行动力"""
        try:
            self.move_point = max(0, self.move_point - amount)
            self.aichatcfg_record.move_point = self.move_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Move point decreased to {self.move_point}")

        except Exception as e:
            logger.error(f"Failed to decline move point: {e}")

    def increase_move_point(self, amount=5):
        """增加行动力"""
        try:
            self.move_point = min(100, self.move_point + amount)
            self.aichatcfg_record.move_point = self.move_point

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Move point increased to {self.move_point}")

        except Exception as e:
            logger.error(f"Failed to increase move point: {e}")

    def add_money(self, amount):
        """增加金钱"""
        try:
            self.money += amount
            self.aichatcfg_record.money = self.money


            logger.info(f"Money increased by {amount} to {self.money}")
            return {"status": "success", "new_balance": self.money}

        except Exception as e:
            logger.error(f"Failed to add money: {e}")
            return {"status": "error", "message": str(e)}

    def spend_money(self, amount):
        """花费金钱"""
        try:
            if self.money < amount:
                logger.warning(f"Insufficient funds. Required: {amount}, Available: {self.money}")
                return {"status": "error", "message": "Insufficient funds"}

            self.money -= amount
            self.aichatcfg_record.money = self.money


            logger.info(f"Money decreased by {amount} to {self.money}")
            return {"status": "success", "new_balance": self.money}

        except Exception as e:
            logger.error(f"Failed to spend money: {e}")
            return {"status": "error", "message": str(e)}

    def add_exp(self, amount):
        """增加经验值"""
        try:
            self.exp_point += amount
            self.aichatcfg_record.exp_point = self.exp_point

            # 检查是否升级
            level_up_threshold = self.level * 100
            if self.exp_point >= level_up_threshold:
                self.level_up()

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()

            logger.info(f"Experience increased by {amount} to {self.exp_point}")

        except Exception as e:
            logger.error(f"Failed to add experience: {e}")

    def level_up(self):
        """升级"""
        try:
            self.level += 1
            self.aichatcfg_record.level = self.level

            # 升级奖励
            self.life_point = 100
            self.energy_point = 100
            self.move_point = 100
            self.iq_point = min(100, self.iq_point + 5)

            if hasattr(self, 'ui_adapter'):
                self.update_resource_display()
                self.show_level_up_notification(self.level)

            logger.info(f"Level up! New level: {self.level}")

        except Exception as e:
            logger.error(f"Failed to level up: {e}")

    def get_resource_status(self):
        """获取当前资源状态"""
        return {
            "life_point": self.life_point,
            "energy_point": self.energy_point,
            "move_point": self.move_point,
            "exp_point": self.exp_point,
            "iq_point": self.iq_point,
            "money": self.money,
            "credit": self.credit,
            "level": self.level
        }

    def format_resource_display(self):
        """格式化资源显示"""
        return f"""
* 资金值: {self.money:.2f}元
* 生命值: {self.life_point}%
* 体力值: {self.energy_point}%
* 行动力: {self.move_point}%
* 经验值: {self.exp_point}
* 智力值: {self.iq_point}
* 信用值: {self.credit}
* 等级: {self.level}
        """.strip()
