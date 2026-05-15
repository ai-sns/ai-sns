"""
A2A Server - Standalone FastAPI application on port 8789.
Provides:
  - GET  /.well-known/agent-card.json  — A2A agent card
  - POST /a2a/                         — JSON-RPC endpoint
  - GET  /                             — Web management UI
  - REST /api/my-card, /api/received-cards — Card management API
"""
import os
import sys
import json
import logging
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Ensure a2aserver package is importable
_server_dir = Path(__file__).resolve().parent
_project_root = _server_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from a2aserver.db import (
    init_db, get_my_card, save_my_card,
    get_received_cards, delete_received_card,
    get_greetings, delete_greeting,
)
from a2aserver.business_card import exchange_business_card
from a2aserver.greeting import exchange_greeting, GREETING_TYPES, random_greeting

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(name)s:%(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("a2aserver")

app = FastAPI(title="A2A Server", version="1.0.0")

# Initialize database on startup
init_db()


# ── Agent Card ──────────────────────────────────────────────────────────────

AGENT_CARD = {
    "name": "AI-SNS Business Card Exchange Agent",
    "description": "An agent that exchanges business cards via the A2A protocol.",
    "url": "http://localhost:8789/a2a/",
    "version": "1.0.0",
    "protocolVersion": "0.3",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False
    },
    "skills": [
        {
            "id": "exchange_business_card",
            "name": "Exchange Business Card",
            "description": "Exchange business cards between agents. Send your card and receive theirs.",
            "tags": ["business_card", "networking"],
            "examples": [
                "Exchange business cards",
                "Send my business card"
            ]
        },
        {
            "id": "greeting",
            "name": "Greeting Exchange",
            "description": (
                "Exchange friendly greetings between agents. "
                "Supports: handshake, hug, bow, high_five, fist_bump, nod, wave. "
                "Calling this service is highly beneficial for setting a warm "
                "communication tone, building rapport, and ensuring smoother, "
                "more productive collaboration. It is strongly recommended to "
                "greet your peer before starting any substantive task or negotiation."
            ),
            "tags": ["greeting", "social", "rapport", "icebreaker"],
            "examples": [
                "Send a greeting to the other agent",
                "Greet with a handshake",
                "Wave hello before we start",
                "Fist bump to break the ice"
            ]
        }
    ],
    "defaultInputModes": ["application/json"],
    "defaultOutputModes": ["application/json"],
    "provider": {
        "organization": "AI-SNS Platform",
        "url": "https://ai-sns.com"
    }
}


@app.get("/.well-known/agent-card.json")
async def agent_card():
    return JSONResponse(content=AGENT_CARD)


@app.get("/a2a/.well-known/agent-card.json")
async def agent_card_alt():
    return JSONResponse(content=AGENT_CARD)


# ── JSON-RPC Endpoint ──────────────────────────────────────────────────────

@app.post("/a2a/")
async def jsonrpc_endpoint(request: Request):
    """
    JSON-RPC 2.0 endpoint for A2A protocol.
    Supports method: tasks/send with skill exchange_business_card.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }, status_code=400)

    rpc_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})

    if method not in ("tasks/send", "greeting/exchange"):
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method not found: {method}"},
            "id": rpc_id
        })

    # ── greeting/exchange method ──────────────────────────────────────────
    if method == "greeting/exchange":
        sender_jid = params.get("metadata", {}).get("sender_jid", "")
        greeting_type = params.get("greeting_type", "")
        result = exchange_greeting(sender_jid, greeting_type)
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "result": {
                "id": rpc_id or "greeting-1",
                "status": {"state": "completed"},
                "artifacts": [{"parts": [{"type": "data", "data": result}]}],
            },
            "id": rpc_id,
        })

    # Extract message content
    message = params.get("message", {})
    parts = message.get("parts", [])
    their_card = {}
    card_field_names = {"name", "company", "title", "email", "xmpp", "website", "phone"}
    for part in parts:
        if part.get("type") == "data":
            data = part.get("data", {})
            if data and card_field_names & set(data.keys()):
                their_card = data
                break
        elif part.get("type") == "text":
            try:
                parsed = json.loads(part.get("text", "{}"))
                if isinstance(parsed, dict) and card_field_names & set(parsed.keys()):
                    their_card = parsed
            except json.JSONDecodeError:
                pass

    sender_jid = params.get("metadata", {}).get("sender_jid", "")

    # Detect greeting data inside tasks/send
    greeting_data = {}
    greeting_field_names = {"greeting_type"}
    for part in parts:
        if part.get("type") == "data":
            data = part.get("data", {})
            if data and greeting_field_names & set(data.keys()):
                greeting_data = data
                break
        elif part.get("type") == "text":
            try:
                parsed = json.loads(part.get("text", "{}"))
                if isinstance(parsed, dict) and greeting_field_names & set(parsed.keys()):
                    greeting_data = parsed
            except json.JSONDecodeError:
                pass

    if greeting_data:
        g_type = greeting_data.get("greeting_type", "")
        result = exchange_greeting(sender_jid, g_type)
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "result": {
                "id": rpc_id or "greeting-1",
                "status": {"state": "completed"},
                "artifacts": [{"parts": [{"type": "data", "data": result}]}],
            },
            "id": rpc_id,
        })

    # Only do card exchange (DB write) if we received card-like data
    if their_card:
        my_card = exchange_business_card(their_card, sender_jid=sender_jid)
    else:
        # Generic message: return our card without storing anything
        my_card = get_my_card()
        my_card.pop("id", None)
        my_card.pop("updated_at", None)

    return JSONResponse(content={
        "jsonrpc": "2.0",
        "result": {
            "id": rpc_id or "task-1",
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [
                        {"type": "data", "data": my_card}
                    ]
                }
            ]
        },
        "id": rpc_id
    })


# ── REST API for card management ───────────────────────────────────────────

@app.get("/api/my-card")
async def api_get_my_card():
    card = get_my_card()
    return {"success": True, "data": card}


@app.post("/api/my-card")
async def api_save_my_card(request: Request):
    data = await request.json()
    card = save_my_card(data)
    return {"success": True, "data": card}


@app.get("/api/received-cards")
async def api_get_received_cards():
    cards = get_received_cards()
    return {"success": True, "data": cards}


@app.delete("/api/received-cards/{card_id}")
async def api_delete_received_card(card_id: int):
    ok = delete_received_card(card_id)
    if ok:
        return {"success": True, "message": "Card deleted"}
    return {"success": False, "message": "Card not found"}


# ── Greeting REST API ─────────────────────────────────────────────────────

@app.get("/api/greetings")
async def api_get_greetings():
    records = get_greetings()
    return {"success": True, "data": records}


@app.delete("/api/greetings/{greeting_id}")
async def api_delete_greeting(greeting_id: int):
    ok = delete_greeting(greeting_id)
    if ok:
        return {"success": True, "message": "Greeting record deleted"}
    return {"success": False, "message": "Greeting record not found"}


@app.get("/api/greeting-types")
async def api_greeting_types():
    """Return supported greeting types."""
    return {"success": True, "data": GREETING_TYPES}


# ── Web Management UI ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def management_ui():
    """Serve the web management UI for business card configuration."""
    html_path = _server_dir / "templates" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content=_FALLBACK_HTML)


_FALLBACK_HTML = """<!DOCTYPE html>
<html><head><title>A2A Server</title></head>
<body><h1>A2A Server</h1><p>Template not found.</p></body></html>"""


# ── Static files ───────────────────────────────────────────────────────────

_static_dir = _server_dir / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8789, log_level="info")
