# AI 配置快速开始

## 使用默认配置（最简单）

项目已经提供了默认的 AI 配置文件 `ai_config.yaml`，包含了可用的 API 配置：

- **API 地址**: `https://api.chatanywhere.tech/v1`
- **API 密钥**: 已预配置（测试用）
- **模型**: `gpt-4o-mini`

**你无需任何配置即可直接使用！**

只需：

```bash
# 1. 安装依赖
pip install -r requirements_platform.txt

# 2. 启动后端服务
python api_server.py --port 8788

# 3. 启动 Electron 应用
npm start
```

## 使用自己的 API 密钥

如果你想使用自己的 OpenAI API 密钥：

1. **确保配置文件存在**：
   - 项目根目录应该已经有 `ai_config.yaml` 文件
   - 如果没有，复制模板：`cp ai_config.yaml.example ai_config.yaml`

2. **编辑配置文件**：
   ```bash
   # 使用任何文本编辑器打开
   nano ai_config.yaml
   # 或
   code ai_config.yaml
   ```

3. **修改配置**：
   ```yaml
   ai:
     api_base: "https://api.openai.com/v1"
     api_key: "sk-你的API密钥"  # 替换这里
     model: "gpt-4o-mini"
     temperature: 1.0
     max_tokens: 4096
   ```

4. **重启后端服务**：
   ```bash
   python api_server.py --port 8788
   ```

## 配置优先级

系统按以下优先级读取配置：

1. **数据库配置**（最高优先级）
2. **环境变量**
3. **配置文件** (`ai_config.yaml`)

如果你没有在数据库或环境变量中配置，系统会自动使用 `ai_config.yaml` 中的配置。

## 查看当前使用的配置

启动后端服务时，查看控制台日志：

```
INFO:     Using AI config from ai_config.yaml
```

或

```
INFO:     Using AI config from database
```

或

```
INFO:     Using AI config from environment variables
```

这会告诉你当前使用的是哪个配置源。

## 安全说明

⚠️ **重要**：`ai_config.yaml` 文件已添加到 `.gitignore`，不会被提交到 Git 仓库。

- ✅ 可以安全地在本地文件中保存 API 密钥
- ✅ 不会意外泄露到版本控制系统
- ✅ 每个开发者可以使用自己的配置

## 故障排除

### 问题：找不到配置文件

**解决方案**：
```bash
cp ai_config.yaml.example ai_config.yaml
```

### 问题：API 密钥无效

**症状**：后端日志显示 401 或 403 错误

**解决方案**：
1. 检查 `ai_config.yaml` 中的 `api_key` 是否正确
2. 确认 API 密钥有足够的余额/配额
3. 如果使用默认配置，可能是测试密钥额度用完了，请使用自己的密钥

## 支持的 API 提供商

配置文件支持所有兼容 OpenAI API 格式的服务：

- OpenAI (`https://api.openai.com/v1`)
- OpenAI 代理 (`https://api.chatanywhere.tech/v1`)
- DeepSeek (`https://api.deepseek.com/v1`)
- 其他兼容 OpenAI API 的服务

只需修改 `api_base` 和 `api_key` 即可切换。
