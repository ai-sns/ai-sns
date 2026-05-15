# XMPP / A2A 子系统代码 Review 报告

> 本报告对 ai-sns-el 中所有 XMPP / A2A 相关代码做静态 review。覆盖 `xmpp_client.py`、`xmpp_a2a.py`、`a2a_commands/*`、`a2aserver/*`、`api_server.py` 的 A2A 子进程逻辑、`service_async.py` 热重载链、`map_task_manager.py` 对端调用闭环、`mixin/xmpp_mixin.py` 引擎入口、`runtime/modules/system/service.py` 的 test_xmpp。
>
> 每条问题包含：**严重度 / 文件:行号 / 复现条件 / 影响 / 建议改法**。
>
> 严重度梯度：**Critical**（生产事故级，立刻修） > **High**（很大概率出问题） > **Medium**（特定条件出问题） > **Low**（小瑕疵） > **Info**（提示）。

---

## 0. 执行摘要（按"必须先看"排序）

| # | 严重度 | 问题 | 文件:行 |
| --- | --- | --- | --- |
| 1 | Critical | `a2aserver` 监听 `0.0.0.0:8789` 且 REST 完全无鉴权 | `a2aserver/server.py:158-182, 211` |
| 2 | Critical | `XMPPClient.on_message` 在 slixmpp 事件循环里调 `db_write(...)`（最长 30 s 阻塞 loop），同时还做同步 `self.db.query(...)` | `xmpp_client.py:288-413` |
| 3 | Critical | `/api/sns/xmpp-a2a/debug/*` 与 `/api/sns/xmpp-a2a/call` 无鉴权，可对任意 JID 触发名片/JSON-RPC 调用 | `router.py:612-895` |
| 4 | High | `XMPPA2AManager.initialize()` 是 fire-and-forget 任务，失败后 PEP/disco/ad-hoc 全部不发布且无重试 | `xmpp_client.py:92-98`、`xmpp_a2a.py:970-1002` |
| 5 | High | `XMPPClient` 长期持有同步 Session，跨连接复用 → 脏数据 + 非线程安全 | `xmpp_client.py:19-22, 893-911` |
| 6 | High | `restart()` 无并发锁，连点保存配置可让 `_client = None` 与新任务交错 | `xmpp_client.py:975-994` |
| 7 | High | 心跳触发 disconnect 后 `_consecutive_failures` 复位；"假连接"下心跳永不复活 | `xmpp_client.py:536-570` |
| 8 | High | `on_message` 中陌生人首条消息自动写入 `AIFriend`，可滥用刷好友 | `xmpp_client.py:316-334` |
| 9 | High | `a2a_task.py` 本地 fallback 与 `a2aserver` `tasks/send` **两份独立实现，行为漂移** | `a2a_task.py:171-246`、`a2aserver/server.py:83-153` |
| 10 | High | `_a2a_process` 子进程无看门狗 + `_a2a_process_log_fp` 反复 open 可泄漏 | `api_server.py:925-1025` |

---

## §A 功能性 Bug

### A1. **Critical** — `on_message` 阻塞 slixmpp 事件循环最长 30 秒
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:303-360`
  ```python
  config = self.db.query(AISnsCfg).filter(...).first()    # 同步 SQLAlchemy
  ...
  result = db_write(_save_incoming, description="xmpp_client_save_incoming")  # 同步阻塞
  ```
- `db_write` 实现 `@c:\dev\agi-ev\ai-sns-el\aisns_backend\db\write_queue.py:142-162`：
  ```python
  op.future.result(timeout=30.0)   # 阻塞当前线程最长 30 秒
  ```
  这是 sync 函数；在 async 协程里直接调用 = **阻塞 asyncio 事件循环**。slixmpp 所有 IQ/Ping/PEP 处理在同一 loop。
- **复现**：写队列前面排着慢操作 / SQLite WAL 短锁；或同时多客户端流入消息。
- **影响**：
  1. 心跳被卡 → 误判掉线 → reconnect 抖动
  2. 入站 ad-hoc IQ 排队，对端可能判 timeout
  3. PEP `+notify` 延迟
- **建议**：把整段改成 `await db_write_async(...)`，并把 `self.db.query(AISnsCfg)` 搬进写队列回调里在 worker thread 执行；或用 `await loop.run_in_executor(None, ...)` 兜底。

### A2. **High** — 心跳触发 disconnect 后"假连接"下永不复活
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:548-570` + `:536-542`
  ```python
  if self._consecutive_failures >= self._max_failures:
      self.disconnect()
      return                          # 心跳协程退出
  ```
  ```python
  async def on_disconnected(self, event):
      self.heartbeat_task = None
      self._consecutive_failures = 0  # 失败计数复位
  ```
