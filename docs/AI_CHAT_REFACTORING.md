# AI 聊天功能重构文档

## 概述

本次重构将 Electron 前端的 AI 聊天功能从直接调用 OpenAI API 改为通过后端 API 服务器进行代理。这样做的好处包括：

1. **安全性提升**：API 密钥不再暴露在前端代码中
2. **统一管理**：所有 AI 配置集中在后端管理
3. **灵活性**：可以轻松切换不同的 AI 模型和服务提供商
4. **可扩展性**：便于添加日志、监控、限流等功能

## 架构变更

### 原架构
```
Electron Frontend → 直接调用 OpenAI API
```

### 新架构
```
Electron Frontend → Backend API Server → OpenAI API (或其他 LLM 服务)
```

## 主要修改

### 1. 后端 (api_server.py)

#### 新增配置管理函数
- `get_ai_config()`: 从数据库或环境变量读取 AI 配置
  - 优先从数据库 `aichat_cfg` 表读取
  - 如果数据库没有配置，使用环境变量
  - 支持的配置项：
    - `api_base`: API 基础地址
    - `api_key`: API 密钥
    - `model`: 模型名称（默认：gpt-4o-mini）
    - `temperature`: 温度参数（默认：1.0）
    - `max_tokens`: 最大 token 数（默认：4096）

#### 新增流式聊天端点
- **路径**: `POST /api/chat/stream`
- **协议**: Server-Sent Events (SSE)
- **请求格式**:
  ```json
  {
    "messages": [
      {"role": "user", "content": "你好"},
      {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
    ],
    "model": "gpt-4o-mini",  // 可选
    "temperature": 1.0,       // 可选
    "max_tokens": 4096        // 可选
  }
  ```

- **响应格式** (SSE):
  ```
  event: message
  data: {"content": "你"}

  event: message
  data: {"content": "好"}

  event: done
  data: {"status": "completed"}
  ```

- **错误格式**:
  ```
  event: error
  data: {"error": "错误信息"}
  ```

### 2. 前端 (electron/main.js)

#### 移除的配置
- 删除了硬编码的 `AZURE_OPENAI_CONFIG`
- API 配置现在完全由后端管理

#### 修改的 IPC 处理器
- `chat-stream-start`:
  - 从调用 `https://api.chatanywhere.tech/v1` 改为调用 `http://localhost:8788/api/chat/stream`
  - 从处理 OpenAI SSE 格式改为处理后端统一的 SSE 格式
  - 错误处理更加健壮

## 配置方式

配置优先级（从高到低）：**数据库配置 > 环境变量 > 配置文件**

### 方式一：配置文件（推荐）

这是最简单的方式，适合快速开始使用。

1. 复制示例配置文件：
```bash
cp ai_config.yaml.example ai_config.yaml
```

2. 编辑 `ai_config.yaml` 文件，填入你的配置：
```yaml
ai:
  api_base: "https://api.chatanywhere.tech/v1"
  api_key: "sk-your-api-key-here"
  model: "gpt-4o-mini"
  temperature: 1.0
  max_tokens: 4096
  stream: true
```

**注意**：`ai_config.yaml` 已添加到 `.gitignore`，不会被提交到版本控制，保护你的 API 密钥安全。

### 方式二：数据库配置

数据库配置具有最高优先级，适合生产环境或需要动态切换配置的场景。

在 `aichat_cfg` 表中添加配置记录：

```sql
INSERT INTO aichat_cfg (name, api_base, api_key, model, temperature, max_tokens, is_delete)
VALUES (
  'OpenAI',
  'https://api.openai.com/v1',
  'sk-your-api-key-here',
  'gpt-4o-mini',
  1.0,
  4096,
  0
);
```

### 方式三：环境变量配置

适合容器化部署或需要通过环境变量管理配置的场景。

在启动 API 服务器前设置环境变量：

```bash
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_API_KEY="sk-your-api-key-here"
export OPENAI_MODEL="gpt-4o-mini"
export OPENAI_TEMPERATURE="1.0"
export OPENAI_MAX_TOKENS="4096"
```

Windows PowerShell:
```powershell
$env:OPENAI_API_BASE="https://api.openai.com/v1"
$env:OPENAI_API_KEY="sk-your-api-key-here"
$env:OPENAI_MODEL="gpt-4o-mini"
$env:OPENAI_TEMPERATURE="1.0"
$env:OPENAI_MAX_TOKENS="4096"
```

## 部署步骤

### 1. 安装依赖

确保已安装 platform 依赖：

```bash
pip install -r requirements_platform.txt
```

