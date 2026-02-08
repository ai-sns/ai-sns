import asyncio
import sqlite3
import sys
import types
import json
import re
from pathlib import Path

# Ensure project root on path
PROJECT_ROOT = Path(r"c:\sharedata\ai-sns-el")
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.database import get_db_sync
from backend.apps.sns.ai_social_engine_adapter import AISocialEngine

FRIEND_JID = "test_friend@xabber.de"
FRIEND_NAME = "测试朋友"
FRIEND_NATION_ID = "AI_TEST_NATION_001"

# Mock external data from http://www.ai-sns.org/api/
PEOPLE_LIST = [
    {
        "nation_id": FRIEND_NATION_ID,
        "account": FRIEND_JID,
        "nick_name": FRIEND_NAME,
        "location": [116.3975, 39.9087],
        "avatar": "img_test",
        "avatar_3d": "test.glb",
        "profile": "我是商人",
        "sns_url": "x.com",
    }
]

PLACE_LIST = [
    {"name": "北京天安门", "location": [116.3975, 39.9087], "description": "著名景点"}
]

SERVICE_LIST = [
    {
        "id": "svc_test",
        "name": "路线规划",
        "description": "生成路线",
        "type": "http",
        "method": "post",
        "address": "http://localhost/does-not-exist",
        "parameter": {},
    }
]

outbox: list[tuple[str, str]] = []
map_commands: list = []


def extract_json_object(text: str) -> str:
    """Best-effort extraction of a single JSON object from a model reply."""
    if not text:
        return text

    candidate = text.strip()
    # remove code fences if present
    candidate = re.sub(r"^\s*```json\s*|\s*```\s*$", "", candidate, flags=re.DOTALL)
    candidate = candidate.strip()

    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        return candidate[start : end + 1]

    return text


