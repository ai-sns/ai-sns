# -*- coding: utf-8 -*-
"""
KM module - API router
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from .schemas import KMConfig, KMResponse
from .service import KMService
from .dependencies import get_km_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=dict)
async def get_knowledge_bases(service: KMService = Depends(get_km_service)):
    """
    Get all knowledge bases

    Returns:
        List of knowledge base configurations
    """
    try:
        kbs = service.get_all_knowledge_bases()
        return {"success": True, "data": kbs}
    except Exception as e:
        logger.error(f"Error getting knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict)
async def create_knowledge_base(
    config: KMConfig,
    service: KMService = Depends(get_km_service)
):
    """
    Create a new knowledge base

    Args:
        config: Knowledge base configuration

    Returns:
        Created knowledge base ID
    """
    try:
        kb_id = service.create_knowledge_base(**config.dict(exclude_unset=True))
        return {"success": True, "data": {"id": kb_id}}
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{kb_id}", response_model=dict)
async def update_knowledge_base(
    kb_id: int,
    config: KMConfig,
    service: KMService = Depends(get_km_service)
):
    """
    Update knowledge base configuration

    Args:
        kb_id: Knowledge base ID
        config: Updated knowledge base configuration

    Returns:
        Success status
    """
    try:
        service.update_knowledge_base(kb_id, **config.dict(exclude_unset=True))
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}", response_model=dict)
async def delete_knowledge_base(
    kb_id: int,
    service: KMService = Depends(get_km_service)
):
    """
    Delete a knowledge base

    Args:
        kb_id: Knowledge base ID

    Returns:
        Success status
    """
    try:
        service.delete_knowledge_base(kb_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/upload", response_model=dict)
async def upload_to_knowledge_base(
    kb_id: int,
    file: UploadFile = File(...),
    service: KMService = Depends(get_km_service)
):
    """
    Upload file to knowledge base

    Args:
        kb_id: Knowledge base ID
        file: File to upload

    Returns:
        File upload information
    """
    try:
        content = await file.read()
        file_path = service.save_uploaded_file(kb_id, file.filename, content)

        # TODO: Process file and add to vector database

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "path": str(file_path)
            }
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
