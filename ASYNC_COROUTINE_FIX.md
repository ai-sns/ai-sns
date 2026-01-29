# 异步协程未 await 问题修复报告

## 问题描述

在运行时出现以下警告：

```
C:\dev\agi-ev\ai-sns-el\backend\modules\sns\map_task_manager.py:610: RuntimeWarning: 
coroutine 'TradeMixin.ask_agent_to_review_conversation_sell' was never awaited
self.parent.ask_agent_to_review_conversation_sell(self.current_objective, talk_history_str)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

## 问题原因

在 `map_task_manager.py` 中，`process_task()` 方法是一个**同步方法**，但它直接调用了**异步方法**而没有使用 `await` 或 `asyncio.create_task()`。

### 问题代码位置

**文件**: `backend/modules/sns/map_task_manager.py`

#### 问题 1: 第 610 行
```python
# ❌ 错误：直接调用异步方法
self.parent.ask_agent_to_review_conversation_sell(self.current_objective, talk_history_str)
```

#### 问题 2: 第 613 行
```python
# ❌ 错误：直接调用异步方法
self.parent.ask_agent_to_review_conversation_buy(self.current_objective, talk_history_str)
```

#### 问题 3: 第 616 行
```python
# ❌ 错误：直接调用异步方法
self.parent.ask_agent_to_review_conversation(self.current_objective, talk_history_str)
```

#### 问题 4: 第 505 行
```python
# ❌ 错误：直接调用异步方法
self.parent.ask_agent_instruction_to_process_human_instruction(ask_content)
```

---

## 修复方案

由于 `process_task()` 是同步方法，我们使用 `asyncio.create_task()` 来调度异步任务的执行。

### 修复 1: conversation_message_received 事件处理

**修复前**:
```python
elif event =="conversation_message_received":
    talk_history_str = kwargs.get("talk_history_str", "")

    if self.parent.talk_type == "sell":
        self.set_command_status("ask_agent_to_review_conversation_sell")
        self.parent.ask_agent_to_review_conversation_sell(self.current_objective, talk_history_str)
    elif self.parent.talk_type == "buy":
        self.set_command_status("ask_agent_to_review_conversation_buy")
        self.parent.ask_agent_to_review_conversation_buy(self.current_objective, talk_history_str)
    else:
        self.set_command_status("ask_agent_to_review_conversation")
        self.parent.ask_agent_to_review_conversation(self.current_objective, talk_history_str)
```

**修复后**:
```python
elif event =="conversation_message_received":
    talk_history_str = kwargs.get("talk_history_str", "")

    if self.parent.talk_type == "sell":
        self.set_command_status("ask_agent_to_review_conversation_sell")
        asyncio.create_task(self.parent.ask_agent_to_review_conversation_sell(self.current_objective, talk_history_str))
    elif self.parent.talk_type == "buy":
        self.set_command_status("ask_agent_to_review_conversation_buy")
        asyncio.create_task(self.parent.ask_agent_to_review_conversation_buy(self.current_objective, talk_history_str))
    else:
        self.set_command_status("ask_agent_to_review_conversation")
        asyncio.create_task(self.parent.ask_agent_to_review_conversation(self.current_objective, talk_history_str))
```

### 修复 2: process_human_instruction 动作处理

**修复前**:
```python
elif action_requested=="process_human_instruction":

    ask_content = kwargs.get("ask_content", "")

    self.set_command_status("ask_agent_instruction_to_process_human_instruction")

    self.parent.ask_agent_instruction_to_process_human_instruction(ask_content)
```

**修复后**:
```python
elif action_requested=="process_human_instruction":

    ask_content = kwargs.get("ask_content", "")

    self.set_command_status("ask_agent_instruction_to_process_human_instruction")

    asyncio.create_task(self.parent.ask_agent_instruction_to_process_human_instruction(ask_content))
```

---

## 修复说明

### 为什么使用 `asyncio.create_task()`？

1. **同步方法调用异步方法**: `process_task()` 是同步方法，不能使用 `await`
2. **非阻塞执行**: `asyncio.create_task()` 会立即返回，不会阻塞当前方法
3. **任务调度**: 异步任务会被添加到事件循环中，在适当的时候执行
4. **一致性**: 代码中其他地方已经使用了这种模式（如第 464、496 行）

### 示例对比

**其他正确的调用**（已存在于代码中）:
```python
# 第 464 行 ✅ 正确
asyncio.create_task(self.parent.ask_agent_to_decompose_task(task))

# 第 496 行 ✅ 正确
asyncio.create_task(self.parent.ask_agent_instruction_to_process_activity(ask_content))
```

---

## 验证修复

### 1. 检查警告是否消失

运行应用后，之前的 RuntimeWarning 应该不再出现：
```
✅ 不再出现: RuntimeWarning: coroutine 'TradeMixin.ask_agent_to_review_conversation_sell' was never awaited
```

### 2. 功能测试

测试以下场景：
- ✅ 对话消息接收（sell 类型）
- ✅ 对话消息接收（buy 类型）
- ✅ 对话消息接收（普通类型）
- ✅ 处理人类指令

### 3. 日志检查

确认异步任务正常执行：
```python
# 在异步方法中应该能看到日志输出
logger.info("ask_agent_to_review_conversation_sell called")
```

---

## 相关文件

### 修改的文件
- `backend/modules/sns/map_task_manager.py`

### 涉及的异步方法
- `backend/modules/sns/trade_mixin.py`:
  - `ask_agent_to_review_conversation_sell()`
  - `ask_agent_to_review_conversation_buy()`
  
- `backend/modules/sns/communication_mixin.py`:
  - `ask_agent_to_review_conversation()`
  
- `backend/modules/sns/ai_social_engine_adapter.py`:
  - `ask_agent_instruction_to_process_human_instruction()`

---

## 总结

✅ **修复完成**

- 修复了 4 处异步协程未 await 的问题
- 使用 `asyncio.create_task()` 正确调度异步任务
- 保持了代码的一致性和非阻塞特性
- 不会再出现 RuntimeWarning

**修复方式**: 在同步方法中调用异步方法时，使用 `asyncio.create_task()` 包装调用。

**影响范围**: 仅修改了 `map_task_manager.py` 文件，不影响其他模块。