- 正常路径靠 `_run_client.await self._client.disconnected` 触发 backoff 重连 → 新 session_start 重建心跳。但如果 `disconnect()` 没让 `disconnected` future 完成（slixmpp 在某些状态下不切换 state），心跳协程已死，但客户端仍认为"在线"，从此再无心跳。
- **建议**：`_run_client` 重连成功后显式校验 `client.heartbeat_task` 是否 None / done，若是则 `create_task(client.heartbeat())`。再额外注册一个 watchdog：N 分钟内既无入站也无 ping ack 就强制 `disconnect()`。

### A3. **High** — `XMPPClient` 持有跨线程同步 Session 永不释放
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:893-911`：
  ```python
  db = get_db_sync()
  ...
  self._client = XMPPClient(config.account, config.password, db)
  ```
- 该 `db` 被 `XMPPClient.__init__` 存到 `self.db`，全生命周期复用；在 `on_message`、`cleanup_roster_if_needed`、`_get_subscription_from_db`、`update_roster_local` 中都用它读。
  - SQLAlchemy `Session` **不是线程安全**
  - `self.db.expire_all()`（`:678`）每次清缓存，否则读到旧值
  - 没有任何路径 `db.close()`，`stop()` 里也没关
- **影响**：长期运行内存增长 + 长事务；与写队列 worker 在另一 Session 上的提交存在版本错位。
- **建议**：每次 read 使用一次性 `with get_db_sync() as db:` 上下文管理器；不要把 Session 持到 client 实例上。

### A4. **High** — 陌生人首条消息自动入 AIFriend 表
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:316-334`
  ```python
  friend = session.query(AIFriend)...first()
  if friend: ...
  else:
      friend = AIFriend(account=_from_jid, nick_name=_from_jid,
                        subscription="none", new_message_flag=True, ...)
      session.add(friend)
  ```
- 任何 XMPP JID 发一条 `<message type='chat'>` 就能在 `AIFriend` 表插一行。与 `cleanup_roster_if_needed` "按 last_message_time 排序删 250 名以下" 叠加，恶意发送方可以反复刷新自己的 `last_message_time` 把真实好友挤出 roster。
- **建议**：
  1. 默认只对 `subscription in ('to','both')` 的发件方写库；其余进"未授信收件箱"或丢弃；
  2. `cleanup_roster_if_needed` 排序时给 `subscription='none'` 一个排序惩罚（先删）。

### A5. **High** — `ensure_mutual_subscription` 常 30 s 超时
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:618-672` + `_notify_subscription_waiters`（`:698-710`）
  ```python
  sub = self._get_subscription_from_db(bare_jid)
  if sub == 'both':
      event.set()
  ```
- 等待器只读 DB。许多 XMPP 服务端 "pre-approve subscriber" 直接 roster push `both` 而不发 `subscribed`；这时 `_find_roster_item.subscription` 已经是 `both`（`:631-638` 内存里看得到），**但 `_get_subscription_from_db` 读的是 DB**，DB 尚未 upsert 完成时 waiter 永远卡到 30 s。
- **复现**：清空 DB → 第一次给陌生人发消息 → 大概率 30 s。
- **影响**：每条首次消息延迟 30 s。
- **建议**：`_notify_subscription_waiters` 同时检查内存 roster；`on_roster_update` 中遍历所有 waiter 主动唤醒（当前只对 `groups` 内 JID 唤醒，`:466-471`）。

### A6. **High** — `update_roster_local` fallback 触发 RosterNode 副作用
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:484-486`
  ```python
  roster_item = self._find_roster_item(account)
  if roster_item is None:
      roster_item = self.client_roster[jid]   # 副作用：add(save=True)
  ```
- slixmpp `RosterNode.__getitem__` 对不存在 JID 静默 `add(save=True)`（已在 `xmpp_a2a.py:907` 用 `has_jid` 规避）。这里没规避，且 `on_roster_update` 反复进入。
- **建议**：`_find_roster_item` 返回 None 时直接 return；删除 fallback。

### A7. **High** — `fetch_peer_agent_card_pep` 取错 child 节点
- 位置：`@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:497-507`
  ```python
  for child in item.xml:
      if child.text:
          payload_el = child
          break
  ```
- 取"第一个有 text 的子节点"。对端 item 里如果有 `<headers/>`、`<delay/>` 等带 text 的兄弟节点，会取错再 `json.loads` 失败。
- **建议**：按命名空间显式过滤：
  ```python
  ns_tag = "{%s}agentcard" % A2A_PEP_NODE
  payload_el = next((c for c in item.xml if c.tag == ns_tag and c.text), None)
  ```

### A8. **Medium** — `_get_agent_card_url` 对 `agent.memo` 不容错
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:86-91`：`json.loads(agent.memo)` 无 try。memo 脏数据时整段失败被外层吞为 `return None`，启动期 PEP 不发布且无可见错误。
- **建议**：`json.loads` 单独 try，失败时 `logger.warning` + 返回空 dict。

### A9. **Medium** — `discover_peer_adhoc_commands` 把 "discovery 失败" 伪装为 "无命令"
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:842-879`：所有 resource 的 disco#items 全失败时 `disco_success=False`，但函数仍返回 `commands`（可能仅含 agent_card 来源）。调用方分不清"对端无命令"还是"网络失败"。
- **建议**：返回结构增加 `"disco_ok": bool`，上游据此决策。

### A10. **Medium** — `discover_peer_adhoc_commands` 元组下标依赖 slixmpp 内部
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:852-854`：`item[1]/item[2]` 依赖 `disco_items.items` 是 `(jid, node, name)` tuple。slixmpp 版本变更可能改为 `DiscoItem` 实例 → IndexError 被外层吞为 "无命令"。
- **建议**：用 `try/except + getattr/具名访问` 双保险。

### A11. **Medium** — initialize 顺序：disco caps 未广播就 publish PEP
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:993-1000`：先 `register_disco_features()` 再 `publish_agent_card_pep()`。但 `add_feature` 不会主动重发 presence/caps；若 server 依赖 caps 决定是否 `+notify`，**首次 publish 时对端不会拿到推送**。
- **建议**：`register_disco_features()` 之后 `self.client.send_presence()` 再 publish。

### A12. **Medium** — `a2aserver` agent card 与主进程不一致
- `@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py:39-68` 写死 agent card 常量；主进程 `/a2a/{agent_id}/.well-known/agent-card.json` 和 `aisns_cfg.memo.a2a_config.agent_card` 各自来源。外部探测可能拿到三份不同结果。
- **建议**：让子进程加载主 DB 的 a2a_config，或直接代理到主进程 endpoint。

---

## §B 健壮性不足

### B1. **High** — 大量 `except Exception: pass` 静默吞错
显著示例：
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:124, 145, 159, 171, 181, 244, 266-267, 270, 442-449, 458-461, 568-569`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:185-186, 235-237, 251-253, 671-673, 720-721, 731-733, 787-789, 920-922`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\base.py:55-59, 95-98`

**影响**：线上排障极困难；某些路径异常被吞后还继续返回"成功"。
**建议**：至少 `logger.debug` 留痕；关键路径 `exc_info=True`。约定一个内部规则："吞掉异常必须打 log"。

### B2. **High** — `_make_execute_handler` 出错时 session 半残
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:402-406`：
  ```python
  session['notes'] = [('error', f'Internal error: {e}')]
  return session
  ```
- 没有同时设置 `payload=None / next=None / has_next=False / status='canceled'`，slixmpp 内部可能仍等待下一阶段，session 挂在内存里。
- **建议**：异常路径下显式收口：
  ```python
  session['payload'] = None
  session['next'] = None
  session['has_next'] = False
  session['status'] = 'canceled'
  ```

### B3. **High** — `_load_my_business_card` 副作用累积
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:159-176`（以及 `a2a_commands/exchange_business_card.py:100-117`、`a2a_commands/a2a_task.py:249-269`）：
  - 每次 `sys.path.insert(0, project_root)` — 长期运行 `sys.path` 膨胀（虽然有 `if X not in sys.path` 判断，但跨平台路径大小写差异下不保证去重）
  - 每次 `init_db()` — 三处都跑 `CREATE TABLE IF NOT EXISTS` + open/close 文件
  - 每次入站名片调用都走一遍
- **建议**：把 `sys.path` 设置移到 manager 初始化时一次；`init_db()` 同样一次性，或在 a2aserver 子进程已启动时跳过。

### B4. **Medium** — `register_adhoc_commands` 未清旧 `xep_0050.commands`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:367-380`：只清自家 `_registered_commands/_command_instances`。`reload_a2a` 路径在 `:940-954` 有清，但任何直接调 `register_adhoc_commands` 的代码路径（包括将来重构）都可能双重注册。
- **建议**：把"清旧 + 注册新"封装成一个内部方法，所有路径强制走它。

### B5. **Medium** — `cleanup_roster_if_needed` 使用 `iq.send(now=True)`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:237-243`：在 slixmpp asyncio 客户端里 `iq.send(now=True)` 语义不明，可能阻塞 loop。
- **建议**：改成 `await iq.send()`；现有 `self.del_roster_item(jid)` 主路径已够用，可考虑直接删 fallback。

### B6. **Medium** — `_subscription_waiters` 在重连后不清空
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:58, 668-672`：`restart()` / 重连后旧 waiter 字典如果残留（虽 `XMPPClient` 是新实例，旧客户端被 GC 之前其上等待的协程仍可能持引用），需要确认。更安全的写法：`on_disconnected` 中 `for w in self._subscription_waiters.values(): w.set()` 释放所有等待者。
- **建议**：在 `on_disconnected` 中统一唤醒所有 waiter（避免持有死 Event 30 s）。

### B7. **Medium** — `XMPPA2AManager.__init__` 没复用 `_subscription_waiters` 设计
- `xmpp_a2a.py:47-60` 没有提供"call_adhoc 进行中"的集合，无法在 disconnect 时主动 cancel；导致 `await asyncio.wait_for(..., 20s)` 持续 20 秒后才返回失败。
- **建议**：维护 `_in_flight_calls: set[asyncio.Task]`，`reload_a2a` / `stop` 时 `task.cancel()`。

### B8. **Medium** — `fetch_agent_card` 重试只看异常，不看 HTTP 状态
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:113-157`：用 `urllib.request.urlopen` 拿响应，如果对端返回 200 但 body 不是合法 JSON，单次 `json.loads` 失败也会重试 5 次（浪费时间）；如果 4xx 直接抛 `HTTPError` 走重试同样浪费。
- **建议**：把 4xx 视为永久失败，4xx 后立即停止重试。

### B9. **Low** — `_sync_http_get` Host 头硬编码 `localhost`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:108`：`Host: localhost` 只在 `localhost → 127.0.0.1` 替换的场景合理；如果 `agent_card_url` 指向远程域名（用户自配 CDN），Host 头错乱可能被 CDN 当成非法请求。
- **建议**：仅当原 URL host == `localhost` 时才覆盖 Host；其它情况让 urllib 默认填。

### B10. **Low** — `a2a_commands/__init__._scan_directory` 用 `importlib.reload`，旧实例残留
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\__init__.py:140-161`：reload 旧模块时，已注册到 `xep_0050.commands` 的旧 handler 闭包仍指向旧 class；用户脚本"修复 bug 重新加载"未必生效。
- **建议**：在 reload 前 `pop` 掉 `sys.modules` 项；或者每次 spec_from_file_location 用唯一模块名。

---

## §C 可能阻塞后端引擎（事件循环 / 长锁 / 无超时）

### C1. **Critical** — 见 §A1（`on_message` 同步阻塞）

### C2. **High** — `cleanup_roster_if_needed` 在 loop 内做同步大查询
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:185-286`：`self.db.query(AISnsCfg)` + `AIFriend.in_(jids)` 都是同步 SQLAlchemy。jids 上百时 `IN (...)` 查询 + SQLite WAL 锁可短期冻结事件循环。
- **建议**：搬进 worker thread（`asyncio.to_thread`）或 write_queue read 模式。

### C3. **High** — `_load_a2a_config` / `_get_agent_card_url` / `_load_my_business_card` 都是同步 DB / 文件 IO
- 三个函数（`xmpp_a2a.py:64-95, 159-176, 261-289`）都在 async 上下文中被直接调用：
  - `register_adhoc_commands` 内（`:328`）
  - `reload_a2a` 内（`:961-963`）
  - `initialize` 内（`:981-984`）
- 每次都 `get_db_sync()` + 同步查询，且 `_load_my_business_card` 额外做 `init_db()` 打开 SQLite。
- **建议**：把这些读改成异步读，或者一次性在 `__init__` 缓存。

### C4. **High** — `a2a_task._sync_http_post_a2a` 通过默认 executor 易吃满线程池
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\a2a_commands\a2a_task.py:131-168`：`loop.run_in_executor(None, ...)` + urllib 30 s 超时。Python 默认线程池大小 `min(32, cpu+4)`；高并发入站 ad-hoc `tasks/send` 会把池吃满，间接卡住 `_sync_http_get`、`broadcast_new_message` 等其它 default executor 使用方。
- **建议**：自建一个专用 `ThreadPoolExecutor(max_workers=8, thread_name_prefix="a2a-http")`，或者改用 `httpx.AsyncClient`。

### C5. **High** — `ensure_mutual_subscription` 每条消息握手 30 s（见 §A5）
此处再次强调阻塞维度：虽然 `send_message_to_jid` 是 async，但只要这条等待没释放，后续同个 JID 的发送都会排队等同一个 Event。

### C6. **Medium** — `_start_a2a_server_subprocess` 在 startup 用 `time.sleep`
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:979-993`：startup 主协程里 `time.sleep(0.2)` + 最多 `20 × 0.1 = 2 s` 同步轮询。`startup_event` 是 async，但里面 `time.sleep` 是阻塞 loop 的；其它 startup 任务推迟。
- **建议**：改 `await asyncio.sleep(...)`，或直接放到独立线程。

