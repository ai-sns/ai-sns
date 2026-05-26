# -*- coding: utf-8 -*-
"""
Agent module - Dependencies
"""
from .service import AgentService
from runtime.shared import debug_info


def get_agent_service() -> AgentService:
    """Get agent service instance"""
    return AgentService()
