# Agent Settings 完整验证指南

## 🚀 快速验证步骤

### 步骤 1: 重启后端服务器

```bash
# 停止当前运行的服务器（按 Ctrl+C）
# 然后重新启动
cd /mnt/c/dev/agi-ev/ai-sns-el
python api_server.py
```

等待看到以下日志：
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8788 (Press CTRL+C to quit)
```

### 步骤 2: 测试 API 端点

在新终端中运行以下命令：

```bash
# 测试 LLM 配置 API
curl http://localhost:8788/api/agent/llm-configs

# 测试 Role 配置 API
curl http://localhost:8788/api/agent/role-configs

# 测试 Agent API
curl http://localhost:8788/api/agent

# 测试钱包 API
curl http://localhost:8788/api/wallet/list
```

### 步骤 3: 启动 Electron 应用

```bash
# 在项目根目录
npm start
```

### 步骤 4: 测试 Agent Settings 功能

1. 在 Electron 应用中，点击左侧导航的 **"Agent"** 图标
2. 点击左侧边栏顶部的 **"Setting"** 按钮（齿轮图标）
3. 检查 Agent Settings 对话框是否正常打开

#### 预期结果：
- ✅ 对话框正常弹出
- ✅ 显示三个页签：基本信息、A2A 协议、区块链钱包
- ✅ LLM 模型下拉框显示可用的模型
- ✅ 角色配置下拉框显示可用的角色
- ✅ 浏览器控制台没有 422 错误

## 📋 详细功能测试

### 测试 1: 创建新 Agent

#### 1.1 基本信息页签
- [ ] 输入 Agent 名称: `测试 Agent`
- [ ] 输入描述: `这是一个测试 Agent`
- [ ] 选择 LLM 模型（确保下拉框有选项）
- [ ] 选择角色配置（确保下拉框有选项）

#### 1.2 A2A 协议页签
- [ ] 输入 A2A 端点 URL: `http://localhost:8788/a2a`
- [ ] Agent 版本: `1.0.0`
- [ ] 协议版本: `0.3`
- [ ] 勾选能力：
  - [ ] 流式响应
  - [ ] 推送通知
- [ ] 选择输入模式: `text`（按住 Ctrl 可多选）
- [ ] 选择输出模式: `text`
- [ ] 提供者组织: `AI-SNS Platform`
- [ ] 提供者 URL: `https://ai-sns.com`

#### 1.3 区块链钱包页签
- [ ] 点击 "创建新钱包" 按钮
- [ ] 查看生成的钱包地址
- [ ] 查看私钥（务必复制保存！）
- [ ] 检查安全警告是否显示

#### 1.4 保存 Agent
- [ ] 点击 "创建" 按钮
- [ ] 看到成功提示
- [ ] Agent 出现在列表中

### 测试 2: 导入现有钱包

1. 再次打开 Setting 对话框
2. 切换到 "区块链钱包" 页签
3. 点击 "导入钱包"
4. 输入测试私钥（可以使用刚才创建的私钥）
5. 确认导入成功
6. 钱包地址正确显示

### 测试 3: 编辑 Agent

1. （将来实现）点击 Agent 列表中的某个 Agent
2. 修改配置
3. 保存更新

### 测试 4: 查看 API 数据

使用浏览器或 curl 查看创建的 Agent 数据：

```bash
# 获取所有 Agent
curl http://localhost:8788/api/agent

# 获取特定 Agent（假设 ID 为 1）
curl http://localhost:8788/api/agent/1
```

预期响应包含所有字段：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "测试 Agent",
    "description": "这是一个测试 Agent",
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
    "wallet_address": "0x...",
    "is_active": true
  }
}
```

## 🔍 故障排查

### 问题 1: 模型和角色下拉框为空

**症状**: Setting 对话框中 LLM 模型和角色下拉框显示"请选择..."但没有选项

**原因**: 数据库中没有 LLM 配置或角色配置数据

**解决方案**:
1. 确保数据库初始化成功
2. 手动添加测试数据：

```bash
# 添加测试 LLM 配置
curl -X POST http://localhost:8788/api/agent/llm-configs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-4 测试",
    "provider": "openai",
    "api_base": "https://api.openai.com/v1",
    "model": "gpt-4",
    "is_active": true
  }'

