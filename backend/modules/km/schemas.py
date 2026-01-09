# -*- coding: utf-8 -*-
"""
KM module - Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel


class KMConfig(BaseModel):
    """Knowledge Management configuration model"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    km_type: Optional[str] = "vector"
    path: Optional[str] = ""


class KMResponse(BaseModel):
    """Knowledge Management response model"""
    id: int
    name: str
    description: Optional[str] = ""
    km_type: Optional[str] = "vector"
    path: Optional[str] = ""
