"""
数据查询和列表管理相关的 Mixin
包含获取人员列表、地点列表、工具列表等数据查询功能
"""
import logging
import json
from typing import List, Dict, Optional
import geopy.distance
from db.DBFactory import query_tool_list

logger = logging.getLogger(__name__)


class DataQueryMixin:
    """数据查询和列表管理相关功能"""

    def get_people_list(self):
        """
        获取周围的人员列表
        
        Returns:
            list: 人员信息列表
        """
        try:
            # 这里应该从数据库或API获取人员列表
            # 暂时返回空列表作为示例
            people_list = []
            
            # 如果有当前位置,可以根据距离过滤
            if hasattr(self, 'search_radius') and self.current_position:
                # 实现基于位置的人员筛选逻辑
                pass
            
            logger.debug(f"Retrieved {len(people_list)} people")
            return people_list

        except Exception as e:
            logger.error(f"Failed to get people list: {e}")
            return []

    def get_place_list(self):
        """
        获取周围的地点列表
        
        Returns:
            list: 地点信息列表
        """
        try:
            # 这里应该从数据库或API获取地点列表
            place_list = []
            
            # 如果有当前位置,可以根据距离过滤
            if hasattr(self, 'search_radius') and self.current_position:
                # 实现基于位置的地点筛选逻辑
                pass
            
            logger.debug(f"Retrieved {len(place_list)} places")
            return place_list

        except Exception as e:
            logger.error(f"Failed to get place list: {e}")
            return []

    def get_tool_list(self):
        """
        获取可用的工具列表
        
        Returns:
            list: 工具信息列表
        """
        try:
            tool_list = query_tool_list()
            logger.debug(f"Retrieved {len(tool_list)} tools")
            return tool_list

        except Exception as e:
            logger.error(f"Failed to get tool list: {e}")
            return []

    def get_ability_list(self):
        """
        获取能力列表
        
        Returns:
            list: 能力信息列表
        """
        try:
            return self.ability_list if hasattr(self, 'ability_list') else []

        except Exception as e:
            logger.error(f"Failed to get ability list: {e}")
            return []

    def filter_people_by_distance(self, people_list, max_distance=None):
        """
        根据距离过滤人员列表
        
        Args:
            people_list: 人员列表
            max_distance: 最大距离(米),默认使用 search_radius
        
        Returns:
            list: 过滤后的人员列表
        """
        try:
            if not max_distance:
                max_distance = self.search_radius if hasattr(self, 'search_radius') else 10000

            if not self.current_position:
                return people_list

            current_pos = tuple(reversed(self.current_position))  # [lng, lat] -> (lat, lng)
            
            filtered_list = []
            for person in people_list:
                if 'location' in person:
                    person_pos = tuple(reversed(person['location']))
                    distance = geopy.distance.distance(current_pos, person_pos).meters
                    
                    if distance <= max_distance:
                        person['distance'] = distance
                        filtered_list.append(person)

            # 按距离排序
            filtered_list.sort(key=lambda x: x.get('distance', float('inf')))
            
            logger.debug(f"Filtered people list: {len(filtered_list)} within {max_distance}m")
            return filtered_list

        except Exception as e:
            logger.error(f"Failed to filter people by distance: {e}")
            return people_list

    def filter_places_by_distance(self, place_list, max_distance=None):
        """
        根据距离过滤地点列表
        
        Args:
            place_list: 地点列表
            max_distance: 最大距离(米),默认使用 search_radius
        
        Returns:
            list: 过滤后的地点列表
        """
        try:
            if not max_distance:
                max_distance = self.search_radius if hasattr(self, 'search_radius') else 10000

            if not self.current_position:
                return place_list

            current_pos = tuple(reversed(self.current_position))  # [lng, lat] -> (lat, lng)
            
            filtered_list = []
            for place in place_list:
                if 'position' in place:
                    place_pos = tuple(reversed(place['position']))
                    distance = geopy.distance.distance(current_pos, place_pos).meters
                    
                    if distance <= max_distance:
                        place['distance'] = distance
                        filtered_list.append(place)

            # 按距离排序
            filtered_list.sort(key=lambda x: x.get('distance', float('inf')))
            
            logger.debug(f"Filtered place list: {len(filtered_list)} within {max_distance}m")
            return filtered_list

        except Exception as e:
            logger.error(f"Failed to filter places by distance: {e}")
            return place_list

    def search_people_by_keyword(self, keyword):
        """
        根据关键词搜索人员
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            list: 匹配的人员列表
        """
        try:
            people_list = self.get_people_list()
            
            if not keyword:
                return people_list

            keyword_lower = keyword.lower()
            results = []
            
            for person in people_list:
                # 搜索名称、简介等字段
                if (keyword_lower in person.get('nick_name', '').lower() or
                    keyword_lower in person.get('profile', '').lower() or
                    keyword_lower in person.get('account', '').lower()):
                    results.append(person)

            logger.debug(f"People search for '{keyword}': {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Failed to search people: {e}")
            return []

    def search_places_by_keyword(self, keyword):
        """
        根据关键词搜索地点
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            list: 匹配的地点列表
        """
        try:
            place_list = self.get_place_list()
            
            if not keyword:
                return place_list

            keyword_lower = keyword.lower()
            results = []
            
            for place in place_list:
                # 搜索名称、描述等字段
                if (keyword_lower in place.get('name', '').lower() or
                    keyword_lower in place.get('description', '').lower() or
                    keyword_lower in place.get('category', '').lower()):
                    results.append(place)

            logger.debug(f"Place search for '{keyword}': {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Failed to search places: {e}")
            return []

    def search_tools_by_keyword(self, keyword):
        """
        根据关键词搜索工具
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            list: 匹配的工具列表
        """
        try:
            tool_list = self.get_tool_list()
            
            if not keyword:
                return tool_list

            keyword_lower = keyword.lower()
            results = []
            
            for tool in tool_list:
                # 搜索名称、描述等字段
                if (keyword_lower in tool.get('name', '').lower() or
                    keyword_lower in tool.get('description', '').lower() or
                    keyword_lower in tool.get('type', '').lower()):
                    results.append(tool)

            logger.debug(f"Tool search for '{keyword}': {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Failed to search tools: {e}")
            return []

    def get_nearby_resources(self, resource_type='all', max_distance=None):
        """
        获取附近的资源(人员、地点、工具等)
        
        Args:
            resource_type: 资源类型 ('people'/'places'/'all')
            max_distance: 最大距离(米)
        
        Returns:
            dict: 包含各类资源的字典
        """
        try:
            resources = {}

            if resource_type in ['people', 'all']:
                people_list = self.get_people_list()
                resources['people'] = self.filter_people_by_distance(people_list, max_distance)

            if resource_type in ['places', 'all']:
                place_list = self.get_place_list()
                resources['places'] = self.filter_places_by_distance(place_list, max_distance)

            if resource_type in ['tools', 'all']:
                resources['tools'] = self.get_tool_list()

            logger.debug(f"Retrieved nearby resources: {resource_type}")
            return resources

        except Exception as e:
            logger.error(f"Failed to get nearby resources: {e}")
            return {}
