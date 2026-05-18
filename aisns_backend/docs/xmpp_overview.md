# AI-SNS-EL — XMPP / A2A 全链路技术文档

> 本文按时序串讲 ai-sns-el 中 XMPP 相关的全部功能，覆盖启动、Service Discovery、PEP、PubSub、Ad-hoc Command (XEP-0050)、A2A (Agent-to-Agent, JSON-RPC over XEP-0050)，并阐明前端 / 后端 / 地图 / A2A 子服务的协同方式。所有结论都附带文件路径与行号，便于核对。
>
> 关键依赖：`slixmpp` (`venv/Lib/site-packages/slixmpp/`) + 内置插件 XEP-0030、XEP-0004、XEP-0050、XEP-0060、XEP-0163、XEP-0199、XEP-0363。

---

## 0. 模块鸟瞰

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Electron 前端 (aisns_frontend)                                          │
│   InitializationWizard / SNSAdvancedDialog / SNSSidebar / map.html         │
│                              │ HTTP + WebSocket                          │
│                              ▼                                           │
│  FastAPI 后端 (aisns_backend/api_server.py)                              │
│   ├─ /api/sns/...  (router.py)                                           │
│   ├─ /api/system/init-wizard/... (system/router.py)                      │
│   └─ /a2a/{agent_id}/.well-known/agent-card.json (本机 agent 卡牌出口)   │
│        │                                                                 │
│        ▼                                                                 │
│   XMPPClientManager → slixmpp ClientXMPP                                 │
│        │                                                                 │
│        ├─ XEP-0030 disco / XEP-0163 PEP / XEP-0050 ad-hoc / XEP-0060     │
│        └─ XMPPA2AManager（注册 / 发布 / 路由 / 远程调用）                │
│                                                                          │
│  A2A HTTP 子进程 (a2aserver/server.py, 端口 8789)                        │
│   ├─ /.well-known/agent-card.json                                        │
│   ├─ /a2a/  (JSON-RPC 2.0: tasks/send)                                   │
│   └─ SQLite a2aserver/data/a2a.sqlite (my_card, received_cards)          │
└──────────────────────────────────────────────────────────────────────────┘
```

注意：项目中存在 **两份 agent card**：
1. **业务名片**（business card）：name/company/title/email/xmpp/website/phone — 储存于 `a2aserver/data/a2a.sqlite`，用于"换名片"。
2. **A2A Agent Card**：A2A 协议的 agent 描述 JSON（含 skills/capabilities），由后端 `/a2a/{agent_id}/.well-known/agent-card.json` 或外部 URL 返回，发布到 PEP 节点 `urn:xmpp:a2a:agentcard`。

下文统一区分。

---

## 1. 启动时序

### 1.1 触发：FastAPI startup 事件

后端 `uvicorn` 启动时，FastAPI 调度 `@app.on_event("startup")`：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:836-892
@app.on_event("startup")
async def startup_event():
    ...
    a2a_enabled = getattr(sys_cfg, 'a2a_server_enabled', False)
    if a2a_enabled:
        _start_a2a_server_subprocess()         # 启动 A2A HTTP 子进程（8789）
    ...
    if sns_router:
        from runtime.apps.sns.xmpp_client import XMPPClientManager
        xmpp_manager = XMPPClientManager.get_instance()
        await xmpp_manager.start()             # 启动 XMPP 客户端
```

A2A 子进程通过 `subprocess.Popen` 拉起 `@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py`，详见 `@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:928-1002`。它做的事：
- 暴露 `GET /.well-known/agent-card.json` 与 `GET /a2a/.well-known/agent-card.json` (`@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py:69-78`)
- 暴露 `POST /a2a/` JSON-RPC 2.0 endpoint，仅支持 `tasks/send` (`@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py:83-138`)
- 暴露名片管理 REST `/api/my-card`、`/api/received-cards`

### 1.2 `XMPPClientManager.start()` 建立 slixmpp 连接

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:888-930
async def start(self):
    db = get_db_sync()
    config = db.query(AISnsCfg).filter(AISnsCfg.is_delete == False).first()
    ...
    self._client = XMPPClient(config.account, config.password, db)
    ...
    self._client.connect()
    self._reconnect_task = loop.create_task(self._run_client())
```

`XMPPClient.__init__` 注册所有 XEP 插件：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:33-52
self.register_plugin('xep_0030')   # Service Discovery
self.register_plugin('xep_0004')   # Data Forms
self.register_plugin('xep_0050')   # Ad-hoc Commands
self.register_plugin('xep_0060')   # PubSub
self.register_plugin('xep_0163')   # PEP (Personal Eventing Protocol)
self.register_plugin('xep_0199', {'keepalive': False})  # XMPP Ping
self.register_plugin('xep_0363')   # HTTP File Upload
```

事件回调注册：`session_start / message / presence_subscribe / presence_subscribed / roster_update / disconnected / connection_failed` (`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:24-31`)。

