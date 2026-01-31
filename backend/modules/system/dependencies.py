# -*- coding: utf-8 -*-
"""
System module - Dependencies
"""
from .service import SystemService, SystemInitWizardService


def get_system_service() -> SystemService:
    """Get system service instance"""
    return SystemService()


def get_system_init_wizard_service() -> SystemInitWizardService:
    return SystemInitWizardService()
