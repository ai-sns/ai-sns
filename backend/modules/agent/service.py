# -*- coding: utf-8 -*-
"""
Agent module - Service layer
"""
import logging
import json
from typing import List, Dict, Any, Optional
from db.DBFactory import (
    add_AgentCfg,
    query_AgentCfg_All,
    update_AgentCfg,
    delete_AgentCfg,
    Session,
    AgentCfg
)

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agents"""

    @staticmethod
    def get_all_agents() -> List[Dict[str, Any]]:
        """Get all agent configurations"""
        agents = query_AgentCfg_All()
        result = []
        for agent in agents:
            # 尝试从 memo 字段解析 JSON 存储的额外数据
            extra_data = {}
            try:
                if agent.memo:
                    extra_data = json.loads(agent.memo)
            except:
                pass

            result.append({
                "id": agent.id,
                "name": agent.name,
                "description": extra_data.get('description', ''),
                "model": getattr(agent, 'defaultmodel', 'gpt-4'),
                "model_config_id": extra_data.get('model_config_id', ''),
                "role_id": extra_data.get('role_id', ''),
                "url": extra_data.get('url', ''),
                "wallet_address": extra_data.get('wallet_address', ''),
                "is_active": getattr(agent, 'is_show', True)
            })
        return result

    @staticmethod
    def create_agent(**kwargs) -> int:
        """
        Create a new agent

        Supports both old and new field names.
        New fields (A2A protocol, wallet, etc.) are stored in memo field as JSON.
        """
        # 提取必需的旧字段
        name = kwargs.get('name', 'New Agent')

        # 将新字段打包到 memo 中
        extra_data = {
            'description': kwargs.get('description', ''),
            'model_config_id': kwargs.get('model_config_id', ''),
            'role_id': kwargs.get('role_id', ''),
            'url': kwargs.get('url', ''),
            'version': kwargs.get('version', '1.0.0'),
            'protocol_version': kwargs.get('protocol_version', '0.3'),
            'capabilities': kwargs.get('capabilities', {}),
            'skills': kwargs.get('skills', []),
            'default_input_modes': kwargs.get('default_input_modes', ['text']),
            'default_output_modes': kwargs.get('default_output_modes', ['text']),
            'security_schemes': kwargs.get('security_schemes', {}),
            'provider_organization': kwargs.get('provider_organization', ''),
            'provider_url': kwargs.get('provider_url', ''),
            'documentation_url': kwargs.get('documentation_url', ''),
            'icon_url': kwargs.get('icon_url', ''),
            'wallet_address': kwargs.get('wallet_address', ''),
        }
        memo = json.dumps(extra_data, ensure_ascii=False)

        # 准备旧字段参数
        user_id = kwargs.get('user_id', 'default_user')
        defaultmodel = kwargs.get('model_config_id', kwargs.get('model', 'gpt-4'))
        defaultrole = kwargs.get('role_id', '')
        prompt = kwargs.get('system_prompt', '')

        # 使用默认值调用旧的 add_AgentCfg
        try:
            session = Session()
            agent = AgentCfg(
                user_id=user_id,
                name=name,
                memo=memo,
                borndate=None,  # Use None instead of empty string for DateTime
                borncontry='',
                language='',
                gender='',
                joinfederation=False,  # Boolean, not empty string
                syncfederation=False,  # Boolean, not empty string
                federationid='',
                defaultmodel=defaultmodel,
                defaultrole=defaultrole,
                lastmodel='',
                lastrole='',
                specialization='',
                plugins='',
                kms='',
                last_plugins='',
                last_kms='',
                prompt=prompt,
                snsaccount='',
                snsnickname='',
                islimittotalmessage=False,
                islimitmessagepp=False,
                totalmessages=0,
                ppmessages=0,
                readfile=True,
                writefile=True,
                deletefile=False,
                execfile=False,
                uselastmodel=False,
                uselastrole=False,
                uselastplugins=False,
                uselastkms=False,
                callpluginbyinstruct=False,
                modelfrequent=False,  # Boolean, not empty string
                rolefrequent=False,  # Boolean, not empty string
                multimodelfrequent=False,  # Boolean, not empty string
                autorunrounds=0,
                is_show=kwargs.get('is_active', True)
            )
            session.add(agent)
            session.commit()
            agent_id = agent.id
            session.close()
            return agent_id
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            raise

    @staticmethod
    def get_agent(agent_id: int) -> Optional[Dict[str, Any]]:
        """Get a single agent by ID"""
        session = Session()
        agent = session.query(AgentCfg).filter_by(id=agent_id).first()
        session.close()

        if not agent:
            return None

        # 解析 memo 中的额外数据
        extra_data = {}
        try:
            if agent.memo:
                extra_data = json.loads(agent.memo)
        except:
            pass

        return {
            "id": agent.id,
            "name": agent.name,
            "description": extra_data.get('description', ''),
            "model": getattr(agent, 'defaultmodel', 'gpt-4'),
            "model_config_id": extra_data.get('model_config_id', ''),
            "role_id": extra_data.get('role_id', ''),
            "system_prompt": getattr(agent, 'prompt', ''),
            "url": extra_data.get('url', ''),
            "version": extra_data.get('version', '1.0.0'),
            "protocol_version": extra_data.get('protocol_version', '0.3'),
            "capabilities": extra_data.get('capabilities', {}),
            "skills": extra_data.get('skills', []),
            "default_input_modes": extra_data.get('default_input_modes', ['text']),
            "default_output_modes": extra_data.get('default_output_modes', ['text']),
            "security_schemes": extra_data.get('security_schemes', {}),
            "provider_organization": extra_data.get('provider_organization', ''),
            "provider_url": extra_data.get('provider_url', ''),
            "documentation_url": extra_data.get('documentation_url', ''),
            "icon_url": extra_data.get('icon_url', ''),
            "wallet_address": extra_data.get('wallet_address', ''),
            "is_active": getattr(agent, 'is_show', True)
        }

    @staticmethod
    def update_agent(agent_id: int, **kwargs) -> None:
        """Update agent configuration"""
        session = Session()
        agent = session.query(AgentCfg).filter_by(id=agent_id).first()

        if not agent:
            session.close()
            raise ValueError(f"Agent {agent_id} not found")

        # 解析现有的 memo
        extra_data = {}
        try:
            if agent.memo:
                extra_data = json.loads(agent.memo)
        except:
            pass

        # 更新基本字段
        if 'name' in kwargs:
            agent.name = kwargs['name']
        if 'model_config_id' in kwargs or 'model' in kwargs:
            agent.defaultmodel = kwargs.get('model_config_id', kwargs.get('model', agent.defaultmodel))
        if 'role_id' in kwargs:
            agent.defaultrole = kwargs['role_id']
        if 'system_prompt' in kwargs:
            agent.prompt = kwargs['system_prompt']
        if 'is_active' in kwargs:
            agent.is_show = kwargs['is_active']

        # 更新 memo 中的额外字段
        for key in ['description', 'url', 'version', 'protocol_version', 'capabilities',
                    'skills', 'default_input_modes', 'default_output_modes', 'security_schemes',
                    'provider_organization', 'provider_url', 'documentation_url',
                    'icon_url', 'wallet_address', 'model_config_id', 'role_id']:
            if key in kwargs:
                extra_data[key] = kwargs[key]

        agent.memo = json.dumps(extra_data, ensure_ascii=False)

        session.commit()
        session.close()

    @staticmethod
    def delete_agent(agent_id: int) -> None:
        """Delete an agent (soft delete)"""
        session = Session()
        agent = session.query(AgentCfg).filter_by(id=agent_id).first()
        if agent:
            agent.is_delete = True
            agent.is_show = False
            session.commit()
        session.close()