### 1.3 `session_start` — XMPP 会话就绪后的工作

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:70-99
async def on_session_start(self, event):
    self.send_presence()                       # 1) 上线 presence 广播
    await self.get_roster()                    # 2) 拉花名册
    ...
    self._roster_cleanup_task = asyncio.create_task(self._delayed_roster_cleanup())  # 3) 20s 后清理超量好友 (>250)
    self.heartbeat_task = asyncio.create_task(self.heartbeat())                        # 4) 心跳 (30s ping, 10s 超时, 3 次失败重连)
    from runtime.apps.sns.xmpp_a2a import XMPPA2AManager
    self._a2a_manager = XMPPA2AManager(self)
    asyncio.create_task(self._a2a_manager.initialize())                                # 5) 初始化 A2A
```

### 1.4 `XMPPA2AManager.initialize()` — A2A 子系统启动

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:970-1002
async def initialize(self):
    # ① 取本机 A2A agent card：先 inline (aisns_cfg.memo.a2a_config.agent_card)，否则按 URL 拉取
    a2a_config = self._load_a2a_config()
    inline_card = a2a_config.get('agent_card')
    if inline_card and isinstance(inline_card, dict) and any(inline_card.values()):
        self._agent_card = inline_card
    else:
        await self.fetch_agent_card()           # HTTP GET agent_cfg.memo.agent_card_url

    # ② 注册 disco 特性
    self.register_disco_features()

    # ③ 发布 PEP
    await self.publish_agent_card_pep()

    # ④ 注册 Ad-hoc 命令
    self.register_adhoc_commands()
```

下面分别说清这四步。

---

## 2. 启动了哪些内容（详单）

| 子系统 | 文件:行 | 功能 |
| --- | --- | --- |
| `XMPPClientManager` 单例 + 重连循环（指数回退，5→300s） | `xmpp_client.py:792-994` | 维持长连接、断线重连、热重启凭据 |
| `XMPPClient` (slixmpp.ClientXMPP) | `xmpp_client.py:16-789` | XMPP 协议栈 |
| 心跳 `heartbeat()` | `xmpp_client.py:548-570` | 每 30s ping，3 次失败触发重连 |
| Roster 清理 `cleanup_roster_if_needed` | `xmpp_client.py:185-286` | 启动 20s 后；>250 联系人按 `last_message_time` 清理 |
| 入站消息 `on_message` | `xmpp_client.py:288-413` | 写库 → WebSocket 广播 → 转交 AI Social Engine |
| 订阅协议 `on_presence_subscribe / subscribed` | `xmpp_client.py:424-461` | 双向自动接受 + 等待器机制 `ensure_mutual_subscription` (`:618-672`) |
| `XMPPA2AManager` | `xmpp_a2a.py` | A2A 全部能力 |
| Ad-hoc 命令注册中心 | `a2a_commands/__init__.py` | 自动发现 builtin + 用户脚本 + DB config |
| 内置命令：换名片 | `a2a_commands/exchange_business_card.py` | node = `urn:xmpp:a2a:cmd:exchange_business_card` |
| 内置命令：A2A JSON-RPC | `a2a_commands/a2a_task.py` | node = `urn:xmpp:a2a:cmd:tasks` |
| A2A HTTP 子进程 | `a2aserver/server.py` (8789) | JSON-RPC `tasks/send` + 名片库 |
| 业务名片库 | `a2aserver/db.py` | SQLite `a2aserver/data/a2a.sqlite` |

---

## 3. 启动时序图（合并版）

```
Electron 前端                  FastAPI 后端                       slixmpp / XMPP Server
     │                              │                                     │
     │ launch app                   │                                     │
     │─────────────────────────────►│                                     │
     │                              │ startup_event (api_server.py:837)   │
     │                              │ ─ a2a_enabled? subprocess(8789)     │
     │                              │ ─ XMPPClientManager.start()         │
     │                              │      读 aisns_cfg(account,password) │
     │                              │      slixmpp.ClientXMPP.connect ───►│
     │                              │◄──────  TLS + SASL + session_start  │
     │                              │ on_session_start (xmpp_client:70)   │
     │                              │   send_presence + get_roster ──────►│
     │                              │   schedule heartbeat (30s ping)     │
     │                              │   XMPPA2AManager.initialize()       │
     │                              │     load agent card                 │
     │                              │     disco.add_feature(...) ────────►│
     │                              │     xep_0163.publish PEP node ─────►│
     │                              │     xep_0050.add_command(...) (本地)│
     │                              │                                     │
     │ WebSocket /ws ◄──── new_message / contact_upserted 推送  ◄────────│
```

---

## 4. 发布"自己的 XMPP Agent Card"

### 4.1 何时

- 启动后 `session_start → XMPPA2AManager.initialize()` 调用 `publish_agent_card_pep()`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:211-257`）。
- 用户在 SNSAdvancedDialog 修改 a2a_config 后，`service_async.update_ai_chat_config()` 调度热重载：
  ```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\service_async.py:1612-1627
  if credentials_changed:
      asyncio.create_task(xmpp_mgr.restart())
  elif _a2a_config is not None:
      asyncio.create_task(a2a.reload_a2a())
  ```
  `reload_a2a()`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:926-968`）会清空已注册命令并重跑 `initialize()`，重新发布 PEP。