# 添加测试角色配置
curl -X POST http://localhost:8788/api/agent/role-configs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "通用助手",
    "system_prompt": "你是一个乐于助人的 AI 助手。",
    "category": "assistant",
    "is_active": true
  }'
```

### 问题 2: 仍然看到 422 错误

**症状**: 浏览器控制台仍显示 422 错误

**解决方案**:
1. 确认已重启后端服务器
2. 清除浏览器缓存或硬刷新（Ctrl+Shift+R）
3. 重启 Electron 应用
4. 检查服务器日志查看详细错误信息

### 问题 3: 钱包创建失败

**症状**: 点击"创建新钱包"后出现错误

**原因**: 缺少区块链相关依赖

**解决方案**:
```bash
pip install web3 eth-account
```

### 问题 4: Agent 保存失败

**症状**: 点击"保存"后返回 500 错误

**排查步骤**:
1. 查看后端日志获取详细错误信息
2. 确认必填字段都已填写
3. 检查数据库连接是否正常

## ✅ 验证清单

在完成所有测试后，确认以下项目：

### API 端点
- [ ] GET `/api/agent/llm-configs` 返回 200
- [ ] GET `/api/agent/role-configs` 返回 200
- [ ] GET `/api/agent` 返回 200
- [ ] POST `/api/agent` 创建成功
- [ ] GET `/api/agent/{id}` 返回完整数据
- [ ] PUT `/api/agent/{id}` 更新成功
- [ ] POST `/api/wallet/create` 创建钱包成功
- [ ] POST `/api/wallet/import` 导入钱包成功

### 前端功能
- [ ] Agent Settings 对话框正常打开
- [ ] 三个页签都可以切换
- [ ] LLM 模型下拉框有选项
- [ ] 角色配置下拉框有选项
- [ ] 创建钱包功能正常
- [ ] 导入钱包功能正常
- [ ] 保存 Agent 成功
- [ ] 浏览器控制台无错误

### 数据持久化
- [ ] 创建的 Agent 保存到数据库
- [ ] 刷新页面后 Agent 仍在列表中
- [ ] 钱包地址正确存储
- [ ] A2A 协议字段正确存储

### Google A2A 协议
- [ ] 所有必需字段都可以配置
- [ ] 能力配置正确保存
- [ ] 输入输出模式正确保存
- [ ] 提供者信息正确保存

## 🎯 成功标准

所有以下条件都满足才算验证成功：

1. ✅ 后端服务器正常启动，无错误日志
2. ✅ 所有 API 端点返回正确响应（无 422 错误）
3. ✅ Agent Settings 对话框完整显示
4. ✅ 可以成功创建包含所有字段的 Agent
5. ✅ 可以成功创建和导入区块链钱包
6. ✅ 创建的 Agent 在列表中显示
7. ✅ 数据库中正确存储所有信息
8. ✅ 浏览器控制台无错误

## 📸 截图检查点

建议在以下步骤截图存档：

1. Agent Settings 对话框 - 基本信息页签
2. Agent Settings 对话框 - A2A 协议页签
3. Agent Settings 对话框 - 区块链钱包页签（显示创建的钱包）
4. Agent 列表显示新创建的 Agent
5. API 返回的完整 Agent 数据（JSON）

## 🔄 下一步

验证成功后，可以：

1. 创建更多 Agent 测试批量操作
2. 测试 Agent 编辑功能（待实现）
3. 测试 Agent 删除功能
4. 集成 Agent 与聊天功能
5. 测试 A2A 协议端点
6. 测试区块链钱包的实际使用

---

**完成时间**: ___________

**测试人员**: ___________

**状态**: [ ] 通过  [ ] 失败  [ ] 部分通过

**备注**:
