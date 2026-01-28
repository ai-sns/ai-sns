# -*- coding: utf-8 -*-
"""
KM module - API router
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from .schemas import KMConfig, KMResponse
from .service import KMService
from .dependencies import get_km_service
from .note_router import router as note_router

logger = logging.getLogger(__name__)

router = APIRouter()

# 包含笔记路由
router.include_router(note_router, tags=["notes"])


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


# File management endpoints
@router.get("/{kb_id}/files", response_model=dict)
async def get_files(kb_id: int, service: KMService = Depends(get_km_service)):
    """Get all files for a knowledge base"""
    try:
        files = service.get_files(kb_id)
        return {"success": True, "data": files}
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/files", response_model=dict)
async def upload_file(
    kb_id: int,
    file: UploadFile = File(...),
    service: KMService = Depends(get_km_service)
):
    """Upload a file to knowledge base"""
    try:
        content = await file.read()
        file_id = service.add_file(kb_id, file.filename, content)
        return {"success": True, "data": {"id": file_id, "filename": file.filename}}
    except ValueError as e:
        logger.warning(f"Invalid upload for kb {kb_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}/files/{file_id}", response_model=dict)
async def delete_file(
    kb_id: int,
    file_id: int,
    service: KMService = Depends(get_km_service)
):
    """Delete a file from knowledge base"""
    try:
        service.delete_file(kb_id, file_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/upload-image", response_model=dict)
async def upload_image(
    kb_id: int,
    file: UploadFile = File(...),
    service: KMService = Depends(get_km_service)
):
    """Upload an image for knowledge base notes"""
    try:
        content = await file.read()

        # Check if file is an image
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")

        # Get file extension
        import os
        filename = file.filename
        file_ext = os.path.splitext(filename)[1].lower()

        # Allowed image extensions
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Only {', '.join(allowed_extensions)} files are allowed"
            )

        # Generate unique filename
        import uuid
        import time
        unique_name = f"{int(time.time())}_{uuid.uuid4().hex[:8]}{file_ext}"

        # Create images directory for this kb in uploads folder
        from pathlib import Path
        images_dir = Path(f"uploads/km/images/{kb_id}")
        images_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        image_path = images_dir / unique_name
        image_path.write_bytes(content)

        # Return image URL with full HTTP path
        image_url = f"http://localhost:8788/uploads/km/images/{kb_id}/{unique_name}"
        logger.info(f"Image uploaded: {image_url}")

        return {
            "success": True,
            "data": {
                "url": image_url,
                "filename": unique_name,
                "original_name": filename
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/search", response_model=dict)
async def vector_search(
    kb_id: int,
    request: dict,
    service: KMService = Depends(get_km_service)
):
    """Perform vector search in knowledge base"""
    try:
        query = request.get("query", "")
        top_k = request.get("top_k", 5)
        results = service.vector_search(kb_id, query, top_k)
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Key-value management endpoints
@router.get("/{kb_id}/keyvalues", response_model=dict)
async def get_key_values(kb_id: int, service: KMService = Depends(get_km_service)):
    """Get all key-value pairs for a knowledge base"""
    try:
        kvs = service.get_key_values(kb_id)
        return {"success": True, "data": kvs}
    except Exception as e:
        logger.error(f"Error getting key-values: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/keyvalues", response_model=dict)
async def create_key_value(
    kb_id: int,
    request: dict,
    service: KMService = Depends(get_km_service)
):
    """Create a new key-value pair"""
    try:
        key = request.get("key")
        value = request.get("value")
        kv_id = service.add_key_value(kb_id, key, value)
        return {"success": True, "data": {"id": kv_id, "key": key, "value": value}}
    except Exception as e:
        logger.error(f"Error creating key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{kb_id}/keyvalues/{kv_id}", response_model=dict)
async def update_key_value(
    kb_id: int,
    kv_id: int,
    request: dict,
    service: KMService = Depends(get_km_service)
):
    """Update a key-value pair"""
    try:
        key = request.get("key")
        value = request.get("value")
        service.update_key_value(kb_id, kv_id, key, value)
        return {"success": True, "data": {"id": kv_id, "key": key, "value": value}}
    except Exception as e:
        logger.error(f"Error updating key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}/keyvalues/{kv_id}", response_model=dict)
async def delete_key_value(
    kb_id: int,
    kv_id: int,
    service: KMService = Depends(get_km_service)
):
    """Delete a key-value pair"""
    try:
        service.delete_key_value(kb_id, kv_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting key-value: {e}")
        raise HTTPException(status_code=500, detail=str(e))