### 4.2 卡片来源

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:64-95
def _get_agent_card_url(self):
    config = db.query(AISnsCfg)...        # aisns_cfg.agent_id
    agent = db.query(AgentCfg).filter_by(id=config.agent_id).first()
    extra_data = json.loads(agent.memo)
    return extra_data.get('agent_card_url')
```

优先级：
1. **inline**：`aisns_cfg.memo.a2a_config.agent_card`（前端 `SNSAdvancedDialog` 的"Agent Card" 表单写入，`@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\sns\SNSAdvancedDialog.js:1281-1336`）。
2. **URL fetch**：`agent_cfg.memo.agent_card_url`，由 `AgentSettingsDialog` 配置（`@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\agent\AgentSettingsDialog.js:227`）。常见的 URL 是本机暴露的 `/a2a/{agent_id}/.well-known/agent-card.json`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:321-326`）或 A2A 子进程的 8789。

`fetch_agent_card()` 使用 `urllib` 同步 GET，避免 slixmpp asyncio 与 httpx 在 Windows 上事件循环冲突，并把 `localhost` 替换为 `127.0.0.1` 防止 IPv6 解析问题（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:97-157`，含 5 次重试 backoff）。

### 4.3 协议：XEP-0030 + XEP-0163 (PEP) + XEP-0060 (PubSub 回退)

**Service Discovery 广告的 features**：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:33-36
A2A_FEATURE_NS = "urn:xmpp:a2a:1"
A2A_BUSINESS_CARD_NS = "urn:xmpp:a2a:business_card:1"
A2A_PEP_NODE = "urn:xmpp:a2a:agentcard"
```

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:191-205
added = [
    A2A_FEATURE_NS,
    A2A_BUSINESS_CARD_NS,
    "http://jabber.org/protocol/commands",
]
for ns in added:
    disco.add_feature(ns)
```

**PEP 发布**：把 agent card JSON 编码为 `<agentcard xmlns='urn:xmpp:a2a:agentcard'>{json}</agentcard>` payload，发布到当前 bare JID 的 PEP 节点：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:218-252
item = ET.Element("{%s}agentcard" % A2A_PEP_NODE)
item.text = json.dumps(self._agent_card, ensure_ascii=False)
pep = self.client['xep_0163']
await pep.publish(item, node=A2A_PEP_NODE, id="current")  # 主路径
# 失败回退到 xep_0060.publish(bare_jid, node, payload=item, id="current")
```

`id="current"` 是 PEP 的典型用法——只保留一条最新条目。任何已 `subscribed` 的好友收到 PEP `+notify` 都能拿到 agent card。

---

## 5. 获取对方的 XMPP Agent Card

### 5.1 何时

由 `MapTaskManager._fetch_peer_agent_card()` 触发，位于 AI 引擎 "tool_check_review" 流程内（决定是否要调用对方工具时）：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\map_task_manager.py:1250-1278
card_json = await self._fetch_peer_agent_card()
...
discovered_commands = await a2a_mgr.discover_peer_adhoc_commands(peer_jid, agent_card=card_dict)
```

### 5.2 双通道（HTTP 优先 + XMPP PEP 回退）

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\map_task_manager.py:968-1039
async def _fetch_peer_agent_card(self) -> str:
    # 路径 A：HTTP — 通过技能 fetch_agent_card 调对方 a2a_endpoint
    endpoint = (active.get("a2a_endpoint") or "").strip()
    if endpoint:
        svc = get_docskills_service()
        result = await svc.run_skill("fetch_agent_card", {"url": endpoint})
        ...
        if parsed.get("ok"): return parsed.get("card")

    # 路径 B：XMPP PEP — 直接读对方 PEP 节点
    peer_jid = (active.get("account") or "").strip()
    a2a_mgr = getattr(client, "_a2a_manager", None)
    card_dict = await a2a_mgr.fetch_peer_agent_card_pep(peer_jid)
```

PEP 实现：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:460-529
async def fetch_peer_agent_card_pep(self, peer_jid):
    pubsub = self.client['xep_0060']
    iq = await asyncio.wait_for(
        pubsub.get_items(bare_jid, A2A_PEP_NODE, max_items=1),
        timeout=10,
    )
    for item in iq['pubsub']['items']['substanzas']:
        payload_el = ...  # 取首个有 text 的子节点
        card = json.loads(payload_el.text)
        return card
```

所以无论对端是不是 ai-sns-el 实现，只要它把 `urn:xmpp:a2a:agentcard` 节点开放给我，就能拿到。

---

## 6. Service Discovery（XEP-0030）的具体玩法

发现对端能力：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:437-456
async def discover_peer_a2a(self, target_jid):
    info = await self.client['xep_0030'].get_info(jid=target_jid)
    features = info['disco_info']['features']
    return A2A_FEATURE_NS in features or A2A_BUSINESS_CARD_NS in features
```

