# Agent Settings 功能使用指南

## 概述

新的 Agent Settings 功能提供了完整的 Agent 配置界面，支持：
- Google A2A 协议的所有字段配置
- LLM 模型和角色选择
- 区块链钱包管理（创建和导入）

## 功能特性

### 1. 基本信息配置
- **Agent 名称**: Agent 的显示名称
- **描述**: Agent 的功能描述
- **LLM 模型**: 选择使用的大语言模型
- **角色配置**: 选择 Agent 的角色和系统提示词

### 2. A2A 协议配置 (Google A2A v0.3)

#### 端点配置
- **A2A 端点 URL**: Agent 的 A2A 协议访问地址
- **Agent 版本**: 当前 Agent 的版本号
- **协议版本**: A2A 协议版本（默认 0.3）

#### 能力配置 (Capabilities)
- **流式响应 (Streaming)**: 支持流式输出
- **推送通知 (Push Notifications)**: 支持异步任务通知
- **状态转换历史 (State Transition History)**: 记录状态变化历史

#### 输入输出模式
- **输入模式**: 支持的输入类型（文本、图像、音频、视频、文件）
- **输出模式**: 支持的输出类型（文本、图像、音频、视频、文件）

#### 提供者信息
- **提供者组织**: 提供 Agent 服务的组织名称
- **提供者 URL**: 组织的官方网站
- **文档 URL**: Agent 的文档地址
- **图标 URL**: Agent 的图标地址

### 3. 区块链钱包管理

#### 创建新钱包
1. 点击 "创建新钱包" 按钮
2. 系统会自动生成一个新的以太坊钱包
3. **重要**: 请务必保存显示的私钥，私钥丢失将无法恢复钱包！
4. 钱包地址会自动填充到配置中

#### 导入现有钱包
1. 点击 "导入钱包" 按钮
2. 在弹出的对话框中输入私钥（带或不带 0x 前缀均可）
3. 系统会验证私钥并导入钱包
4. 钱包地址会自动填充到配置中

## 使用方法

### 打开 Agent Settings 对话框

在 Electron 应用的 Agent 页面中：
1. 点击左侧边栏上方的 **"Setting"** 按钮
2. 配置对话框会弹出，显示三个页签：
   - **基本信息**
   - **A2A 协议**
   - **区块链钱包**

### 配置步骤

#### 步骤 1: 基本信息
1. 填写 Agent 名称（必填）
2. 填写描述（可选）
3. 选择 LLM 模型（必填）
4. 选择角色配置（必填）

#### 步骤 2: A2A 协议配置
1. 填写 A2A 端点 URL（必填，例如: `http://localhost:8788/a2a`）
2. 设置 Agent 版本和协议版本
3. 选择支持的能力（勾选相应的复选框）
4. 选择输入和输出模式（按住 Ctrl 可多选）
5. 填写提供者信息和文档 URL

#### 步骤 3: 区块链钱包
1. 如果没有钱包，点击 "创建新钱包" 并保存私钥
2. 如果已有钱包，点击 "导入钱包" 并输入私钥
3. 钱包地址会自动显示在输入框中

#### 步骤 4: 保存
点击对话框底部的 "保存" 或 "创建" 按钮，系统会：
- 验证必填字段
- 将配置保存到数据库
- 更新 Agent 列表

## API 接口

### 区块链钱包 API

#### 创建钱包
```
POST /api/wallet/create
Body: { "label": "Agent Wallet" }
Response: {
  "success": true,
  "data": {
    "address": "0x...",
    "public_key": "0x...",
    "private_key": "0x...",
    "warning": "请务必安全保存私钥！"
  }
}
```

#### 导入钱包
```
POST /api/wallet/import
Body: {
  "private_key": "0x...",
  "label": "Agent Wallet"
}
Response: {
  "success": true,
  "data": {
    "address": "0x...",
    "public_key": "0x..."
  }
}
```

