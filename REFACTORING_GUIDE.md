# AISocialEngine 重构使用指南

## 快速开始

### 1. 导入新的重构类

```python
from backend.modules.sns.ai_social_engine_adapter_new import AISocialEngine
```

### 2. 创建实例

```python
from sqlalchemy.orm import Session
from backend.modules.sns.ai_social_engine_adapter_new import AISocialEngine

# 创建数据库会话
db = Session()  # 你的数据库会话

# 初始化 AISocialEngine
engine = AISocialEngine(db)

# 异步初始化
await engine.async_init()

# 启动引擎
await engine.start()
```

### 3. 使用业务方法

重构后的 `AISocialEngine` 提供了所有原有的方法，按业务模块组织：

#### 生命周期管理
```python
await engine.start()           # 启动引擎
await engine.stop()            # 停止引擎
status = engine.get_status()   # 获取状态
engine.start_task()            # 启动任务
```

#### Agent 交互
```python
await engine.ask_agent_and_get_instruction(
    question="我的问题",
    system_role_prompt="系统提示",
    type_flag="command"
)
```

#### 任务执行
```python
engine.think(event="after_conversation", current_chat_summary="对话总结")
await engine.ask_agent_to_decompose_task("任务描述")
```

#### 地图导航
```python
result = engine.go_around()                    # 附近逛逛
result = engine.move_ahead(current_pos, target_pos, "目标地点")  # 移动到指定位置
result = engine.move_to_a_place(lng, lat)  # 移动到地点
```

#### 人员交互
```python
engine.talk_to_a_people(content, nationid, account, user_name)
await engine.ask_agent_start_to_talk_to_a_people(action_str, human_object)
```

#### 工具调用
```python
result = engine.use_tools()
await engine.ask_agent_to_pick_a_tool(task_summary, tool_list)
```

#### XMPP 通信
```python
engine.sendMessage(content, by_click=False, to_jid=None, to_name=None)
engine.handle_receiveMessage(content, from_str)
```

## 架构说明

### 多重继承结构

```
AISocialEngine
├── LifecycleManager              # 生命周期管理
├── AgentCommunicationAdapter      # Agent 交互
├── UICommunicationAdapter        # UI 通信
├── TaskExecutor               # 任务执行
├── MapNavigation              # 地图导航
├── PeopleInteractionManager     # 人员交互
├── ConversationAnalyzer        # 对话分析
├── ToolServiceExecutor        # 工具服务
├── SkillManager              # 技能管理
├── TradeNegotiationManager   # 交易协商
├── MessageProtocolParser      # 消息解析
├── XMPPCommunicationManager  # XMPP 通信
├── ResourceManager          # 资源管理
├── EventHookHandler        # 事件钩子
└── AuxiliaryServices        # 辅助服务
```

### 方法继承规则

- 所有适配器的方法都自动继承到 `AISocialEngine`
- 可以直接通过 `engine.method_name()` 调用
- 方法名与重构前完全一致

## 模块化测试

### 单独测试某个适配器

```python
from backend.modules.sns.adapters.map_navigation import MapNavigation

class TestEngine(MapNavigation):
    pass

engine = TestEngine()
result = engine.go_around()
print(result)
```

### 覆盖某个方法

```python
from backend.modules.sns.adapters.map_navigation import MapNavigation

class CustomEngine(AISocialEngine):
    def go_around(self):
        # 自定义逻辑
        result = super().go_around()
        # 添加自定义处理
        return result
```

## 迁移步骤

### 从旧版本迁移到新版本

1. **更新导入语句**
   ```python
   # 旧版本
   from backend.modules.sns.ai_social_engine_adapter import AISocialEngine
   
   # 新版本
   from backend.modules.sns.ai_social_engine_adapter_new import AISocialEngine
   ```

2. **修改实例化代码**（如有必要）
   - 所有方法调用保持不变
   - `__init__` 参数保持不变

3. **测试验证**
   - 运行所有原有测试用例
   - 确保功能完整性
   - 检查性能是否受影响

4. **逐步替换**
   - 在测试环境先验证
   - 逐步在生产环境替换
   - 保留旧文件作为备份

## 常见问题

### Q1: 为什么方法调用方式没有变化？
A: 因为使用了多重继承，所有适配器的方法都自动继承到主类，保持了原有的API接口不变。

### Q2: 如何访问某个适配器的特定方法？
A: 直接通过 `engine.method_name()` 调用，Python会自动解析到正确的适配器类。

### Q3: 是否需要修改现有代码？
A: 通常不需要，只需更新导入语句即可。所有方法签名和行为保持不变。

### Q4: 如何添加新的业务功能？
A: 在对应的适配器文件中添加新方法，主类会自动继承。

## 性能考虑

- 多重继承在Python中非常高效，几乎没有性能开销
- 方法解析在实例创建时完成，运行时无额外查找
- 代码组织更清晰，可能带来更好的CPU缓存命中

## 扩展建议

### 1. 添加新适配器

```python
# 创建新适配器
# backend/modules/sns/adapters/new_feature_adapter.py

class NewFeatureAdapter:
    def new_method(self):
        # 实现
        pass

# 更新主类继承
class AISocialEngine(
    # ... 其他适配器
    NewFeatureAdapter  # 新增
):
    pass
```

### 2. 替换适配器实现

```python
# 创建新的实现
class CustomMapNavigation(MapNavigation):
    def go_around(self):
        # 自定义实现
        pass

# 使用组合替代继承（可选）
class AISocialEngine(
    # ... 其他适配器
):
    def __init__(self, db):
        self.map_nav = CustomMapNavigation()
        # ... 其他初始化
```

## 技术支持

如有问题，请参考：
- `REFACTORING_SUMMARY.md` - 完整重构报告
- 各适配器文件中的文档字符串
- 原始 `ai_social_engine_adapter.py` 文件