发现对端命令列表（XEP-0050 disco#items 标准 query）：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:809-879
async def discover_peer_adhoc_commands(self, peer_jid, agent_card=None):
    # 源 1：agent card.skills（HTTP / PEP 已拿到）
    for skill in agent_card.get("skills", []):
        node = self._derive_adhoc_node_from_skill(skill)
        ...
    # 源 2：disco#items 取 commands
    items_iq = await disco.get_items(
        jid=candidate_jid,
        node="http://jabber.org/protocol/commands",
    )
    for item in items_iq['disco_items']['items']:
        node = item[1]; name = item[2] or ""
```

`_derive_adhoc_node_from_skill` 的规则（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:792-805`）：
- skill 里如有显式字段 `xmpp_adhoc_node / adhoc_node / command_node / node`，直接使用；
- 否则若 `skill.id` 是 URI（`urn:`/`://`）直接用；
- 否则拼成 `urn:xmpp:a2a:cmd:{skill_id}`。

调用方会尝试 roster 中所有 resource，再回退到 bare JID（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:881-922` 的 `_get_all_resources`），以应对多端登录场景。

---

## 7. Ad-hoc Command（XEP-0050）：自己注册 + 调对端 + 处理对端入站

### 7.1 自己注册（让别人调我）

三源合并：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:293-387
1. discover_commands()      # 扫描 a2a_commands/*.py (builtin)
                            # 扫描 aisns_backend/scripts/a2a_commands/*.py (用户插件)
2. build_config_commands()  # aisns_cfg.memo.a2a_config.adhoc_commands (DB 配置)
3. 合并、去重、按 enabled 过滤
4. xep_0050.add_command(node, name, handler=_make_execute_handler(cmd))
```

每个命令是 `AdhocCommand` 子类，必须提供 `node`、`name`，并实现两阶段：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\base.py:38-119
class AdhocCommand:
    async def handle_execute(self, iq, session, ctx): ...   # 阶段 1：返回表单
    async def handle_submit(self, payload, session, ctx): ... # 阶段 2：处理并返回结果
```

注册时 `XMPPA2AManager._make_execute_handler` 把 `cmd.handle_execute` 包成 slixmpp 期望的 coroutine，并把 `cmd.handle_submit` 挂在 `session['next']` 上：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:389-426
async def _execute_handler(iq, session):
    session = await cmd.handle_execute(iq, session, ctx)
    session['next'] = self._make_submit_handler(cmd)
    return session
```

`CommandContext` 注入 `xmpp_client` 与 `make_form()`（XEP-0004 数据表单工厂）（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\base.py:14-35`）。

**内置命令**：
- `exchange_business_card.py` — 见 §9
- `a2a_task.py` — 见 §10
- 用户脚本可放在 `aisns_backend/scripts/a2a_commands/`，自动热重载（每次 `register_adhoc_commands` 都 `importlib.reload`，`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\__init__.py:140-161`）。
- DB config 类型用 `TemplateCommand` 包装，支持 `{{var}}` 模板替换（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\base.py:122-173`）。

### 7.2 对方调我（入站时序）

```
对端                            本机 slixmpp                XMPPA2AManager + Plugin
  │ <iq type=set> command       │                            │
  │  node=...  action=execute   │                            │
  │────────────────────────────►│                            │
  │                             │ xep_0050 路由 node ───────►│ _execute_handler
  │                             │                            │   handle_execute()
  │                             │                            │   返回 form (XEP-0004)
  │◄──────────  <command status=executing> + form  ──────────│
  │                             │                            │
  │ <iq type=set> command       │                            │
  │  action=complete + payload  │                            │
  │────────────────────────────►│ session.next ─────────────►│ _submit_handler
  │                             │                            │   handle_submit(payload)
  │                             │                            │   返回 result form
  │◄────────── <command status=completed> + result ──────────│
```

### 7.3 我调对方（出站调用：通用入口）

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:534-709
async def call_adhoc_command(self, peer_jid, command_node, form_data=None, inspect_only=False, ...):
    candidates = self._get_all_resources(peer_jid) or [peer_jid]
    for resolved_jid in candidates:
        # 1) execute → 取 form
        resp = await adhoc.send_command(target, command_node, action='execute')
        session_id = resp['command']['sessionid']
        form = resp['command'].get('form')

        if inspect_only:
            await adhoc.send_command(target, command_node, action='cancel', sessionid=session_id)
            return {"ok": True, "form": form_meta}

        # 2) 填表 — 只填 form_data 中与 form 字段匹配的键
        self._set_form_values(form, form_data or {})

        # 3) complete + payload
        result = await adhoc.send_command(target, command_node, action='complete',
                                          sessionid=session_id, payload=form)
        return {"ok": True, "result": self._form_to_dict(result['command']['form'])}
```

异常处理覆盖：`asyncio.TimeoutError`、`slixmpp.exceptions.IqTimeout`、`IqError(service-unavailable)`，会自动换下一个 resource 重试（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:589-636`）。

