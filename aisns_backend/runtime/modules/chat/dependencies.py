# -*- coding: utf-8 -*-
"""
Chat module - Dependencies
"""
from .service import ChatService
from .streaming import StreamingService
from runtime.shared import debug_info


def get_chat_service() -> ChatService:
    """Get chat service instance"""
    return ChatService()


def get_streaming_service() -> StreamingService:
    """Get streaming service instance"""
    return StreamingService()