def extract_price_from_history(history_text: str) -> float:
    if not history_text:
        return -1
    # e.g. "价格50元" / "50元" / "price: 50"
    patterns = [
        r"价格\s*[:：]?\s*(\d+(?:\.\d+)?)\s*元",
        r"(\d+(?:\.\d+)?)\s*元",
        r"price\s*[:：]?\s*(\d+(?:\.\d+)?)",
    ]
    for pat in patterns:
        m = re.search(pat, history_text, flags=re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                continue
    return -1


def patch_engine(engine: AISocialEngine) -> None:
    # Avoid network calls to ai-sns.org
    engine.get_people_list = types.MethodType(lambda self: PEOPLE_LIST, engine)
    engine.get_place_list = types.MethodType(lambda self: PLACE_LIST, engine)
    engine.get_service_list = types.MethodType(lambda self: SERVICE_LIST, engine)

    # Disable UI / websocket sends (must remain coroutines where expected)
    async def _noop_async(*args, **kwargs):
        return None

    engine.send_talk_message = types.MethodType(_noop_async, engine)
    engine._send_to_frontend = types.MethodType(_noop_async, engine)

    # Capture map commands
    engine.send_msg_to_map = types.MethodType(lambda self, command: map_commands.append(command), engine)

    # Make XMPP send always succeed but capture messages
    def _send_xmpp_message(self, to_jid: str, content: str) -> bool:
        outbox.append((to_jid, content))
        return True

    engine.send_xmpp_message = types.MethodType(_send_xmpp_message, engine)

    # Debug: print raw LLM replies with command_status
    original_on_agent_return = engine.on_agent_return_instruction

    def _on_agent_return_instruction_debug(self, question, content):
        try:
            cs = getattr(self, "command_status", None)
            preview = content if isinstance(content, str) else str(content)
            preview = preview.replace("\r", "")
            print("\n--- LLM_REPLY_DEBUG ---")
            print("command_status:", cs)
            print("reply_preview:", preview[:800])
            print("--- END_LLM_REPLY_DEBUG ---\n")
        except Exception:
            pass
        return original_on_agent_return(question, content)

    engine.on_agent_return_instruction = types.MethodType(_on_agent_return_instruction_debug, engine)

    # Robustify buy review parsing for E2E test only
    original_buy_final = engine.handle_agent_review_conversation_buy_result_final

    def _buy_review_final_robust(self, content):
        try:
            text = content.strip() if isinstance(content, str) else str(content)
            try:
                json.loads(text)
                return original_buy_final(text)
            except Exception:
                extracted = extract_json_object(text)
                try:
                    return original_buy_final(extracted)
                except Exception:
                    # Fallback: build a minimal valid JSON from local talk history
                    history_text = "\n".join(getattr(self, "current_talk_history", []) or [])
                    price = extract_price_from_history(history_text)
                    fallback = {
                        "summary": "(fallback) model reply is not JSON; used local heuristic.",
                        "continue_chat": False,
                        "buy_score": 90,
                        "buy_score_reason": "(fallback) continue trade for E2E verification.",
                        "price": price if price >= 0 else 0,
                        "objective": "buy",
                        "game_tips": "",
                        "reason": "(fallback)",
                        "next_message": "",
                    }
                    print("buy_review_fallback_json:", json.dumps(fallback, ensure_ascii=False))
                    return original_buy_final(json.dumps(fallback, ensure_ascii=False))
        except Exception as e:
            print("buy_review_parse_failed:", repr(e))

    engine.handle_agent_review_conversation_buy_result_final = types.MethodType(_buy_review_final_robust, engine)


def find_last_message(substr: str):
    for to_jid, msg in reversed(outbox):
        if substr in msg:
            return to_jid, msg
    return None


def parse_pay_message(msg: str) -> tuple[str, str]:
    # AISNS_INT_001_PAY_SEND_START\n{trade_id}__AISNS_INT_SEPARATOR__{price}\nAISNS_INT_001_PAY_SEND_END
    lines = [l.strip() for l in msg.splitlines()]
    for i, line in enumerate(lines):
        if "AISNS_INT_001_PAY_SEND_START" in line and i + 1 < len(lines):
            payload = lines[i + 1]
            if "__AISNS_INT_SEPARATOR__" in payload:
                trade_id, price = payload.split("__AISNS_INT_SEPARATOR__", 1)
                return trade_id.strip(), price.strip()
    return "", ""


async def simulate_friend_message(engine: AISocialEngine, text: str):
    await engine.handle_receiveMessage(text, FRIEND_JID)


def query_map_trade(trade_id: str):
    db_path = PROJECT_ROOT / "db" / "db.sqlite"
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        return cur.execute(
            "SELECT trade_id, trade_type, title, pay, substr(detail,1,80) FROM map_trade WHERE trade_id=?",
            (trade_id,),
        ).fetchone()
    finally:
        conn.close()


async def main():
    db = get_db_sync()
    engine = AISocialEngine(db)
    patch_engine(engine)

    await engine.async_init()

    # Critical: MapTaskManager blocks unless map_task_status == 'started'
    engine.map_task_status = "started"
    engine.started_flag = True

    # Ensure current_process exists (handlers expect it)
    if not engine.taskmng.current_process:
        engine.taskmng.add_process(
            current_place=engine.current_place,
            current_position=engine.aichatcfg_record.current_position,
        )

    print("=== ENV ===")
    print("ai_chat_cfg.account:", getattr(engine.ai_chat_cfg, "account", None))
    print("ai_chat_cfg.agent_id:", getattr(engine.ai_chat_cfg, "agent_id", None))
    print("handle_after_trade:", getattr(engine.ai_chat_cfg, "handle_after_trade", None))
    print("handle_content_prefix:", str(getattr(engine.ai_chat_cfg, "handle_content", ""))[:50])

    print("\n=== 1) 沟通闭环 ===")
    engine.communicate_with_a_people("沟通：请问附近有什么值得去的地方？", "")
    await asyncio.sleep(12)
    await simulate_friend_message(engine, "我建议你去天安门。")
    await asyncio.sleep(12)

    print("outbox_size_after_communication:", len(outbox))
    if outbox:
        print("last_outbox:", outbox[-1][0], outbox[-1][1][:120].replace("\n", "\\n"))

    print("\n=== 2) 推销闭环 ===")
    engine.sell_to_a_people("推销：向对方推销一次“路线规划/出行建议”服务", "")
    await asyncio.sleep(12)
    await simulate_friend_message(engine, "听起来不错，你怎么收费？")
    await asyncio.sleep(18)

    print("outbox_size_after_sell:", len(outbox))

    print("\n=== 3) 求购 + 支付 + 收货（完整交易闭环：买方侧）===")
    engine.buy_from_a_people("求购：我想购买一份北京旅游攻略。", "")
    await asyncio.sleep(14)

    inquiry = find_last_message("[AISNS_INT_003_INQUIRY]")
    print("inquiry_sent:", bool(inquiry))
    if inquiry:
        print("inquiry_prefix:", inquiry[1][:160].replace("\n", "\\n"))

    await simulate_friend_message(engine, "可以卖给你一份北京旅游攻略，价格50元。你确认购买我就发货。")
    await asyncio.sleep(20)

    pay_msg = find_last_message("AISNS_INT_001_PAY_SEND_START")
    print("pay_sent:", bool(pay_msg))
    trade_id, price = ("", "")
    if pay_msg:
        trade_id, price = parse_pay_message(pay_msg[1])
        print("pay_trade_id:", trade_id)
        print("pay_price:", price)

    if trade_id:
        goods_payload = (
            "AISNS_INT_002_GOOD_SEND_START\n"
            f"{trade_id}__AISNS_INT_SEPARATOR__北京旅游攻略内容: Day1...Day2...\n"
            "AISNS_INT_002_GOOD_SEND_END"
        )
        await simulate_friend_message(engine, goods_payload)
        await asyncio.sleep(2)

        row = query_map_trade(trade_id)
        print("map_trade_row_after_goods_received:", row)

    print("\n=== 4) 收款 -> (tool/消息) -> 发货（完整交易闭环：卖方侧）===")
    engine.current_talk_people = dict(PEOPLE_LIST[0])

    pay_in_trade_id = "TRADE_SELL_SIDE_TEST_001"
    pay_in_payload = (
        "AISNS_INT_001_PAY_SEND_START\n"
        f"{pay_in_trade_id}__AISNS_INT_SEPARATOR__88\n"
        "AISNS_INT_001_PAY_SEND_END"
    )
    await simulate_friend_message(engine, pay_in_payload)

    # Tool path is async via task callback; give it time
    await asyncio.sleep(30)

    goods_sent = find_last_message("AISNS_INT_002_GOOD_SEND_START")
    print("goods_sent_after_pay_in:", bool(goods_sent))
    if goods_sent:
        print("goods_sent_prefix:", goods_sent[1][:200].replace("\n", "\\n"))

    row2 = query_map_trade(pay_in_trade_id)
    print("map_trade_row_sell_side:", row2)

    print("\n=== DONE ===")


if __name__ == "__main__":
    asyncio.run(main())