### C7. **Medium** — `xep_0050.send_command` 没显式 timeout
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:652, 689`：靠外层 `asyncio.wait_for` 20 s 截停，但 slixmpp 内部 IQ Future 不一定能被 cancel 干净 — 可能泄漏 pending IQ 等待器，长时间运行后内存增长。
- **建议**：直接给 `send_command` 传 `timeout=20`，避免外层 `wait_for` 与内部超时不同步。

### C8. **Medium** — `discover_peer_adhoc_commands` disco#items 15 s 超时遍历所有 resource
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_a2a.py:842-871`：每个 candidate 最多 15 s。对方挂 10 个 resource 时最坏 150 s。
- **建议**：全局 budget（如 30 s）超过就 break。

---

## §D 可能让后端引擎崩溃 / 资源泄漏 / 不可恢复

### D1. **Critical** — `XMPPA2AManager.initialize()` fire-and-forget 失败后永久死亡
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:92-98`：
  ```python
  self._a2a_manager = XMPPA2AManager(self)
  asyncio.create_task(self._a2a_manager.initialize())
  ```
- task 抛异常后 Python 默认只打个 "Task exception was never retrieved" 警告就结束。整个 A2A 子系统（PEP、ad-hoc、commands）将不被注册，**前端看 disco/PEP/换名片全无效**。
- **复现**：DB 内 `aisns_cfg.memo` 是非法 JSON / agent_card_url 域名解析失败时极易触发。
- **建议**：
  ```python
  task = asyncio.create_task(self._a2a_manager.initialize())
  task.add_done_callback(_log_init_result)
  ```
  并提供一个 `/api/sns/xmpp-a2a/reinitialize` 强制重试入口。

### D2. **High** — `_run_client` 重连分支可能 100% CPU 紧绷
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:934-968`：
  ```python
  while not self._stopping:
      try:
          await self._client.disconnected
      except Exception as e:
          logger.error(...)
      ...
      self._client.connect()
  ```
- 如果 `self._client.disconnected` 在 reconnect 后立刻是已 done 的 Future（slixmpp 不重置该 Future），下一轮 await 立刻返回，紧接 `sleep(self._current_reconnect_delay)`；这部分有 sleep 不会 100% CPU，OK。但如果 backoff 是 5s 而 future 一直 done，每 5 秒重连一次没问题。**真正风险**：`self._client.connect()` 抛同步异常时被 try 包了 `logger.error`，循环继续；但 `_current_reconnect_delay` 已增长。可观察到的现象是 backoff 永远不会被重置（因为 reconnect_delay 仅在 `on_session_start_reset` 调用时重置）。
- **建议**：把 backoff 重置移到 `_run_client` 顶端"成功 await 完成"的那一刻；同时校验 `connect()` 抛错时不要把 delay 增长得太快。

### D3. **High** — `restart()` 无锁
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\xmpp_client.py:975-994`：`stop()` 把 `_client = None` 后 `start()` 立即重建。如果两次 restart 并发：
  1. R1 stop 中 cancel reconnect task；
  2. R2 stop 又 cancel 一次（OK，None）；
  3. R1 start 创建新 client；
  4. R2 start 又创建一个新 client（覆盖前一个）→ 旧 client 已 connect 但被丢弃，慢慢 GC。
- 实际触发：前端 1 秒内连点保存按钮（每次保存都 `update_ai_chat_config` → `restart()`，`service_async.py:1612-1614`）。
- **建议**：`XMPPClientManager` 加 `asyncio.Lock`，`restart` 全程持锁。

### D4. **High** — `_a2a_process` 子进程死掉无看门狗
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:925-1001`：只在 startup 一次性检查端口；运行中子进程 OOM/crash 后主服务无感。
- **影响**：之后所有走 8789 的 A2A `tasks/send` 全部失败，落回 `_local_handle_jsonrpc`（行为不一致）；名片管理 UI 无法访问。
- **建议**：加一个后台协程 `_a2a_supervisor`，每 30 s `poll()`，已退出则重启。

