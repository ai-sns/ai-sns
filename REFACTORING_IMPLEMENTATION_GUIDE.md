# AISocialEngine 重构实施指南

## 快速开始

本指南提供了详细的重构步骤，确保系统功能完整性，特别是 POST /api/sns/start-engine 接口的正常运行。

---

## 第一步：创建适配器目录结构

```bash
cd backend/modules/sns
mkdir adapters
cd adapters
touch __init__.py
```

---

## 第二步：按顺序创建适配器文件

### 2.1 创建 utility_adapter.py（无依赖）

```python
"""
工具适配器
提供通用辅助功能
"""
import logging
import requests
import geopy.distance
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class UtilityAdapter:
    """通用工具适配器"""

    def __init__(self, parent):
        self.parent = parent
        self.logger = logger

    def http_request(self, url: str, params: Optional[Dict] = None, method: str = "POST"):
        """
        发送HTTP请求

        Args:
            url: 请求URL
            params: 请求参数
            method: 请求方法 (GET/POST)

        Returns:
            响应的JSON数据，失败返回None
        """
        try:
            method = method.upper()
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, data=params)
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP错误发生: {http_err}")
        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"请求错误发生: {req_err}")
        except ValueError as json_err:
            self.logger.error(f"JSON解析错误: {json_err}")

        return None

    def get_dict_by_id(self, dict_list: List[Dict], target_id: str) -> Optional[Dict]:
        """
        根据目标 id 从字典列表中查找并返回对应的字典

        Args:
            dict_list: 包含若干字典的列表
            target_id: 目标 id 字符串

        Returns:
            对应 id 的字典，如果没有找到，则返回 None
        """
        dict_map = {d['id']: d for d in dict_list}
        return dict_map.get(target_id)

    def remove_dict_from_list(self, dict_list: List[Dict], t_dict: Dict) -> List[Dict]:
        """
        从列表中移除指定字典

        Args:
            dict_list: 字典列表
            t_dict: 需要移除的字典

        Returns:
            移除后的列表
        """
        return [dict_item for dict_item in dict_list if dict_item != t_dict]

    def are_lists_of_dicts_equal(self, list1: List[Dict], list2: List[Dict]) -> bool:
        """
        检查两个字典列表是否相等（忽略顺序）

        Args:
            list1: 第一个字典列表
            list2: 第二个字典列表

        Returns:
            相等返回True，否则返回False
        """
        sorted_list1 = sorted(list1, key=lambda d: str(sorted(d.items())))
        sorted_list2 = sorted(list2, key=lambda d: str(sorted(d.items())))
        return sorted_list1 == sorted_list2

    def get_people_by_distance(self, count: int, people_list: List[Dict]) -> List[Dict]:
        """
        返回按与给定位置的距离排序的最近人员列表

        Args:
            count: 要返回的最近人员数量
            people_list: 人员字典列表

        Returns:
            按距离排序的最近人员列表
        """
        my_position = self.parent.aichatcfg_record.current_position

        if not people_list or not all("location" in person and len(person["location"]) == 2 for person in people_list):
            return []

        # 转换为 (latitude, longitude) 格式
        my_position_converted = (my_position[1], my_position[0])

        # 计算距离
        distances = [
            (geopy.distance.geodesic(my_position_converted, (person["location"][1], person["location"][0])).km, person)
            for person in people_list
        ]

        # 按距离排序
        distances.sort()

        # 返回最近的人员
        return [person for distance, person in distances[:count]]

    def download_file(self, url: str, file_path: str) -> bool:
        """
        下载文件

        Args:
            url: 文件URL
            file_path: 保存路径

        Returns:
            成功返回True，失败返回False
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                self.logger.info(f"文件 '{file_path}' 下载成功！")
                return True
            else:
                self.logger.error(f"下载失败，状态码：{response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"下载文件时出错: {e}")
            return False
```

### 2.2 创建 message_protocol_adapter.py（无依赖）