LLM Agent 也可以把这个能力当作 tool 调用，函数 `_execute_a2a_xmpp_adhoc`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\modules\agent\agent_instance.py:1152-1191`），在 OpenAI tools schema 中注册为 `a2a_xmpp_adhoc`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\modules\agent\agent_instance.py:1042-1062`）。

---

## 8. 双方如何"知道怎么调对方功能" — 协议与数据契约

可用握手路径：

| 步骤 | 数据 | 协议 |
| --- | --- | --- |
| 1. 发现对方支持 A2A | `urn:xmpp:a2a:1` 出现在 disco#info features | XEP-0030 |
| 2. 列举对方命令 | (a) 拉取对方 PEP `urn:xmpp:a2a:agentcard` → 解析 `skills[]`；(b) 对 `node=http://jabber.org/protocol/commands` 发 disco#items | XEP-0163/0060 + XEP-0030 |
| 3. 探测某命令的表单 | `call_adhoc_command(..., inspect_only=True)`：发 `action=execute` 拿 form metadata，再 `action=cancel` 释放 session | XEP-0050 + XEP-0004 |
| 4. 真正调用 | 按 form 字段填 `form_data`，发 `action=complete` 提交，解析返回 form | XEP-0050 + XEP-0004 |

**提交的数据形态**（XEP-0004 数据表单字段）：
- 字段类型支持 `text-single`、`text-multi` 等。`text-multi` 入参可以是 list，会自动 `\n` 拼接；
- 表单填充策略：`_set_form_values()` **只填同名字段**，其余键忽略（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:736-768`），所以远端可以安全演化字段集。

---

## 9. 名片交换详细实现

### 9.1 命令定义

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\exchange_business_card.py:17-34
A2A_ADHOC_EXCHANGE_NODE = "urn:xmpp:a2a:cmd:exchange_business_card"

class ExchangeBusinessCardCommand(AdhocCommand):
    node = A2A_ADHOC_EXCHANGE_NODE
    name = "Exchange Business Card"
    form_fields = [
        {"var": "name",    "type": "text-single", "label": "Name"},
        {"var": "company", "type": "text-single", "label": "Company"},
        {"var": "title",   "type": "text-single", "label": "Title"},
        {"var": "email",   "type": "text-single", "label": "Email"},
        {"var": "xmpp",    "type": "text-single", "label": "XMPP"},
        {"var": "website", "type": "text-single", "label": "Website"},
        {"var": "phone",   "type": "text-single", "label": "Phone"},
    ]
```

### 9.2 入站（别人调我换名片）

- 阶段 1 `handle_execute` (`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\exchange_business_card.py:38-59`)：返回 7 个字段的空白表单。
- 阶段 2 `handle_submit` (`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\exchange_business_card.py:61-98`)：
  - 解析对方提交的卡片字段，加上 `sender_jid = session['from']`；
  - 调 `a2aserver.business_card.exchange_business_card`：把对方名片写入 `a2aserver/data/a2a.sqlite` 表 `received_cards`，并返回自己的 `my_card`（`@c:\dev\agi-ev\ai-sns-el\a2aserver\business_card.py:11-34`、`@c:\dev\agi-ev\ai-sns-el\a2aserver\db.py:99-133`）；
  - 用 `ctx.make_form(ftype='result')` 把自己的名片回写成结果表单。

### 9.3 出站（我主动换名片）

最简捷径是 debug HTTP：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\router.py:707-739
@router.post("/xmpp-a2a/debug/call-exchange")
async def xmpp_a2a_debug_call_exchange(request):
    my_card = a2a._load_my_business_card() or {}
    form_data = {key: my_card.get(key, '') for key in
                 ('name','company','title','email','xmpp','website','phone')}
    result = await a2a.call_adhoc_command(target_jid, A2A_ADHOC_EXCHANGE_NODE, form_data)
```

时序图：

```
我 (XMPPA2AManager)                                 对方 (slixmpp + ExchangeBusinessCardCommand)
   │ call_adhoc_command(peer, exchange_node, my_card_form)        │
   │ ──── <iq set> command node action=execute  ────────────────►│
   │                                                              │ handle_execute → form (空白 7 字段)
   │ ◄──── <command status=executing> + form ────────────────────│
   │ _set_form_values(form, my_card)                              │
   │ ──── <iq set> command action=complete + payload ───────────►│
   │                                                              │ handle_submit:
   │                                                              │   add_received_card(their_card)  → a2a.sqlite
   │                                                              │   my_card = get_my_card()
   │                                                              │   build result form
   │ ◄──── <command status=completed> + result form ─────────────│
   │ _form_to_dict(result) → 得到对方 my_card 字段                 │
