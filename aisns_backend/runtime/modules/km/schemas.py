# -*- coding: utf-8 -*-
"""
KM module - Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel
from runtime.shared import debug_info


class KMConfig(BaseModel):
    """Knowledge Management configuration model"""
    id: Optional[int] = None
    km_id: Optional[str] = None
    name: str
    memo: Optional[str] = ""
    label: Optional[str] = ""
    kmpath: Optional[str] = ""
    vectorization: Optional[bool] = True
    stopvectorization: Optional[bool] = False
    kmtype: Optional[int] = 1
    vectortype: Optional[str] = ""
    embeddingmodel: Optional[str] = ""
    textblocklength: Optional[int] = 1000
    overlaplength: Optional[int] = 100
    titleaugment: Optional[bool] = True
    config_param: Optional[str] = ""
    position: Optional[int] = None
    is_show: Optional[bool] = True


class KMResponse(BaseModel):
    """Knowledge Management response model"""
    id: int
    km_id: Optional[str] = None
    name: str
    memo: Optional[str] = ""
    kmtype: Optional[str] = "1"
    kmpath: Optional[str] = ""
    is_show: Optional[bool] = True
