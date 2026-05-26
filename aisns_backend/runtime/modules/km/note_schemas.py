# -*- coding: utf-8 -*-
"""
KM Note schemas - Data models for notes
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from runtime.shared import debug_info


class NoteCreate(BaseModel):
    """Request model for creating a note."""
    title: str
    content: str
    tags: Optional[List[str]] = []
    km_id: Optional[str] = None  # Knowledge base ID


class NoteUpdate(BaseModel):
    """Request model for updating a note."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


class NoteResponse(BaseModel):
    """Note response model."""
    id: int
    title: str
    content: str
    tags: List[str] = []
    is_pinned: bool = False
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