```

注意：本机 `a2aserver/data/a2a.sqlite` 的 `my_card` 表是单行（id=1），由 a2aserver 提供的 Web 管理 UI 维护（`@c:\dev\agi-ev\ai-sns-el\a2aserver\templates\index.html` + `a2aserver/server.py` REST）。

---

## 10. A2A JSON-RPC over Ad-hoc（通用任务）

### 10.1 命令本体

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\a2a_task.py:19-30
A2A_ADHOC_TASK_NODE = "urn:xmpp:a2a:cmd:tasks"

class A2ATaskCommand(AdhocCommand):
    node = A2A_ADHOC_TASK_NODE
    form_fields = [
        {"var": "jsonrpc_request", "type": "text-multi", "label": "JSON-RPC Request"},
    ]
```

`handle_submit` 把表单中的 JSON-RPC 字符串提取出来，**优先 POST 到本机 8789 A2A HTTP 子进程**：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\a2a_task.py:131-168
async def _forward_to_local_a2a_server(request_str):
    return await loop.run_in_executor(None, _sync_http_post_a2a, request_str)
# → urllib POST http://127.0.0.1:8789/a2a/
```

子进程对 `tasks/send` 的处理：

```@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py:83-138
if method == "tasks/send":
    ... 解析 parts 找名片字段 ...
    if their_card:
        my_card = exchange_business_card(their_card, sender_jid=sender_jid)
    else:
        my_card = get_my_card()
    return artifacts=[{parts:[{type:"data", data: my_card}]}]
```

若 8789 不可用，`_local_handle_jsonrpc` 在 ad-hoc 进程内做兜底（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\a2a_task.py:171-246`）。

### 10.2 前端 HTTP → XMPP 链路

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\router.py:798-895
@router.post("/xmpp-a2a/call")
async def xmpp_a2a_call(request: A2AXmppCallRequest):
    jsonrpc_request = {"jsonrpc":"2.0","id":rpc_id,"method":method,"params":{...}}
    form_data = {"jsonrpc_request": json.dumps(jsonrpc_request)}
    result = await a2a_mgr.call_adhoc_command(peer_jid, A2A_ADHOC_TASK_NODE, form_data)
    # 把 result['result']['jsonrpc_response'] 反序列化后返回前端
```

完整链路：前端 → `POST /api/sns/xmpp-a2a/call` → `XMPPA2AManager.call_adhoc_command` → 对端 ad-hoc handler → 对端本地 8789 (或本地 fallback) → JSON-RPC 响应 → form `jsonrpc_response` 字段 → 回到前端。

---

## 11. 前端如何调度 XMPP（端到端）

### 11.1 初始化向导（首次配置）

`InitializationWizard.js` 的 XMPP 步骤（`@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\home\InitializationWizard.js:382-414`、`:655-676`）：

```@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\home\InitializationWizard.js:655-676
testXmppBtn.addEventListener('click', async () => {
    const res = await window.api.post('/api/system/init-wizard/test-xmpp', {
        account: this.state.account,
        account_password: this.state.account_password
    });
});
```

后端测试 endpoint：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\modules\system\router.py:441-451
@router.post("/init-wizard/test-xmpp")
async def test_xmpp_config(payload: SystemInitTestXMPP, service): ...
```

具体登录测试在 `SystemInitWizardService.test_xmpp`（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\modules\system\service.py:527-710`）：动态创建一个临时 `slixmpp.ClientXMPP`，监听 `session_start / failed_auth / connection_failed`，12 秒超时。

向导最终 `submit` 时把 `account`、`password`、`agent_id` 等写入 `aisns_cfg` 表，下一次后端 startup 就会用它连接 XMPP。

### 11.2 编辑 Agent Card / Ad-hoc Commands

`SNSAdvancedDialog.js` "XMPP" Tab 内：
- 字段：`xmppAccount / xmppPassword / a2aCardName / Description / Version / Provider Org / Provider URL`（`@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\sns\SNSAdvancedDialog.js:279-326`）。
- 命令列表通过 `_loadMergedA2ACommands` 拉取后端合并结果：

```@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\sns\SNSAdvancedDialog.js:1057-1075
const resp = await fetch(this.resolve('/api/sns/a2a/commands'));
```

后端响应来源：

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\router.py:270-310
@router.get("/a2a/commands")
async def list_a2a_commands(db):
    commands = discover_commands() + build_config_commands(...)
    # 附加 enabled flag (取自 aisns_cfg.memo.a2a_config.adhoc_commands)
```

保存时 `_collectA2AConfig`（`@c:\dev\agi-ev\ai-sns-el\aisns_frontend\renderer\js\modules\sns\SNSAdvancedDialog.js:1281-1336`）打包 `{agent_card, adhoc_commands}` 写回 `aisns_cfg.memo.a2a_config`；`service_async.update_ai_chat_config` 检测到变更后调度 `reload_a2a()`（不掉线）或者全量 `restart()`（凭据变更）。

### 11.3 发送消息 / 文件

```@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\router.py:58-83
@router.post("/send-message"): service.send_message(...)
@router.post("/send-file"):    service.send_file(...)
```