#### 获取钱包列表
```
GET /api/wallet/list
Response: {
  "success": true,
  "data": [
    {
      "address": "0x...",
      "public_key": "0x...",
      "label": "Agent Wallet",
      "created_at": "2024-01-11T..."
    }
  ]
}
```

#### 获取钱包详情
```
GET /api/wallet/{address}
Response: {
  "success": true,
  "data": {
    "address": "0x...",
    "public_key": "0x...",
    "label": "Agent Wallet"
  }
}
```

### Agent 配置 API

#### 创建 Agent
```
POST /api/agent
Body: {
  "name": "GPT-4 助手",
  "description": "基于 GPT-4 的 AI 助手",
  "model_config_id": "cfg_xxx",
  "role_id": "role_xxx",
  "url": "http://localhost:8788/a2a",
  "version": "1.0.0",
  "protocol_version": "0.3",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": false
  },
  "default_input_modes": ["text"],
  "default_output_modes": ["text"],
  "wallet_address": "0x...",
  ...
}
```

#### 更新 Agent
```
PUT /api/agent/{agent_id}
Body: { 与创建 Agent 相同的字段 }
```

#### 获取 Agent 详情
```
GET /api/agent/{agent_id}
Response: {
  "success": true,
  "data": { Agent 配置对象 }
}
```

## 安全注意事项

### 私钥管理
1. **绝对不要泄露私钥**: 私钥相当于银行密码，任何人获取私钥都可以完全控制钱包
2. **安全存储**: 建议将私钥加密后存储在安全的地方
3. **定期备份**: 创建钱包后立即备份私钥
4. **不要截图**: 避免将包含私钥的截图保存到云端或不安全的位置

### API 安全
1. 区块链钱包功能需要安装依赖: `pip install web3 eth-account`
2. 私钥只在创建时返回一次，之后无法再次获取
3. 导入钱包时请在安全环境中操作

## 故障排查

### 钱包功能不可用
如果看到 "区块链钱包功能需要安装 web3 和 eth-account" 错误：
```bash
pip install web3 eth-account
```

### Agent 保存失败
1. 检查必填字段是否都已填写（名称、LLM 模型、角色、A2A URL）
2. 检查后端 API 服务器是否正常运行（http://localhost:8788）
3. 查看浏览器控制台和后端日志获取详细错误信息

### A2A 协议字段验证
确保：
- URL 格式正确（包含 http:// 或 https://）
- 版本号格式符合语义化版本规范（例如: 1.0.0）
- 至少选择一个输入模式和输出模式

## 技术架构

### 前端
- **AgentSettingsDialog.js**: 配置对话框组件
- **agentApi.js**: API 调用封装
- **agentHandlers.js**: 事件处理
- **agent-settings-dialog.css**: 样式文件

### 后端
- **backend/modules/agent/schemas.py**: Agent 数据模型（支持 A2A 协议字段）
- **backend/modules/wallet/router.py**: 钱包管理 API
- **blockchain/did/wallet.py**: 钱包核心功能

### A2A 协议支持
完整支持 Google A2A Protocol v0.3 规范：
- Agent Card 标准格式
- 能力声明 (Capabilities)
- 技能定义 (Skills)
- 安全方案 (Security Schemes)
- 输入输出模式定义

## 参考资料

- [Google A2A Protocol Specification](https://github.com/google/A2A)
- [以太坊钱包开发指南](https://docs.ethers.org/)
- [Web3.py 文档](https://web3py.readthedocs.io/)

## 更新日志

### v1.0.0 (2024-01-11)
- ✅ 实现完整的 Agent Settings 对话框
- ✅ 支持 Google A2A 协议 v0.3 所有字段
- ✅ 集成区块链钱包管理（创建和导入）
- ✅ LLM 模型和角色配置集成
- ✅ 响应式设计支持移动端
- ✅ 完整的 API 接口和错误处理