### D5. **High** — `_a2a_process_log_fp` 反复 open 可泄漏 fp
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\api_server.py:960-977`：每次 `_start_a2a_server_subprocess` 先 close 旧 fp 再 open 新 fp。但**旧的 Popen 进程仍持有旧 fp**（OS 层 fd 被进程继承）；如果调用者后续没 `_stop_a2a_server_subprocess` 旧进程，新进程开始把日志写到新 fp 而旧进程继续写到旧 fp（已被父端关闭，但子端 fd 仍打开），双进程并存时旧进程的写可能挂死。
- **建议**：start 时如果旧进程还活着先 `terminate()`，再 open 新 fp。

### D6. **High** — `XMPPClient.db` Session 永不 close（同 §A3）
**资源泄漏**：进程长期跑后 SQLAlchemy 内部连接池里这条连接处于"活跃但空闲"，无法回收，对 SQLite WAL 模式下 checkpoint 也是阻碍。

### D7. **High** — `XMPPA2AManager` 与 `XMPPClient` 双向引用残留
- `XMPPClient.__init__: self._a2a_manager = None` 之后 `on_session_start` 中 `self._a2a_manager = XMPPA2AManager(self)`；`XMPPA2AManager(self.client = xmpp_client)`。
- `restart()` 把 `self._client = None`，但旧 `_a2a_manager` 仍持有旧 client 的引用；如果此时旧 A2A 还在跑长 RPC（`call_adhoc_command` 在 await），它会继续向已断开的 client 发 IQ → 报 IqTimeout → 不会崩溃，但持续浪费 20 秒。
- **建议**：`stop()` 中显式 `if self._client._a2a_manager: cancel its tasks`。

### D8. **Medium** — `register_disco_features` 重复添加不会出错但状态漂移
- `xmpp_a2a.py:191-205`：列表 `_registered_features` 自家去重，但底层 `disco.add_feature` 多次调同一 ns 是否幂等取决于版本；安全起见显式判断。

### D9. **Medium** — `cleanup_old_backend_logs_async` 任务静默失败
- `xmpp_client.py:880`：fire-and-forget，失败只 warning；如果磁盘满或权限错，会反复 retry（每次启动）但用户不知道。
- **建议**：失败 N 次后通过 WebSocket 推一个 system notice。

---

## §E 设计 / 架构不合理

### E1. **High** — `XMPPA2AManager` 单类 1000 行，五种职责
- `xmpp_a2a.py` 同时承担：disco 注册 / PEP 发布 / config 加载 / ad-hoc 命令注册 / 出站调用 / 表单编解码。
- **建议**：拆为 `A2ADiscoveryService / A2APubSubService / A2AAdhocRegistry / A2AAdhocCaller / A2AFormCodec`；每个文件 200 行以内。

### E2. **High** — `a2a_task` 本地 fallback 与 `a2aserver` 行为漂移
- `a2a_commands/a2a_task.py:171-246` 自行实现了一份 `tasks/send` 的兜底逻辑（识别 card-like data → 调 `exchange_business_card`）；与 `a2aserver/server.py:102-153` 主实现并行。
- **问题**：未来新增 method（例如 `tasks/get` 或 streaming）只在 a2aserver 实现 → fallback 行为偏离 → 8789 挂掉时静默退化但用户感知不到。
- **建议**：要么完全去掉 fallback（强依赖 8789），要么把 8789 的处理函数搬到共享模块两边复用。

### E3. **High** — 三处副本的 "6 dirname" 魔法路径
- `xmpp_a2a.py:164`、`a2a_commands/exchange_business_card.py:106-110`、`a2a_commands/a2a_task.py:254-258`：完全相同的 `os.path.dirname` × 6 解析 project root。
- **风险**：目录结构调整时必须改 3 处，少改一处就炸。
- **建议**：在 `runtime/shared/paths.py` 暴露 `PROJECT_ROOT`，所有用例 `from runtime.shared.paths import PROJECT_ROOT`。

### E4. **High** — 主进程 agent card 端点与 A2A 子进程并存
- 主进程 `/a2a/{agent_id}/.well-known/agent-card.json`（`api_server.py:321-326`）始终在线，与 8789 子进程独立；开关 `a2a_server_enabled` 只控子进程，外部探测一致性差。
- **建议**：两者二选一；保留主进程那条更合理（无需子进程），把 a2aserver 重定位为"业务名片管理 UI"，把 JSON-RPC 端点也搬到主进程。

### E5. **Medium** — `xep_0050.commands` dict key shape 兼容多 slixmpp 版本
- `xmpp_a2a.py:946-954` 显式兼容 `key=node` 与 `key=(jid, node)` 两种 shape，说明 slixmpp 版本未固定。生产中如果 pip 升级了 slixmpp，行为可能突变。
- **建议**：在 `requirements.txt` pin `slixmpp==<verified-version>`，并在 CI 加 import smoke test。

### E6. **Medium** — `on_message` 既写库又调引擎，强耦合
- `xmpp_client.py:288-413`：DB 写与 Engine forward 一锅炖；任一失败被 try 吞，互不知道。
- **建议**：改 producer/consumer：`on_message` 只入 in-memory queue + WS 广播 + write_queue；engine 作为 consumer，单独 task pull。

### E7. **Medium** — `ensure_mutual_subscription` 应该是引擎层关注，而非每条消息
- `xmpp_client.py:572-580`：`send_message_to_jid` 每次都 `await ensure_mutual_subscription`。
- **建议**：把"首次握手"做成"对每个 JID 一次"的幂等动作（缓存 `subscribed_set`）；后续消息直接发，握手只在显式"添加好友" / 首次"打招呼"时触发。

### E8. **Medium** — `SystemInitWizardService.test_xmpp` 自建临时 ClientXMPP
- `runtime/modules/system/service.py:527-710`：测试连接占用对方账号一个 resource，对 server 端连接数有压力；频繁点测试会有限流风险。
- **建议**：复用主 `XMPPClientManager`，把"测试"做成 dry-run（连上就 disconnect，不订阅 roster），最大并发 1。

### E9. **Low** — 命名空间 URI 三个语义不清
- `A2A_FEATURE_NS = urn:xmpp:a2a:1` 与 `A2A_BUSINESS_CARD_NS = urn:xmpp:a2a:business_card:1` 同时存在，对端只要支持其中一个就算"支持 A2A"（`xmpp_a2a.py:450`），这违反 XEP-0030 feature 的常用语义（一个 feature 表示一个具体能力）。
- **建议**：保留 `urn:xmpp:a2a:1` 作为父能力，业务子能力单独 advertise（`urn:xmpp:a2a:cmd:tasks` / `urn:xmpp:a2a:cmd:exchange_business_card`）。

### E10. **Low** — `format_internal_xmpp_message_for_storage` 黑盒
- `xmpp_client.py:309`、`service_async.py:537, 698`：对入站正文做改写。如果未来加 markdown / 链接处理，可能破坏 PEP 内容或文件 URL（XEP-0363 上传后的 URL 也走这条管道）。
- **建议**：把"存档格式化"与"原始正文"分离，DB 同时存两份（raw + formatted）。

---

## §F 遗漏 / 安全 / 其他

### F1. **Critical** — `a2aserver` 监听 `0.0.0.0:8789` 且 REST 无鉴权
- `@c:\dev\agi-ev\ai-sns-el\a2aserver\server.py:211`：`uvicorn.run(app, host="0.0.0.0", port=8789, log_level="info")`
- 暴露：
  - `GET /api/my-card` — 读我方名片
  - `POST /api/my-card` — 改我方名片
  - `GET /api/received-cards` — 看所有收到的名片（包含对方 jid/email/phone）
  - `DELETE /api/received-cards/{card_id}` — 删名片
  - `POST /a2a/` — 触发任意 `tasks/send`
- **威胁模型**：局域网（公司 / 公共 wifi）下任何人通过 `http://<host>:8789/api/received-cards` 一行 curl 就能拿全部名片库。
- **建议**：
  1. **立即**：把 `host="0.0.0.0"` 改成 `host="127.0.0.1"`；
  2. 加 token 鉴权头（主进程启动子进程时通过环境变量传入 shared secret）；
  3. 默认禁用 REST 写接口，UI 通过主进程代理调用。