```python
"""
消息协议解析适配器
解析各种消息协议格式
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class MessageProtocolAdapter:
    """消息协议解析适配器"""

    def __init__(self, parent):
        self.parent = parent
        self.logger = logger

    def get_tool_list_in_message(self, msg: str) -> Optional[str]:
        """
        从消息中提取工具列表JSON字符串

        Args:
            msg: 包含工具列表的消息

        Returns:
            提取的JSON字符串，未找到返回None
        """
        pattern = r'AISNS_INT_001_TOOL_DETAIL_SHOW_START(.*?)AISNS_INT_001_TOOL_DETAIL_SHOW_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_tool_order_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取工具订单信息"""
        pattern = r'AISNS_INT_002_TOOL_ORDER_START(.*?)AISNS_INT_002_TOOL_ORDER_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_order_confirm_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取订单确认信息"""
        pattern = r'AISNS_INT_003_TOOL_ORDER_CONFIRM_START(.*?)AISNS_INT_003_TOOL_ORDER_CONFIRM_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_tool_mcp_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取MCP工具信息"""
        pattern = r'AISNS_INT_004_TOOL_SEND_START(.*?)AISNS_INT_004_TOOL_SEND_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_tool_inquiry_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取工具询价信息"""
        pattern = r'AISNS_INT_005_TOOL_INQUIRY_START(.*?)AISNS_INT_005_TOOL_INQUIRY_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_buyer_bargain_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取买家议价信息"""
        pattern = r'AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_START(.*?)AISNS_INT_006_TOOL_BARGAIN_FOR_BUYER_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def get_seller_bargain_in_message(self, msg: str) -> Optional[str]:
        """从消息中提取卖家议价信息"""
        pattern = r'AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_START(.*?)AISNS_INT_007_TOOL_BARGAIN_FOR_SELLER_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def check_pay_in_received(self, msg: str) -> Optional[str]:
        """检查消息中是否包含付款信息"""
        pattern = r'AISNS_INT_001_PAY_SEND_START(.*?)AISNS_INT_001_PAY_SEND_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def check_good_in_received(self, msg: str) -> Optional[str]:
        """检查消息中是否包含货物信息"""
        pattern = r'AISNS_INT_002_GOOD_SEND_START(.*?)AISNS_INT_002_GOOD_SEND_END'
        match = re.search(pattern, msg, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def check_buy_in_received(self, msg: str) -> bool:
        """检查消息中是否包含购买请求"""
        pattern = '[AISNS_INT_003_INQUIRY]'
        return pattern in msg

    def get_tool_url_in_message_v2(self, msg: str) -> Optional[str]:
        """从消息中提取交易ID"""
        match = re.search(r'AISNS_INT_002_TN_(.*?)_SYS_CONTENT_SENDING_FILE', msg)
        if match:
            return match.group(1)
        return None

    def get_tool_confirm_in_message(self, msg: str, prefix: str = "AISNS_INT_003_TN_") -> str:
        """从消息中提取确认信息"""
        if msg.startswith(prefix):
            return msg[len(prefix):]
        return ""

    # 便捷方法
    def check_tool_for_buy(self, msg: str) -> Optional[str]:
        """检查是否为购买工具消息"""
        return self.get_tool_list_in_message(msg)

    def check_tool_for_inquiry(self, msg: str) -> Optional[str]:
        """检查是否为询价消息"""
        return self.get_tool_inquiry_in_message(msg)

    def check_tool_for_order(self, msg: str) -> Optional[str]:
        """检查是否为订单消息"""
        return self.get_tool_order_in_message(msg)

    def check_tool_for_order_confirm(self, msg: str) -> Optional[str]:
        """检查是否为订单确认消息"""
        return self.get_order_confirm_in_message(msg)

    def check_tool_for_receive(self, msg: str) -> Optional[str]:
        """检查是否为接收工具消息"""
        return self.get_tool_mcp_in_message(msg)

    def check_tool_for_buyer_bargain(self, msg: str) -> Optional[str]:
        """检查是否为买家议价消息"""
        return self.get_buyer_bargain_in_message(msg)

    def check_tool_for_seller_bargain(self, msg: str) -> Optional[str]:
        """检查是否为卖家议价消息"""
        return self.get_seller_bargain_in_message(msg)
```

### 2.3 更新 adapters/__init__.py

```python
"""
SNS适配器模块
"""
from .utility_adapter import UtilityAdapter
from .message_protocol_adapter import MessageProtocolAdapter

__all__ = [
    'UtilityAdapter',
    'MessageProtocolAdapter',
]
```

---

## 第三步：重构主类初始化

修改 `ai_social_engine_adapter.py` 的 `__init__` 方法：

```python
def __init__(self, db: Session):
    self.db = db
    # ... 其他初始化代码 ...

    # 初始化适配器
    from backend.modules.sns.adapters import UtilityAdapter, MessageProtocolAdapter
    self.utility_adapter = UtilityAdapter(self)
    self.protocol_adapter = MessageProtocolAdapter(self)

    # ... 其他初始化代码 ...
```

---

## 第四步：逐步替换方法调用

### 示例：替换 http_request 方法

**原代码：**
```python
def http_request(self, url, params=None, method="POST"):
    # ... 实现代码 ...
```

**重构后：**
```python
def http_request(self, url, params=None, method="POST"):
    """委托给utility_adapter"""
    return self.utility_adapter.http_request(url, params, method)
```

### 示例：替换协议解析方法

**原代码：**
```python
def get_tool_list_in_message(self, msg):
    pattern = r'AISNS_INT_001_TOOL_DETAIL_SHOW_START(.*?)AISNS_INT_001_TOOL_DETAIL_SHOW_END'
    match = re.search(pattern, msg, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
```

