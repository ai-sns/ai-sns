# -*- coding: utf-8 -*-
"""
System module - Pydantic schemas
"""
from typing import Optional, List
from pydantic import BaseModel


class SystemConfig(BaseModel):
    """System configuration model"""
    theme: Optional[str] = "dark"
    language: Optional[str] = "zh"
    minirunontray: Optional[bool] = True


class WebMngReorderItem(BaseModel):
    """Web management reorder item"""
    id: int
    position: int


class WebMngReorderRequest(BaseModel):
    """Web management reorder request"""
    items: List[WebMngReorderItem]
