# 错误修复完成 - 快速指南

## ✅ 已修复的问题

### 1. ❌ `Illegal header value b'Bearer '`
**原因**: 数据库中有空的 API key 配置，优先级高于配置文件

**修复**:
- 改进了配置加载逻辑，只有非空 API key 才使用数据库配置
- 添加了 API key 检查，给出明确的错误提示

### 2. ❌ `connect ECONNREFUSED ::1:8788`
**原因**: Node.js 尝试使用 IPv6 (::1) 连接，但服务器只监听 IPv4

**修复**:
- Electron 前端改为明确使用 `127.0.0.1` 而非 `localhost`

## 🚀 现在该怎么做？

### 第一步：运行诊断工具

```bash
python diagnose.py
```

这个工具会自动检查：
1. ✓ 配置文件是否存在
2. ✓ API key 是否配置
3. ✓ API 服务器是否运行
4. ✓ 流式 API 是否正常

### 第二步：根据诊断结果修复

#### 如果显示 "API Key 未配置"

编辑 `ai_config.yaml` 文件，确认配置正确：

```yaml
ai:
  api_base: "https://api.chatanywhere.tech/v1"
  api_key: "sk-SVCuk9EAqrgUEvvh31PKxVIr1fZhwt5boDB2Hexw8vs2Bl26"  # 确保这个不为空
  model: "gpt-4o-mini"
```

#### 如果显示 "API 服务器未运行"

启动后端服务：
```bash
python api_server.py --port 8788
```

### 第三步：重新测试

**重启后端服务**（重要！）：
```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python api_server.py --port 8788
```

**运行测试**：
```bash
python test_stream_api.py
```

**重启 Electron 应用**：
```bash
npm start
```

## 📊 检查配置状态

访问以下 URL 查看当前配置：

```bash
# 在浏览器或使用 curl
curl http://localhost:8788/api/config/status
```

应该返回：
```json
{
  "has_api_key": true,
  "api_base": "https://api.chatanywhere.tech/v1",
  "model": "gpt-4o-mini",
  "api_key_preview": "sk-SVCuk9...",
  "config_file_exists": true,
  "recommendation": "配置正常"
}
```

## 🔍 查看后端日志

启动服务时，后端会显示使用的配置来源：

```
INFO:     Using AI config from ai_config.yaml
```

或

```
INFO:     Using AI config from database
```

如果看到这行，说明找到了空配置：
```
ERROR:    No valid AI config found! Please configure API key...
```

## ⚡ 快速测试流程

```bash
# 1. 诊断
python diagnose.py

# 2. 启动后端（新终端窗口）
python api_server.py --port 8788

# 3. 测试（另一个终端）
python test_stream_api.py

# 4. 启动 Electron
npm start
```

## 🆘 仍然有问题？

### 检查数据库配置

数据库中可能有空的配置，优先级高于配置文件。

查看数据库：
```bash
sqlite3 db/db.sqlite "SELECT id, name, api_key FROM aichat_cfg WHERE is_delete=0;"
```

如果有空的 api_key，删除或更新它：
```bash
# 删除空配置
sqlite3 db/db.sqlite "DELETE FROM aichat_cfg WHERE api_key='' OR api_key IS NULL;"

# 或更新为有效的 API key
sqlite3 db/db.sqlite "UPDATE aichat_cfg SET api_key='sk-your-key' WHERE id=1;"
```

### 清除环境变量

确保没有空的环境变量：
```bash
# Linux/macOS
unset OPENAI_API_KEY
unset OPENAI_API_BASE

# Windows PowerShell
Remove-Item Env:OPENAI_API_KEY
Remove-Item Env:OPENAI_API_BASE
```

## 📝 文件清单

已创建/修改的文件：

- ✅ `api_server.py` - 改进配置加载逻辑
- ✅ `electron/main.js` - 修复 IPv6 问题
- ✅ `diagnose.py` - 新增诊断工具
- ✅ `test_stream_api.py` - 测试脚本
- ✅ 新增 `/api/config/status` 端点

## 🎯 成功标志

当一切正常时，你会看到：

1. **诊断工具输出**:
   ```
   🎉 所有检查通过！系统运行正常。
   ```

2. **测试脚本输出**:
   ```
   ✓ 测试成功！共接收 XX 个字符
   ```

3. **Electron 正常运行**，可以与 AI 聊天

---

**现在就运行 `python diagnose.py` 开始诊断吧！** 🚀
