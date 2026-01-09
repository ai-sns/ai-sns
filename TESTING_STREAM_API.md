# 测试流式聊天 API 指南

## 问题说明

如果你在浏览器中直接访问 `http://localhost:8788/api/chat/stream`，会看到 "Method Not Allowed" 错误。

**原因**：这是一个 `POST` 端点，浏览器默认使用 `GET` 方法。

## 解决方案

### 方案 1：使用 Python 测试脚本（推荐）

我们提供了一个测试脚本，可以直观地看到流式输出：

```bash
python test_stream_api.py
```

这个脚本会：
1. 检查 API 服务健康状态
2. 发送一个测试消息
3. 实时显示 AI 的流式回复

### 方案 2：使用 curl 命令

#### Linux/macOS:
```bash
bash test_stream_api.sh
```

或直接使用 curl:
```bash
curl -N -X POST http://localhost:8788/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请用一句话介绍自己"}
    ]
  }'
```

#### Windows:
```cmd
test_stream_api.bat
```

或使用 PowerShell:
```powershell
curl.exe -N -X POST http://localhost:8788/api/chat/stream `
  -H "Content-Type: application/json" `
  -H "Accept: text/event-stream" `
  -d '{\"messages\": [{\"role\": \"user\", \"content\": \"你好\"}]}'
```

### 方案 3：在浏览器中查看 API 文档

1. **查看端点信息**：
   访问 http://localhost:8788/api/chat/stream

   浏览器会显示 JSON 格式的使用说明，包括：
   - 请求方法
   - 请求格式
   - 示例命令

2. **查看完整 API 文档**：
   访问 http://localhost:8788/docs

   FastAPI 自动生成的交互式文档，可以直接在浏览器中测试 API！

3. **查看所有端点**：
   访问 http://localhost:8788/

   显示所有可用的 API 端点列表

## 验证步骤

### 1. 检查服务是否运行

```bash
curl http://localhost:8788/health
```

应该返回：
```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T..."
}
```

### 2. 测试流式聊天

运行测试脚本：
```bash
python test_stream_api.py
```

预期输出：
```
🚀 AI-SNS 流式聊天 API 测试工具

检查 API 服务健康状态...
✓ API 服务运行正常
  状态: healthy
  时间: 2025-01-09T...

============================================================
测试流式聊天 API
============================================================
URL: http://localhost:8788/api/chat/stream
请求数据: {
  "messages": [
    {
      "role": "user",
      "content": "你好，请用一句话介绍自己"
    }
  ]
}
============================================================
AI 回复:
------------------------------------------------------------
你好！我是一个人工智能助手，旨在帮助你解答问题和提供信息。
------------------------------------------------------------
✓ 测试成功！共接收 XX 个字符
============================================================
```

## 常见问题

### Q1: 提示 "Connection refused" 或 "无法连接"

**原因**：后端服务未启动

**解决方案**：
```bash
python api_server.py --port 8788
```

### Q2: 提示 401 或 403 错误

**原因**：API 密钥无效或额度用完

**解决方案**：
1. 编辑 `ai_config.yaml` 文件
2. 更换为你自己的 API 密钥
3. 重启服务

### Q3: 返回错误但没有流式输出

**原因**：可能是网络问题或 API 服务异常

**解决方案**：
1. 查看后端控制台日志
2. 检查 `ai_config.yaml` 中的 `api_base` 地址是否正确
3. 尝试使用其他 API 服务

### Q4: curl 命令在 Windows 上不工作

**原因**：Windows CMD 对引号处理不同

**解决方案**：
- 使用 PowerShell 而不是 CMD
- 或直接运行 `test_stream_api.bat`
- 或使用 Python 脚本：`python test_stream_api.py`

## 在代码中使用

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8788/api/chat/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: '你好' }
    ]
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  // 处理 SSE 数据
  console.log(chunk);
}
```

### Python

```python
import requests
import json

response = requests.post(
    'http://localhost:8788/api/chat/stream',
    json={'messages': [{'role': 'user', 'content': '你好'}]},
    headers={'Accept': 'text/event-stream'},
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data:'):
            data = json.loads(line_str[5:])
            if 'content' in data:
                print(data['content'], end='', flush=True)
```

## 相关文件

- `test_stream_api.py` - Python 测试脚本（推荐）
- `test_stream_api.sh` - Linux/macOS Shell 脚本
- `test_stream_api.bat` - Windows 批处理脚本
- `api_server.py` - API 服务器源码
- `ai_config.yaml` - AI 配置文件

## 获取帮助

如果遇到其他问题：

1. 查看后端日志：启动 `api_server.py` 时的控制台输出
2. 查看完整文档：`docs/AI_CHAT_REFACTORING.md`
3. 查看快速开始：`AI_CONFIG_QUICKSTART.md`