### F2. **Critical** — `/api/sns/xmpp-a2a/debug/*` 与 `/api/sns/xmpp-a2a/call` 无鉴权
- `@c:\dev\agi-ev\ai-sns-el\aisns_backend\runtime\apps\sns\router.py:612-895`
- 任何能访问 8000 端口的人都可以：
  - 看到本机 agent_card / PEP XML（隐私泄漏）
  - 用本机名片向任意 JID 触发 exchange_business_card（外发我方名片）
  - 发任意 JSON-RPC `/xmpp-a2a/call`（可滥用本账号 A2A 资源）
- **建议**：复用现有 session/cookie 鉴权 middleware；对 debug 接口默认只接受本机 IP。

### F3. **High** — `_sync_http_get` 不限大小
- `xmpp_a2a.py:97-111`：`resp.read()` 无 maxlen；恶意 URL 返回上百 MB 会 OOM。
- **建议**：限制 `read(N)` 并校验 Content-Length。

### F4. **High** — `on_message` body 不限长度
- `xmpp_client.py:292-298`：1 MB 文本消息会原样写库 + WS 广播 → 内存与带宽放大。
- **建议**：入口阶段截断到 64 KB，超长 log warning。

### F5. **High** — `exchange_business_card` 输入无长度限制 / 不转义
- `a2aserver/business_card.py:11-34`、`a2aserver/db.py:109-133`：对方提交的 7 字段全部直接落 SQLite。后续 web UI 渲染时若模板未转义，存储型 XSS。
- **建议**：入库时按字段长度截断 + html-escape 一份用于显示。

### F6. **Medium** — `InitializationWizard.test-xmpp` 明文密码走 HTTP
- `frontend → /api/system/init-wizard/test-xmpp` body 含 `account_password`（`service.py:527-710`）。本机 OK；如果反向代理把 8000 暴露到外网，HTTP 明文传 XMPP 密码。
- **建议**：在文档里强制 HTTPS，或限制该 endpoint 只接受本机 IP。