`SNSService.send_message` (`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\service_async.py:517-650`)：
- 拿 `XMPPClientManager.get_client()`
- `await client.send_message_to_jid(to_account, content)`  → 内部先 `ensure_mutual_subscription`，再 `send_message(mto=, mbody=, mtype='chat')`
- 写库 + 广播 WebSocket

文件走 XEP-0363 (`xmpp_client.py:582-616`)：HTTP File Upload 拿到 URL 后以普通文本消息形式 `📎 File: <name>\n<url>` 发送。

### 11.4 地图层（map.html / interact_python.js）

- 入站消息：`XMPPClient.on_message` 写库后广播 `new_message` (`xmpp_client.py:363-373`)，前端 SNS 模块 + `interact_python.js`（`show_talk_message` 等函数）渲染气泡。
- 主动模式：`XmppMixin.receiveMessage` → 当对话方为活跃人时调 `self.send_talk_message(account, self.aisns_cfg.account, content)` 直接驱动地图 UI（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\mixin\xmpp_mixin.py:113-126`）。
- 远程交易：`skills/skill_send_to_remote_agent/send_to_remote_agent.py` 直接走 HTTP A2A（不经 XMPP），但消息正文里携带 `XMPP Account / Trade ID / description`，让远端 agent 用 XMPP 主动回话（`@c:\dev\agi-ev\ai-sns-el\aisns_backend\skills\skill_send_to_remote_agent\send_to_remote_agent.py:80-103`）。

---

## 12. 完整端到端时序（典型场景）

### 12.1 启动 + AI 引擎首次接收消息

```
T0  api_server.startup → A2A 子进程(8789) + XMPPClientManager.start
T1  XMPPClient.connect → SASL → session_start
T2     send_presence + get_roster
T3     XMPPA2AManager.initialize:
         load agent card (inline or HTTP fetch)
         disco.add_feature(urn:xmpp:a2a:1, ..., commands)
         xep_0163.publish(urn:xmpp:a2a:agentcard, id=current)
         xep_0050.add_command(urn:xmpp:a2a:cmd:exchange_business_card)
         xep_0050.add_command(urn:xmpp:a2a:cmd:tasks)
         xep_0050.add_command(<用户脚本/config 定义>)
T4  好友 PEP +notify 到达 → 持有方更新 agent card 缓存
T5  好友发文本 → on_message → 写库 → ws broadcast → service_async.ensure_social_engine_started
T6  AI Social Engine.receiveMessage → XmppMixin.handle_receiveMessage
T7  引擎在 tool_check_review 中 _fetch_peer_agent_card →
        HTTP skill fetch_agent_card 失败 → fetch_peer_agent_card_pep → 拿到对端 skills
T8  引擎决定调用 a2a_xmpp_adhoc tool →
        XMPPA2AManager.call_adhoc_command(peer, node, form_data) → 完整 XEP-0050 双阶段
T9  收到对端结果 → 返回 LLM → 回复消息 → send_message_to_jid → mutual subscribe + xep_0363/0049 发出
```

### 12.2 用户在前端 UI 编辑 Agent Card

```
SNSAdvancedDialog 保存 → PUT /api/sns/ai-chat-config (a2a_config=…)
  → service_async.update_ai_chat_config:
       _data['memo']['a2a_config'] = new_cfg
       if 凭据变 → XMPPClientManager.restart()  (full reconnect)
       elif a2a_config 变 → a2a._a2a_manager.reload_a2a()
                              清旧命令 → initialize() 重新发布 PEP / 注册命令
```

---

## 13. 关键参数 / 常量速查

| 参数 | 文件:行 | 值 |
| --- | --- | --- |
| 心跳间隔 | `xmpp_client.py:64` | 30 s |
| 心跳超时 | `xmpp_client.py:65` | 10 s |
| 连续失败重连阈值 | `xmpp_client.py:68` | 3 |
| 初始重连退避 | `xmpp_client.py:804` | 5 s |
| 最大重连退避 | `xmpp_client.py:805` | 300 s |
| Roster 最大保留 | `xmpp_client.py:104` | 250 |
| Roster 清理延迟 | `xmpp_client.py:102` | 20 s |
| call_adhoc 单 resource 超时 | `xmpp_a2a.py:540` | 20 s |
| fetch_peer_agent_card_pep 超时 | `xmpp_a2a.py:491-493` | 10 s |
| A2A HTTP 端口 | `api_server.py:944-947`、`a2aserver/server.py` | 8789 |
| PEP 节点 | `xmpp_a2a.py:36` | `urn:xmpp:a2a:agentcard` |
| Features | `xmpp_a2a.py:33-35` | `urn:xmpp:a2a:1`、`urn:xmpp:a2a:business_card:1`、`http://jabber.org/protocol/commands` |
| 名片交换 node | `a2a_commands/exchange_business_card.py:17` | `urn:xmpp:a2a:cmd:exchange_business_card` |
| A2A task node | `a2a_commands/a2a_task.py:19` | `urn:xmpp:a2a:cmd:tasks` |

---

## 14. 调试 API 速查（无需第三方 XMPP 客户端）

