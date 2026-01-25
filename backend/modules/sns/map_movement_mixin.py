"""
地图和移动相关的 Mixin
包含位置管理、移动、导航、路线规划等功能
"""
import logging
import json
import random
import math
from typing import List, Dict, Optional
from geopy.distance import distance
from geopy.point import Point
from geographiclib.geodesic import Geodesic

logger = logging.getLogger(__name__)


class MapMovementMixin:
    """地图和移动相关功能"""

    def go_around(self):
        """随机移动到附近位置"""
        radius = 500  # 半径，单位为米
        # 初始化当前位置和上一个位置
        current_position = Point(self.aichatcfg_record.current_position[1], self.aichatcfg_record.current_position[0])
        last_position = Point(self.aichatcfg_record.last_position[1], self.aichatcfg_record.last_position[0])

        # 如果位置相同，跳过象限排除
        if current_position == last_position:
            excluded_quadrant = None
        else:
            # 确定上一个位置相对于当前坐标的象限
            last_lon_diff = last_position.longitude - current_position.longitude
            last_lat_diff = last_position.latitude - current_position.latitude

            # 根据差值计算上个位置所在的象限
            if last_lon_diff > 0 and last_lat_diff > 0:
                excluded_quadrant = 1  # 第一象限
            elif last_lon_diff < 0 and last_lat_diff > 0:
                excluded_quadrant = 2  # 第二象限
            elif last_lon_diff < 0 and last_lat_diff < 0:
                excluded_quadrant = 3  # 第三象限
            else:
                excluded_quadrant = 4  # 第四象限

        def generate_random_point(excluded_quadrant):
            while True:
                bearing = random.uniform(0, 360)
                candidate_position = distance(meters=radius).destination(current_position, bearing)

                if abs(candidate_position.latitude) >= 90:
                    candidate_position = Point(89.999 if candidate_position.latitude > 0 else -89.999,
                                               current_position.longitude)

                candidate_position = Point(candidate_position.latitude,
                                           (candidate_position.longitude + 180) % 360 - 180)

                if excluded_quadrant is None:  # 跳过象限排除
                    return candidate_position

                lon_diff = candidate_position.longitude - current_position.longitude
                lat_diff = candidate_position.latitude - current_position.latitude

                if lon_diff > 0 and lat_diff > 0:
                    candidate_quadrant = 1
                elif lon_diff < 0 and lat_diff > 0:
                    candidate_quadrant = 2
                elif lon_diff < 0 and lat_diff < 0:
                    candidate_quadrant = 3
                else:
                    candidate_quadrant = 4

                if candidate_quadrant != excluded_quadrant:
                    return candidate_position

        target_position = generate_random_point(excluded_quadrant)
        self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
        self.aichatcfg_record.current_position = [target_position.longitude, target_position.latitude]

        new_pos = self.aichatcfg_record.current_position
        self.ui_adapter.update_current_location(new_pos)

        result = f"在附近逛逛，从{self.current_place}移动到了{new_pos}附近"
        return result

    def move_ahead(self, current_position, target_position, target_place):
        """向目标位置前进"""
        try:
            # 计算当前位置和目标位置之间的距离
            current_point = Point(current_position[1], current_position[0])
            target_point = Point(target_position[1], target_position[0])
            total_distance = distance(current_point, target_point).meters

            # 设定每次移动的距离（例如 500 米）
            step_distance = 500

            # 如果总距离小于等于步进距离，直接移动到目标
            if total_distance <= step_distance:
                self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
                self.aichatcfg_record.current_position = target_position
                self.current_place = target_place
                result = f"成功到达目标地点: {target_place}"
                self.target_position = None
                self.target_place = ""
            else:
                # 计算移动的方向（方位角）
                bearing = Geodesic.WGS84.Inverse(current_point.latitude, current_point.longitude,
                                                 target_point.latitude, target_point.longitude)['azi1']

                # 使用 geopy 移动指定距离
                new_point = distance(meters=step_distance).destination(current_point, bearing)

                # 更新位置
                self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
                self.aichatcfg_record.current_position = [new_point.longitude, new_point.latitude]

                # 计算剩余距离
                remaining_distance = total_distance - step_distance
                result = f"向 {target_place} 前进了 {step_distance} 米，剩余距离: {remaining_distance:.0f} 米"

            # 更新UI
            new_pos = self.aichatcfg_record.current_position
            self.ui_adapter.update_current_location(new_pos)

            return result

        except Exception as e:
            logger.error(f"移动失败: {e}")
            return f"移动失败: {str(e)}"

    def move_by_route(self):
        """按照路线移动"""
        try:
            if not self.route_position_list or len(self.route_position_list) == 0:
                return "路线已完成或未设置路线"

            # 获取下一个路径点
            next_position = self.route_position_list.pop(0)

            # 更新位置
            self.aichatcfg_record.last_position = self.aichatcfg_record.current_position
            self.aichatcfg_record.current_position = next_position

            # 更新UI
            self.ui_adapter.update_current_location(next_position)

            remaining_points = len(self.route_position_list)
            if remaining_points == 0:
                self.move_by_route_flag = False
                result = f"已到达目的地: {self.route_target_place}"
                self.route_target_place = ""
            else:
                result = f"沿路线前进，剩余 {remaining_points} 个路径点"

            return result

        except Exception as e:
            logger.error(f"按路线移动失败: {e}")
            return f"按路线移动失败: {str(e)}"

    def get_guidance(self):
        """获取导航指引"""
        try:
            if not self.target_position:
                return "未设置目标位置，无法提供导航"

            current_point = Point(self.aichatcfg_record.current_position[1], 
                                 self.aichatcfg_record.current_position[0])
            target_point = Point(self.target_position[1], self.target_position[0])

            # 计算距离和方位
            geod_result = Geodesic.WGS84.Inverse(
                current_point.latitude, current_point.longitude,
                target_point.latitude, target_point.longitude
            )

            distance_m = geod_result['s12']  # 距离（米）
            bearing = geod_result['azi1']  # 方位角

            # 转换方位角为方向描述
            direction = self._bearing_to_direction(bearing)

            result = f"导航提示: 目标 {self.target_place} 在您的{direction}方向，距离约 {distance_m:.0f} 米"
            return result

        except Exception as e:
            logger.error(f"获取导航失败: {e}")
            return f"获取导航失败: {str(e)}"

    def _bearing_to_direction(self, bearing):
        """将方位角转换为方向描述"""
        if bearing < 0:
            bearing += 360

        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = int((bearing + 22.5) / 45) % 8
        return directions[index]

    def calculate_distance(self, pos1, pos2):
        """计算两点之间的距离（米）"""
        try:
            point1 = Point(pos1[1], pos1[0])
            point2 = Point(pos2[1], pos2[0])
            return distance(point1, point2).meters
        except Exception as e:
            logger.error(f"计算距离失败: {e}")
            return 0

    def update_current_location(self, position):
        """更新当前位置"""
        try:
            self.aichatcfg_record.current_position = position
            self.ui_adapter.update_current_location(position)
            logger.info(f"位置已更新: {position}")
        except Exception as e:
            logger.error(f"更新位置失败: {e}")

    def set_target_location(self, position, place_name):
        """设置目标位置"""
        self.target_position = position
        self.target_place = place_name
        logger.info(f"目标位置已设置: {place_name} at {position}")

    def clear_target_location(self):
        """清除目标位置"""
        self.target_position = None
        self.target_place = ""
        logger.info("目标位置已清除")