### F7. **Medium** — PEP 节点未设置 publishing options
- `xmpp_a2a.py:229-233`：`publish(... id="current")` 没传 `options`，server 默认配置可能不是 PEP 模式（`pubsub#access_model=presence`, `pubsub#notify_retract`...）；某些 ejabberd 配置下变成 transient bare node，好友拿不到推送。
- **建议**：传 `options={"pubsub#access_model":"presence","pubsub#max_items":1,"pubsub#notify_retract":True}`。

### F8. **Medium** — `discover_peer_a2a` 用 `A2A_FEATURE_NS in features or A2A_BUSINESS_CARD_NS in features`
- `xmpp_a2a.py:450`：任一即"支持 A2A"。如果对端只 advertise 旧版本 namespace，会被当 A2A 节点；后续 ad-hoc 调用可能不兼容。
- **建议**：精确匹配 + 版本号策略（参见 E9）。

### F9. **Medium** — `heartbeat` 无 jitter
- `xmpp_client.py:548-570`：所有客户端整齐 30 s 一次 ping，规模化部署后 XMPP 服务器会感受到周期性 spike。
- **建议**：`await asyncio.sleep(self.heartbeat_interval + random.uniform(-3, 3))`。

### F10. **Low** — `del_roster_item` 后未确认 server 回 IQ result
- `xmpp_client.py:235-243`：发 unsubscribe + unsubscribed 但不等响应，roster cleanup 可能客户端以为成功、server 实际拒绝。
- **建议**：`await iq.send()` 拿 result，失败计入 `failed`。

### F11. **Low** — 缺少 metrics / 可观测性
- A2A 调用次数、成功率、超时分布、PEP fetch 命中率等没暴露，问题难定位。
- **建议**：加一个 Prometheus exporter 或简单的 `/api/sns/xmpp-a2a/stats`。

### F12. **Low** — `XMPPClient` 注册 plugin 时仅 xep_0030 没 try
- `xmpp_client.py:34`：与下面其它 plugin 不一致；不影响功能但风格不统一。

### F13. **Info** — `groupchat`/`headline` 消息未处理
- `xmpp_client.py:290`：`if msg['type'] in ('chat','normal')` 跳过 MUC / headline；当前业务不需要，但要在 README 说明，避免被误以为支持群聊。

### F14. **Info** — `a2aserver` 使用同步 sqlite3 + 同步 FastAPI handler
- `a2aserver/server.py` 的 `/api/*` 全是 `async def` 但内部 `sqlite3` 是同步阻塞 — 因为请求量小可接受，但要标注。

---

## §G 复现 / 验证手段

| 问题 | 验证 |
| --- | --- |
| F1 | `curl http://<lan-ip>:8789/api/received-cards` |
| F2 | `curl http://<lan-ip>:8000/api/sns/xmpp-a2a/debug/pep-items` |
| A1 | 同时给本机连发 50 条 `<message>`，观察心跳 ping 日志是否 >10 s |
| A5 | DELETE `ai_friend` 表中对方记录，前端发消息，看是否卡 30 s |
| D1 | 把 `aisns_cfg.memo` 写成 `"this is not json"`，重启后端，看 `GET /api/sns/xmpp-a2a/debug/status` 是否 `disco_features=[]` |
| D4 | 启动后 `taskkill /f /pid <a2a_pid>`，再发 `POST /api/sns/xmpp-a2a/call`，观察是否 fallback 到本地 |
| F5 | 用 swift/conversations 客户端调 `exchange_business_card` 提交 `<script>...</script>`，看名片 UI 渲染 |

---

## §H 修复优先级建议

**P0（立刻修，建议本次发版前完成）**
1. F1 — `a2aserver` 绑定 `127.0.0.1` 并加 token 鉴权
2. F2 — `/api/sns/xmpp-a2a/*` 加现有 session 鉴权
3. A1 — `on_message` 改 async 写库
4. D1 — `initialize()` task 加 done callback + 重试

**P1（一周内）**
5. A2 / A5 / D2 / D3 / D4 / A4 / A6 / A7
6. C2 / C3 / C4 / C6
7. A3 / D6 / D7 — Session 生命周期与双向引用

**P2（视情况）**
8. §E 架构拆分
9. §B 健壮性细节
10. §F 其它安全 / 可观测性

---

## §I 附：未在本报告范围的事项
- 不评估 SNS Engine 内部 LLM 工具调度（仅评估它与 XMPP 边界）
- 不评估 mapvgl 前端非 XMPP 部分
- 不做单元测试编写
- 不做 slixmpp 库本身的 bug 评估

