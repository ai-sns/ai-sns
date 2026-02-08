import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"c:\sharedata\ai-sns-el")
DB_PATH = PROJECT_ROOT / "db" / "db.sqlite"

TARGET_TITLES = [
    "__review_conversation__",
    "__review_conversation_buy__",
    "__review_conversation_sell__",
]

JSON_ENFORCEMENT_SUFFIX = "\n\nIMPORTANT: 你必须只输出一个JSON对象，且输出必须以'{'开始并以'}'结束；不得输出任何解释、Markdown、代码块标记(例如```json)、前后缀文字。若无法完成，仍必须返回一个JSON对象，字段齐全。\n"

BUY_SCORE_RULE_TAG = "BUY_SCORE_RULE_V1"
BUY_SCORE_RULE_SUFFIX = (
    "\n\n" + BUY_SCORE_RULE_TAG + ": "
    "如果聊天记录中已经出现明确报价（price可填写为>=0的数值），并且对话目标是购买/求购该商品或服务，"
    "则buy_score必须给到>=80，并且price字段必须填写当前达成的价格。\n"
)


def connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"db not found: {DB_PATH}")
    return sqlite3.connect(str(DB_PATH))


def table_info(conn, table: str):
    cur = conn.cursor()
    return cur.execute(f"PRAGMA table_info({table})").fetchall()


def list_titles(conn):
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT title, length(content) as len FROM prompts WHERE title IN (?,?,?)",
        TARGET_TITLES,
    ).fetchall()
    found = {r[0]: r[1] for r in rows}
    for title in TARGET_TITLES:
        print(f"{title}: {'FOUND' if title in found else 'MISSING'} len={found.get(title)}")


def backup_db() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_name(f"db.sqlite.bak_{ts}")
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def update_prompts(conn):
    cur = conn.cursor()
    for title in TARGET_TITLES:
        row = cur.execute("SELECT content FROM prompts WHERE title=?", (title,)).fetchone()
        if not row:
            print(f"SKIP missing title: {title}")
            continue
        content = row[0] or ""
        if "只输出一个JSON对象" in content or "IMPORTANT: 你必须只输出一个JSON对象" in content:
            print(f"SKIP already enforced: {title}")
            continue
        new_content = content + JSON_ENFORCEMENT_SUFFIX
        cur.execute("UPDATE prompts SET content=? WHERE title=?", (new_content, title))
        print(f"UPDATED: {title} (+{len(JSON_ENFORCEMENT_SUFFIX)} chars)")
    conn.commit()


def enhance_buy_prompt(conn):
    cur = conn.cursor()
    title = "__review_conversation_buy__"
    row = cur.execute("SELECT content FROM prompts WHERE title=?", (title,)).fetchone()
    if not row:
        print(f"SKIP missing title: {title}")
        return
    content = row[0] or ""
    if BUY_SCORE_RULE_TAG in content:
        print(f"SKIP already enhanced: {title}")
        return
    cur.execute("UPDATE prompts SET content=? WHERE title=?", (content + BUY_SCORE_RULE_SUFFIX, title))
    conn.commit()
    print(f"ENHANCED: {title} (+{len(BUY_SCORE_RULE_SUFFIX)} chars)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-schema", action="store_true")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--enhance-buy", action="store_true")
    args = ap.parse_args()

    conn = connect()
    try:
        if args.show_schema:
            info = table_info(conn, "prompts")
            print("prompts schema:")
            for cid, name, ctype, notnull, dflt, pk in info:
                print(f"  - {name} {ctype} pk={pk} notnull={notnull} default={dflt}")
            print()

        print("target titles:")
        list_titles(conn)
        print()

        if args.update:
            backup_path = backup_db()
            print(f"backup created: {backup_path}")
            update_prompts(conn)

        if args.enhance_buy:
            backup_path = backup_db()
            print(f"backup created: {backup_path}")
            enhance_buy_prompt(conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