**重构后：**
```python
def get_tool_list_in_message(self, msg):
    """委托给protocol_adapter"""
    return self.protocol_adapter.get_tool_list_in_message(msg)
```

---

## 第五步：测试验证

### 5.1 单元测试

创建 `tests/test_adapters.py`:

```python
import pytest
from backend.modules.sns.adapters import UtilityAdapter, MessageProtocolAdapter


class MockParent:
    """模拟父类"""
    def __init__(self):
        self.aichatcfg_record = type('obj', (object,), {
            'current_position': [116.0, 40.0]
        })()


def test_utility_adapter():
    """测试工具适配器"""
    parent = MockParent()
    adapter = UtilityAdapter(parent)

    # 测试 get_dict_by_id
    dict_list = [{'id': '1', 'name': 'test1'}, {'id': '2', 'name': 'test2'}]
    result = adapter.get_dict_by_id(dict_list, '1')
    assert result == {'id': '1', 'name': 'test1'}


def test_protocol_adapter():
    """测试协议适配器"""
    parent = MockParent()
    adapter = MessageProtocolAdapter(parent)

    # 测试工具列表提取
    msg = "AISNS_INT_001_TOOL_DETAIL_SHOW_START{\"test\": \"data\"}AISNS_INT_001_TOOL_DETAIL_SHOW_END"
    result = adapter.get_tool_list_in_message(msg)
    assert result == '{"test": "data"}'
```

运行测试：
```bash
pytest tests/test_adapters.py -v
```

### 5.2 集成测试

测试 POST /api/sns/start-engine 接口：

```bash
# 启动服务器
python api_server.py

# 在另一个终端测试接口
curl -X POST http://localhost:8000/api/sns/start-engine \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 第六步：继续创建其他适配器

按照 REFACTORING_PLAN.md 中的顺序，继续创建其他适配器：

1. resource_management_adapter.py
2. agent_communication_adapter.py
3. movement_adapter.py
4. place_selection_adapter.py
5. tool_management_adapter.py
6. people_communication_adapter.py
7. xmpp_message_adapter.py
8. trading_adapter.py
9. skill_service_adapter.py
10. task_management_adapter.py
11. activity_processing_adapter.py

---

## 第七步：完整性检查清单

### 功能检查：
- [ ] POST /api/sns/start-engine 接口正常
- [ ] Agent可以正常启动和停止
- [ ] 消息收发功能正常
- [ ] 移动功能正常
- [ ] 工具选择和调用正常
- [ ] 人员沟通功能正常
- [ ] 交易功能正常
- [ ] 数据库操作正常

### 代码质量检查：
- [ ] 所有适配器都有完整的文档字符串
- [ ] 日志记录完整
- [ ] 异常处理完善
- [ ] 类型提示完整
- [ ] 代码风格统一

### 性能检查：
- [ ] 无明显性能下降
- [ ] 内存使用正常
- [ ] 响应时间正常

---

## 第八步：文档更新

更新以下文档：
1. README.md - 添加架构说明
2. API文档 - 更新接口说明
3. 开发文档 - 添加适配器使用指南

---

## 常见问题解决

### Q1: 循环依赖问题
**解决方案**: 使用延迟导入或重新设计依赖关系

```python
# 不好的做法
from .adapter_a import AdapterA

# 好的做法
def method(self):
    from .adapter_a import AdapterA
    adapter = AdapterA(self.parent)
```

### Q2: 适配器间通信
**解决方案**: 通过parent对象访问其他适配器

```python
# 在适配器A中访问适配器B
def method_in_adapter_a(self):
    result = self.parent.adapter_b.some_method()
```

### Q3: 测试困难
**解决方案**: 使用Mock对象和依赖注入

```python
class TestableAdapter:
    def __init__(self, parent, dependency=None):
        self.parent = parent
        self.dependency = dependency or RealDependency()
```

---

## 回滚方案

如果重构出现问题，可以快速回滚：

```bash
# 1. 切换到备份分支
git checkout backup-branch

# 2. 或者恢复特定文件
git checkout HEAD~1 -- backend/modules/sns/ai_social_engine_adapter.py

# 3. 重启服务
systemctl restart ai-sns-service
```

---

## 总结

本重构方案将4280行的单一类拆分为13个职责清晰的适配器，每个适配器约100-400行代码。重构后的系统将更易于维护、测试和扩展。

关键成功因素：
1. 按依赖关系顺序实施
2. 每个阶段都进行测试
3. 保持接口兼容性
4. 详细的日志记录
5. 完善的文档

预计工作量：10-12个工作日
风险等级：中等
收益：显著提升代码质量和可维护性
