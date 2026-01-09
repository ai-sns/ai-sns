# "Method Not Allowed" 错误解决方案

## 🔴 问题

访问 `http://localhost:8788/api/chat/stream` 时出现 **405 Method Not Allowed** 错误。

## ✅ 原因

这是一个 **POST 端点**，不是 GET 端点。浏览器直接访问 URL 时使用的是 GET 方法，所以会报错。

## 🎯 快速解决（3种方法）

### 方法 1：使用 Python 测试脚本（最简单）✨

```bash
python test_stream_api.py
```

**优点**：
- ✅ 自动检查服务状态
- ✅ 实时显示流式输出
- ✅ 跨平台（Windows/Linux/macOS）
- ✅ 清晰的输出格式

### 方法 2：在浏览器中查看文档

直接在浏览器访问以下 URL：

1. **查看 API 使用说明**
   ```
   http://localhost:8788/api/chat/stream
   ```
   现在会返回 JSON 格式的使用说明（不再报错）

2. **FastAPI 交互式文档**
   ```
   http://localhost:8788/docs
   ```
   可以直接在浏览器中测试 API！

3. **查看所有端点**
   ```
   http://localhost:8788/
   ```

### 方法 3：使用 curl 命令

#### Linux/macOS
```bash
bash test_stream_api.sh
```

#### Windows
```cmd
test_stream_api.bat
```

## 📊 预期效果

运行 `python test_stream_api.py` 后，你会看到：

```
🚀 AI-SNS 流式聊天 API 测试工具

检查 API 服务健康状态...
✓ API 服务运行正常
  状态: healthy
  时间: 2025-01-09T18:20:30.123456

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
✓ 测试成功！共接收 32 个字符
============================================================
```

## 🔍 现在浏览器访问会返回什么？

现在当你在浏览器中访问 `http://localhost:8788/api/chat/stream` 时，会看到：

```json
{
  "message": "这是一个 POST 端点，用于流式聊天",
  "method": "POST",
  "url": "/api/chat/stream",
  "content_type": "application/json",
  "accept": "text/event-stream",
  "request_body": {
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "model": "gpt-4o-mini (可选)",
    "temperature": 1.0,
    "max_tokens": 4096
  },
  "example_curl": "curl -N -X POST http://localhost:8788/api/chat/stream ...",
  "test_script": "运行 python test_stream_api.py 进行测试"
}
```

这样就不会再报错了！🎉

## 📁 测试文件说明

我为你创建了以下测试文件：

| 文件 | 用途 | 平台 |
|------|------|------|
| `test_stream_api.py` | Python 测试脚本（推荐） | 全平台 |
| `test_stream_api.sh` | Shell 脚本 | Linux/macOS |
| `test_stream_api.bat` | 批处理脚本 | Windows |
| `TESTING_STREAM_API.md` | 详细测试指南 | 文档 |

## 🚀 下一步

1. **启动后端服务**（如果还没启动）：
   ```bash
   python api_server.py --port 8788
   ```

2. **运行测试**：
   ```bash
   python test_stream_api.py
   ```

3. **在浏览器中查看**：
   - http://localhost:8788/ （主页）
   - http://localhost:8788/docs （交互式文档）
   - http://localhost:8788/api/chat/stream （使用说明）

## 💡 提示

- 现在访问任何端点都不会报错，会返回有用的信息
- 使用 `/docs` 可以在浏览器中交互式测试所有 API
- Python 测试脚本最简单直观

## 📖 更多文档

- `TESTING_STREAM_API.md` - 完整测试指南
- `AI_CONFIG_QUICKSTART.md` - 配置说明
- `docs/AI_CHAT_REFACTORING.md` - 技术文档
