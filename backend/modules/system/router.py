# -*- coding: utf-8 -*-
"""
System module - API router
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List

from .schemas import SystemConfig, WebMngReorderItem
from .service import SystemService
from .dependencies import get_system_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config", response_model=dict)
async def get_system_config(service: SystemService = Depends(get_system_service)):
    """
    Get system configuration

    Returns:
        System configuration
    """
    try:
        config = service.get_system_config()
        return {"success": True, "data": config}
    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config", response_model=dict)
async def update_system_config(
    config: SystemConfig,
    service: SystemService = Depends(get_system_service)
):
    """
    Update system configuration

    Args:
        config: Updated system configuration

    Returns:
        Success status
    """
    try:
        service.update_system_config(**config.dict(exclude_unset=True))
        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/web-mng", response_model=dict)
async def get_web_mng(service: SystemService = Depends(get_system_service)):
    """
    Get web management data (LLM and Tools)

    Returns:
        List of web management items
    """
    try:
        data = service.get_web_mng()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error getting web-mng data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/web-mng", response_model=dict)
async def create_web_mng(
    item: dict,
    service: SystemService = Depends(get_system_service)
):
    """
    Create new web management item

    Args:
        item: Web management item data

    Returns:
        Created item
    """
    try:
        result = service.create_web_mng(item)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error creating web-mng item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/web-mng/reorder", response_model=dict)
async def reorder_web_mng(
    request: Request,
    service: SystemService = Depends(get_system_service)
):
    """
    Reorder web management items
    
    IMPORTANT: This route must be defined BEFORE /web-mng/{item_id}
    to avoid FastAPI matching 'reorder' as an item_id

    Args:
        request: Request body containing list of items with id and position

    Returns:
        Success status
    """
    try:
        items = await request.json()
        logger.info(f"Received reorder request: {items}")
        logger.info(f"Items type: {type(items)}")
        
        # Validate items
        if not isinstance(items, list):
            error_msg = f"Expected a list of items, got {type(items).__name__}"
            logger.error(error_msg)
            raise HTTPException(status_code=422, detail=error_msg)
        
        if len(items) == 0:
            logger.warning("Empty items list received")
            return {"success": True}
        
        for idx, item in enumerate(items):
            logger.info(f"Item {idx}: {item} (type: {type(item).__name__})")
            if not isinstance(item, dict):
                error_msg = f"Item {idx} is not a dict, got {type(item).__name__}"
                logger.error(error_msg)
                raise HTTPException(status_code=422, detail=error_msg)
            if 'id' not in item:
                error_msg = f"Item {idx} missing 'id' field. Keys: {list(item.keys())}"
                logger.error(error_msg)
                raise HTTPException(status_code=422, detail=error_msg)
            if 'position' not in item:
                error_msg = f"Item {idx} missing 'position' field. Keys: {list(item.keys())}"
                logger.error(error_msg)
                raise HTTPException(status_code=422, detail=error_msg)
        
        service.reorder_web_mng(items)
        logger.info("Reorder completed successfully")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering web-mng items: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/web-mng/{item_id}", response_model=dict)
async def update_web_mng(
    item_id: int,
    item: dict,
    service: SystemService = Depends(get_system_service)
):
    """
    Update web management item

    Args:
        item_id: Item ID
        item: Updated item data

    Returns:
        Updated item
    """
    try:
        result = service.update_web_mng(item_id, item)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error updating web-mng item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/web-mng/{item_id}", response_model=dict)
async def delete_web_mng(
    item_id: int,
    service: SystemService = Depends(get_system_service)
):
    """
    Delete web management item (soft delete)

    Args:
        item_id: Item ID

    Returns:
        Success status
    """
    try:
        service.delete_web_mng(item_id)
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting web-mng item: {e}")
        raise HTTPException(status_code=500, detail=str(e))