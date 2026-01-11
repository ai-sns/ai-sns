# Agent Settings 功能快速演示

## 快速开始

### 1. 启动应用

```bash
# 启动后端 API 服务器
cd /mnt/c/dev/agi-ev/ai-sns-el
python api_server.py

# 在另一个终端启动 Electron 应用
npm start
```

### 2. 打开 Agent Settings

1. 在 Electron 应用中，点击左侧导航栏的 "Agent" 图标
2. 在 Agent 页面左侧边栏顶部，点击 **"Setting"** 按钮（齿轮图标）
3. Agent Settings 配置对话框会弹出

### 3. 配置示例

#### 示例 1: 创建一个基础的 GPT-4 Agent

**基本信息页签:**
- Agent 名称: `GPT-4 智能助手`
- 描述: `基于 GPT-4 的通用 AI 助手，可以回答各类问题`
- LLM 模型: 选择 `GPT-4` 或任何已配置的模型
- 角色配置: 选择 `通用助手` 或任何已配置的角色

**A2A 协议页签:**
- A2A 端点 URL: `http://localhost:8788/a2a`
- Agent 版本: `1.0.0`
- 协议版本: `0.3`
- 能力: 勾选 `流式响应` 和 `推送通知`
- 输入模式: 选择 `text`
- 输出模式: 选择 `text`
- 提供者组织: `AI-SNS Platform`
- 提供者 URL: `https://ai-sns.com`

**区块链钱包页签:**
- 点击 "创建新钱包" 按钮
- 系统会生成新钱包并显示地址和私钥
- **重要**: 复制并保存私钥到安全的地方！

点击 "创建" 按钮完成配置。

#### 示例 2: 创建一个多模态 Agent

**基本信息:**
- Agent 名称: `多模态 AI 助手`
- 描述: `支持文本、图像、音频等多种输入输出的 AI 助手`
- LLM 模型: 选择支持多模态的模型（如 GPT-4V）
- 角色配置: 选择 `多模态助手`

**A2A 协议:**
- A2A 端点 URL: `http://localhost:8788/a2a`
- 能力: 勾选所有三项
- 输入模式: 选择 `text`, `image`, `audio`（按住 Ctrl 多选）
- 输出模式: 选择 `text`, `image`, `audio`
- 文档 URL: `https://docs.ai-sns.com/multimodal`
- 图标 URL: `https://ai-sns.com/icons/multimodal.png`

**区块链钱包:**
- 如果已有钱包，点击 "导入钱包"
- 输入私钥: `0x1234...` （你的实际私钥）
- 系统会验证并导入钱包

保存配置。

### 4. 测试钱包功能

#### 创建钱包测试

使用 API 直接测试：

```bash
# 创建新钱包
curl -X POST http://localhost:8788/api/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"label": "Test Wallet"}'

# 响应示例:
{
  "success": true,
  "data": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4",
    "public_key": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4",
    "private_key": "0x1234567890abcdef...",
    "label": "Test Wallet",
    "warning": "请务必安全保存私钥！私钥丢失将无法恢复钱包！"
  }
}
```

#### 导入钱包测试

```bash
curl -X POST http://localhost:8788/api/wallet/import \
  -H "Content-Type: application/json" \
  -d '{
    "private_key": "0x1234567890abcdef...",
    "label": "Imported Wallet"
  }'
```

#### 查看钱包列表

```bash
curl http://localhost:8788/api/wallet/list

# 响应:
{
  "success": true,
  "data": [
    {
      "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4",
      "public_key": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4",
      "label": "Test Wallet",
      "created_at": "2024-01-11T10:30:00"
    }
  ]
}
```

### 5. 查看 A2A Agent Card

创建 Agent 后，可以通过 A2A 端点查看 Agent Card：

```bash
# 假设 Agent ID 为 1
curl http://localhost:8788/a2a/agents/1/card

# 响应会是标准的 A2A Agent Card JSON
{
  "name": "GPT-4 智能助手",
  "description": "基于 GPT-4 的通用 AI 助手",
  "url": "http://localhost:8788/a2a",
  "version": "1.0.0",
  "protocolVersion": "0.3",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": false
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "securitySchemes": {
    "apiKey": {
      "type": "apiKey",
      "in": "header",
      "name": "X-API-Key"
    }
  },
  "provider": {
    "organization": "AI-SNS Platform",
    "url": "https://ai-sns.com"
  }
}
```

## 常见使用场景

### 场景 1: 为不同用户创建专属 Agent

1. 点击 "Setting" 创建新 Agent
2. 设置不同的名称、描述和钱包地址
3. 每个 Agent 可以有独立的 LLM 模型和角色配置
4. 钱包地址用于身份识别和交易管理

### 场景 2: 配置企业级 Agent

1. 使用企业的钱包地址
2. 配置企业提供者信息
3. 添加详细的文档 URL 和图标
4. 设置适当的能力和输入输出模式

### 场景 3: 测试和开发

1. 创建多个测试 Agent
2. 使用不同的配置组合
3. 通过 A2A 协议接口测试 Agent 的行为
4. 验证钱包集成和交易功能

## 演示视频脚本

### 第 1 步: 打开配置对话框 (10 秒)
"首先，点击 Agent 页面左侧的 Setting 按钮"

### 第 2 步: 填写基本信息 (20 秒)
"在基本信息页签，输入 Agent 名称，选择 LLM 模型和角色"

### 第 3 步: 配置 A2A 协议 (30 秒)
"切换到 A2A 协议页签，填写端点 URL，选择支持的能力和输入输出模式"

### 第 4 步: 创建钱包 (20 秒)
"切换到区块链钱包页签，点击创建新钱包，复制并保存私钥"

### 第 5 步: 保存配置 (10 秒)
"点击保存按钮，Agent 配置完成，可以在列表中看到新创建的 Agent"

## 验证清单

配置完成后，验证以下内容：

- [ ] Agent 出现在 Agent 列表中
- [ ] 可以通过 API 获取 Agent 详情
- [ ] A2A Agent Card 可以正常访问
- [ ] 钱包地址正确显示
- [ ] 可以使用钱包地址进行身份验证
- [ ] 所有必填字段都已正确保存
- [ ] LLM 模型和角色配置正确关联

## 下一步

配置完成后，可以：
1. 使用配置好的 Agent 进行对话
2. 通过 A2A 协议与其他 Agent 通信
3. 使用钱包地址进行区块链交易
4. 导出 Agent Card 供其他系统使用

## 故障排查

### 问题 1: 钱包创建失败
```
错误: 区块链钱包功能需要安装 web3 和 eth-account

解决:
pip install web3 eth-account
```

### 问题 2: Agent 保存失败
```
错误: 请输入 Agent 名称 / 请选择 LLM 模型

解决:
确保所有必填字段（标记 * 的）都已填写
```

### 问题 3: 私钥无法显示
```
原因: 私钥只在创建时显示一次

解决:
如果没有保存私钥，需要重新创建新钱包或导入已有钱包
```

## 技术支持

如有问题，请：
1. 查看完整文档: `AGENT_SETTINGS_GUIDE.md`
2. 检查浏览器控制台日志
3. 查看后端日志: `api_server.py` 的输出
4. 提交 Issue 到 GitHub 仓库

---

**祝你使用愉快！** 🎉
