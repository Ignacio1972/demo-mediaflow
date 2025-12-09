"""
AI Clients Settings API Endpoints
Handles AI client/context management - v2.1 Playground
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.ai_client import (
    AIClientCreate,
    AIClientUpdate,
    AIClientReorderRequest,
    AIClientListResponse,
)
from app.services.ai.client_manager import ai_client_manager
from app.api.v1.serializers import serialize_ai_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/ai-clients",
    response_model=AIClientListResponse,
    summary="Get All AI Clients",
    description="Get all AI client configurations with active client info",
)
async def get_all_clients(
    db: AsyncSession = Depends(get_db),
):
    """Get all AI clients for AI Client Manager"""
    try:
        logger.info("📋 Fetching all AI clients")

        clients = await ai_client_manager.list_clients(db, active_only=False)
        active_id = await ai_client_manager.get_active_client_id(db)

        logger.info(f"✅ Retrieved {len(clients)} AI clients")

        return AIClientListResponse(
            clients=[serialize_ai_client(c) for c in clients],
            active_client_id=active_id,
            total=len(clients)
        )

    except Exception as e:
        logger.error(f"❌ Failed to fetch AI clients: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI clients: {str(e)}",
        )


@router.get(
    "/ai-clients/active",
    summary="Get Active AI Client",
    description="Get the currently active AI client",
)
async def get_active_client(
    db: AsyncSession = Depends(get_db),
):
    """Get the active (default) AI client"""
    try:
        logger.info("📋 Fetching active AI client")

        client = await ai_client_manager.get_active_client(db)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay cliente IA activo configurado",
            )

        return serialize_ai_client(client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch active client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active client: {str(e)}",
        )


@router.get(
    "/ai-clients/{client_id}",
    summary="Get Single AI Client",
    description="Get a single AI client configuration by ID",
)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single AI client by ID"""
    try:
        client = await ai_client_manager.get_client(db, client_id)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI Client '{client_id}' not found",
            )

        return serialize_ai_client(client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch AI client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI client: {str(e)}",
        )


@router.post(
    "/ai-clients",
    status_code=status.HTTP_201_CREATED,
    summary="Create AI Client",
    description="Create a new AI client configuration",
)
async def create_client(
    data: AIClientCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new AI client"""
    try:
        logger.info(f"➕ Creating AI client: {data.name}")

        # Check if ID already exists (if provided)
        if data.id:
            existing = await ai_client_manager.get_client(db, data.id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"AI Client with ID '{data.id}' already exists",
                )

        client = await ai_client_manager.create_client(db, data)

        logger.info(f"✅ AI client created: {client.id}")
        return serialize_ai_client(client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create AI client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI client: {str(e)}",
        )


@router.patch(
    "/ai-clients/{client_id}",
    summary="Update AI Client",
    description="Update an existing AI client configuration",
)
async def update_client(
    client_id: str,
    data: AIClientUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing AI client"""
    try:
        logger.info(f"📝 Updating AI client: {client_id}")

        client = await ai_client_manager.update_client(db, client_id, data)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI Client '{client_id}' not found",
            )

        logger.info(f"✅ AI client updated: {client_id}")
        return serialize_ai_client(client)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update AI client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI client: {str(e)}",
        )


@router.delete(
    "/ai-clients/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete AI Client",
    description="Delete an AI client configuration",
)
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete an AI client"""
    try:
        logger.info(f"🗑️ Deleting AI client: {client_id}")

        success, error = await ai_client_manager.delete_client(db, client_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        logger.info(f"✅ AI client deleted: {client_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete AI client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete AI client: {str(e)}",
        )


@router.post(
    "/ai-clients/active/{client_id}",
    summary="Set Active AI Client",
    description="Set an AI client as the active (default) one",
)
async def set_active_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Set a client as the active (default) one"""
    try:
        logger.info(f"⭐ Setting active AI client: {client_id}")

        success = await ai_client_manager.set_active_client(db, client_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI Client '{client_id}' not found",
            )

        return {"success": True, "active_client_id": client_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set active client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set active client: {str(e)}",
        )


@router.put(
    "/ai-clients/reorder",
    summary="Reorder AI Clients",
    description="Reorder AI clients by providing a new order of IDs",
)
async def reorder_clients(
    request: AIClientReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder AI clients"""
    try:
        logger.info(f"🔄 Reordering AI clients: {request.client_ids}")

        await ai_client_manager.reorder_clients(db, request.client_ids)

        return {"success": True, "message": "Clients reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder AI clients: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder AI clients: {str(e)}",
        )