关键依赖：
- `httpx>=0.25.0` - 用于异步 HTTP 请求
- `sse-starlette>=1.8.0` - 用于 SSE 流式响应
- `PyYAML` - 用于读取配置文件

### 2. 配置 AI 服务

**快速开始（推荐）**:

```bash
# 复制配置模板
cp ai_config.yaml.example ai_config.yaml

# 编辑配置文件，填入你的 API 密钥
# 使用你喜欢的编辑器打开 ai_config.yaml
nano ai_config.yaml  # 或 vim, code 等
```

项目已经在 `ai_config.yaml` 中提供了默认配置，包括：
- API 地址: `https://api.chatanywhere.tech/v1`
- API 密钥: 预配置的测试密钥
- 模型: `gpt-4o-mini`

**如果你不修改配置文件，系统将使用这些默认值，可以直接使用。**

或者，选择上述其他配置方式之一（数据库或环境变量）。

### 3. 启动后端服务

```bash
python api_server.py --host 0.0.0.0 --port 8788
```

或使用自动重载模式（开发环境）：

```bash
python api_server.py --host 0.0.0.0 --port 8788 --reload
```

### 4. 启动 Electron 应用

确保 Electron 应用配置中的 API 地址正确：

```javascript
const API_HOST = 'localhost';
const API_PORT = 8788;
```

然后启动应用：

```bash
npm start
```

或开发模式：

```bash
npm start -- --dev
```

## 测试验证

### 测试后端 API

使用 curl 测试流式聊天：

```bash
curl -N -X POST http://localhost:8788/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

预期输出（SSE 格式）：
```
event: message
data: {"content": "你"}

event: message
data: {"content": "好"}

event: done
data: {"status": "completed"}
```

### 测试前端集成

1. 启动后端服务
2. 启动 Electron 应用
3. 打开 Agent 聊天窗口
4. 发送测试消息
5. 查看控制台日志：
   - 后端日志：`INFO:     Streaming chat request to: ...`
   - 前端日志：`Sending chat request to backend: ...`
   - 前端日志：`Stream content: ...`

## 故障排除

### 问题 1: 连接后端失败

**症状**: 前端显示连接错误

**解决方案**:
1. 确认后端服务已启动：`curl http://localhost:8788/health`
2. 检查防火墙设置
3. 确认端口 8788 未被占用

### 问题 2: API 密钥错误

**症状**: 后端日志显示 401 或 403 错误

**解决方案**:
1. 检查配置的 API 密钥是否正确
2. 确认 API 密钥有足够的余额/配额
3. 查看后端日志获取详细错误信息

### 问题 3: 流式输出卡住

**症状**: 只收到部分响应就停止了

**解决方案**:
1. 检查网络连接是否稳定
2. 查看后端日志是否有异常
3. 增加超时时间（httpx client timeout）

### 问题 4: SSE 格式解析错误

**症状**: 前端控制台显示 JSON 解析错误

**解决方案**:
1. 检查后端 SSE 输出格式是否正确
2. 查看网络请求的 Raw 响应
3. 确认没有代理/中间件修改了响应内容

## 扩展建议

### 1. 添加多模型支持

可以在数据库中配置多个 AI 模型，前端选择使用：

```python
def get_ai_config(model_name=None):
    if model_name:
        cfg = query_AiChatCfg_by_name(model_name)
    else:
        cfg = query_AiChatCfg_All(is_delete=0)[0]
    # ...
```

### 2. 添加请求日志

在 `stream_chat` 函数中记录所有请求：

```python
logger.info(f"Chat request from user, messages count: {len(request.messages)}")
```

### 3. 添加限流保护

使用 FastAPI 中间件限制请求频率：

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat/stream")
@limiter.limit("10/minute")
async def stream_chat(request: StreamChatRequest):
    # ...
```

### 4. 添加缓存机制

对于相同的问题可以返回缓存的答案：

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 检查缓存
cache_key = hashlib.md5(json.dumps(request.messages).encode()).hexdigest()
cached = r.get(cache_key)
if cached:
    yield {"event": "message", "data": cached}
    return
```

## 相关文件

- **后端**: `/api_server.py`
  - 流式聊天端点：第 532-634 行
  - AI 配置管理：第 102-126 行

- **前端**: `/electron/main.js`
  - IPC 处理器：第 331-467 行
  - API 配置：第 22-24 行

- **依赖**: `/requirements_platform.txt`
  - httpx 和 sse-starlette

## 更新日志

- **2025-01-09**: 完成初始重构
  - 添加后端流式聊天 API
  - 重构前端 AI 调用逻辑
  - 移除硬编码配置