| 路由 | 文件:行 | 用途 |
| --- | --- | --- |
| `GET /api/sns/xmpp-a2a/debug/status` | `router.py:612-662` | 看 disco features、已注册 ad-hoc、agent_card、plugin 列表 |
| `GET /api/sns/xmpp-a2a/debug/pep-items` | `router.py:665-704` | 读本机 PEP `urn:xmpp:a2a:agentcard` 的实际 XML 内容 |
| `POST /api/sns/xmpp-a2a/debug/call-exchange` | `router.py:707-739` | 用本地名片向 target_jid 触发 exchange_business_card |
| `POST /api/sns/xmpp-a2a/debug/discover-commands` | `router.py:742-767` | 列出 peer 支持的 ad-hoc 命令 |
| `POST /api/sns/xmpp-a2a/debug/inspect-command` | `router.py:770-795` | inspect_only 模式看对方某命令的表单 |
| `POST /api/sns/xmpp-a2a/call` | `router.py:798-895` | 通用 JSON-RPC over XMPP（业务用） |
| `GET  /api/sns/a2a/commands` | `router.py:270-310` | 本机合并后的命令清单（前端配置 UI 消费） |

---

## 15. 容易遗漏但重要的点

1. **PEP 的"+notify" 隐式订阅**：xep_0163 在好友 subscription=both 时会自动接收对方的 agent card 更新通知；这就是为什么 `ensure_mutual_subscription` 在 `send_message_to_jid` 中是必要前置（`xmpp_client.py:572-580`）。
2. **Windows IPv6 痛点**：`urllib` 请求 agent_card_url 时强制把 `localhost` 替换为 `127.0.0.1` 并设 `Host: localhost` 头（`xmpp_a2a.py:104-110`、`a2a_commands/a2a_task.py:153-167`），否则在某些 Windows 环境下会 hang。
3. **Heartbeat 与 ConnectionFailed 解耦**：`on_disconnected` 主动 cancel 心跳 task 避免双重 reconnect（`xmpp_client.py:536-546`）。
4. **Slixmpp RosterItem 取值差异**：`_read_roster_field` 兼容三种访问方式（bracket / .get / getattr），避免不同 slixmpp 版本差异（`xmpp_client.py:130-160`）。
5. **重连 backoff 重置**：`on_session_start` 回调 `XMPPClientManager.on_session_start_reset`，让一次成功登录就把重连延迟拉回 5 s（`xmpp_client.py:82-87`、`:970-973`）。
6. **多端 resource 容错**：`_get_all_resources` 按 priority 排序遍历 resource，再回退 bare JID；对单端用户的 service-unavailable 会自动跳过（`xmpp_a2a.py:578-636`）。
7. **A2A 子进程独立 DB**：`a2aserver/data/a2a.sqlite` 与主 DB `aisns_backend/db/db.sqlite` 是分离的，避免互锁；主进程访问业务名片走 `a2aserver.db.get_my_card` 等模块函数（`xmpp_a2a.py:159-176`、`exchange_business_card.py:120-139`）。
8. **配置热重载语义**：仅 `a2a_config` 变化时走轻量级 `reload_a2a`（不掉线），凭据变化才会 `restart` 整个 XMPP 会话（`service_async.py:1602-1629`）。
9. **AI Agent 的 Tool**：LLM 在 reasoning 中可以直接选择 `a2a_xmpp_adhoc` 工具（OpenAI tools schema 由 `agent_instance.py:1042-1062` 注入），所以"语言模型动态调用对方 XMPP ad-hoc"的能力天然具备。
10. **A2A HTTP `/a2a/` 与 XMPP `urn:xmpp:a2a:cmd:tasks` 同构**：都是 JSON-RPC 2.0 `tasks/send`；XMPP 路径只是把同一个请求体放到 XEP-0050 表单的 `jsonrpc_request` 字段里携带过去，这样 NAT 后的 agent 也能被调用。

---

## 16. 一句话总结

ai-sns-el 把"标准 XMPP + 一组 A2A 命名空间约定"拼成了一套 P2P agent 互操作协议：
- **启动**：随后端进程拉起 slixmpp + A2A HTTP (8789)，session_start 后自动发布 agent card (PEP) 并注册 ad-hoc 命令；
- **发现**：disco 看 features → PEP 拉 agent card → disco#items 列命令 → inspect_only 探表单；
- **调用**：`call_adhoc_command` 两阶段表单（execute → complete），通用 JSON-RPC 任务则封装到 `urn:xmpp:a2a:cmd:tasks` 命令中桥到本地 A2A HTTP；
- **名片**：`urn:xmpp:a2a:cmd:exchange_business_card` ad-hoc 命令负责双向交换，存进独立的 `a2aserver/data/a2a.sqlite`；
- **前后端**：前端 InitializationWizard 决定 XMPP 凭据、SNSAdvancedDialog 决定 a2a_config / 命令开关，后端通过 `reload_a2a` 实现无缝热更新；地图通过 WebSocket 实时呈现 XMPP 消息。
