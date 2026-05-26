# -*- coding: utf-8 -*-
"""
Map module - WebSocket handling
"""
import asyncio
import logging
from typing import Dict
from fastapi import WebSocket
from runtime.shared import debug_info

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, message: dict, client_id: str):
        """Send message to a specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections.values():
            await connection.send_json(message)


# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket_message(data: dict, client_id: str):
    """
    Handle incoming WebSocket message

    Args:
        data: Message data
        client_id: Client ID
    """
    msg_type = data.get("type", "")

    if msg_type == "chat":
        # Handle chat message
        agent_id = data.get("agent_id")
        message = data.get("message")

        # Get Agent reply
        from runtime.modules.chat.service import agent_instances
        agent_key = f"agent_{agent_id}"
        if agent_key not in agent_instances:
            from Agent import Agent
            agent_instances[agent_key] = Agent()

        agent = agent_instances[agent_key]
        response = await asyncio.to_thread(agent.chat, message)

        await manager.send_message({
            "type": "chat_response",
            "agent_id": agent_id,
            "response": response
        }, client_id)

    elif msg_type == "ping":
        await manager.send_message({"type": "pong"}, client_id)
