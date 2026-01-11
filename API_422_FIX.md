# API 端点 422 错误修复

## 问题描述

前端访问 LLM 和 Role 配置 API 时遇到 422 错误：
```
GET http://localhost:8788/api/agent/llm-configs 422 (Unprocessable Entity)
GET http://localhost:8788/api/agent/role-configs 422 (Unprocessable Entity)
```

## 问题原因

FastAPI 的 Query 参数定义为必需的布尔类型：
```python
active_only: bool = Query(True, ...)
```

当前端不传递任何查询参数时，FastAPI 会尝试将 `None` 转换为 `bool`，导致验证失败并返回 422 错误。

## 解决方案

将 Query 参数改为可选类型：

### 修复前
```python
@router.get("", response_model=dict)
async def get_llm_configs(
    active_only: bool = Query(True, description="...")
):
```

### 修复后
```python
@router.get("", response_model=dict)
async def get_llm_configs(
    active_only: Optional[bool] = Query(None, description="...")
):
    # 如果没有指定 active_only，默认返回所有活跃的配置
    configs = service.get_all(active_only=active_only if active_only is not None else True)
```

## 修复的文件

1. ✅ `backend/modules/agent/llm_router.py` - LLM 配置路由
2. ✅ `backend/modules/agent/role_router.py` - Role 配置路由

## 验证测试

重启后端服务器后，测试以下 API 端点：

### 1. 测试 LLM 配置 API

```bash
# 不带参数
curl http://localhost:8788/api/agent/llm-configs

# 带参数
curl "http://localhost:8788/api/agent/llm-configs?active_only=true"
curl "http://localhost:8788/api/agent/llm-configs?active_only=false"
```

预期响应：
```json
{
  "success": true,
  "data": [
    {
      "config_id": "cfg_xxx",
      "name": "GPT-4",
      "provider": "openai",
      "is_active": true,
      ...
    }
  ]
}
```

### 2. 测试 Role 配置 API

```bash
# 不带参数
curl http://localhost:8788/api/agent/role-configs

# 带参数
curl "http://localhost:8788/api/agent/role-configs?active_only=true"
curl "http://localhost:8788/api/agent/role-configs?category=developer"
```

预期响应：
```json
{
  "success": true,
  "data": [
    {
      "role_id": "role_xxx",
      "name": "开发助手",
      "category": "developer",
      "is_active": true,
      ...
    }
  ]
}
```

### 3. 前端测试

在浏览器控制台中测试：

```javascript
// 测试 LLM 配置
fetch('http://localhost:8788/api/agent/llm-configs')
  .then(r => r.json())
  .then(d => console.log('LLM configs:', d));

// 测试 Role 配置
fetch('http://localhost:8788/api/agent/role-configs')
  .then(r => r.json())
  .then(d => console.log('Role configs:', d));
```

## 预期行为

- ✅ 不带参数时，返回所有活跃的配置（active_only=true）
- ✅ 带 `active_only=false` 时，返回所有配置（包括非活跃的）
- ✅ 带 `category` 参数时，按类别过滤
- ✅ 不再返回 422 错误

## 重启步骤

1. 停止当前运行的 `api_server.py`（Ctrl+C）
2. 重新启动：
   ```bash
   python api_server.py
   ```
3. 刷新浏览器或重启 Electron 应用
4. 点击 Agent 页面的 Setting 按钮

## 相关端点

所有需要这些配置的功能都会受益：

- ✅ Agent Settings 对话框 - 需要加载 LLM 和 Role 选项
- ✅ 模型管理页面 - 显示所有 LLM 配置
- ✅ 角色管理页面 - 显示所有 Role 配置
- ✅ Agent 聊天界面 - 模型和角色选择器

## 额外优化

如果你想要更灵活的默认行为，可以进一步修改：

```python
@router.get("", response_model=dict)
async def get_llm_configs(
    active_only: Optional[bool] = None,  # 不使用 Query，直接设置为 None
    category: Optional[str] = None
):
    """Get all LLM configurations."""
    try:
        service = LlmConfigService()
        # 默认行为：如果没有指定，返回所有活跃配置
        if active_only is None:
            active_only = True
        configs = service.get_all(active_only=active_only, category=category)
        return {"success": True, "data": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 总结

修复非常简单，只需要：
1. 将 `bool` 改为 `Optional[bool]`
2. 将 `Query(True, ...)` 改为 `Query(None, ...)`
3. 在函数内部处理 `None` 值，设置合理的默认值

这样既保持了 API 的灵活性，又避免了 422 验证错误。✅
