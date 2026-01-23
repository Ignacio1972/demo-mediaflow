"""
Shortcuts Settings API Endpoints
Handles shortcut management for quick audio playback
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.shortcut import Shortcut
from app.models.audio import AudioMessage
from app.core.config import settings
from app.schemas.shortcut import (
    ShortcutCreate,
    ShortcutUpdate,
    ShortcutResponse,
    ShortcutPositionUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_shortcut(shortcut: Shortcut, include_audio: bool = True) -> dict:
    """Serialize shortcut model to response dict"""
    data = {
        "id": shortcut.id,
        "audio_message_id": shortcut.audio_message_id,
        "custom_name": shortcut.custom_name,
        "custom_icon": shortcut.custom_icon,
        "custom_color": shortcut.custom_color,
        "position": shortcut.position,
        "active": shortcut.active,
        "created_at": shortcut.created_at.isoformat() if shortcut.created_at else None,
        "updated_at": shortcut.updated_at.isoformat() if shortcut.updated_at else None,
    }

    if include_audio and shortcut.audio_message:
        audio = shortcut.audio_message
        data["audio_message"] = {
            "id": audio.id,
            "filename": audio.filename,
            "display_name": audio.display_name,
            "duration": audio.duration,
            "audio_url": f"{settings.API_URL}/api/v1/library/{audio.id}/stream",
        }

    return data


@router.get(
    "/shortcuts",
    summary="Get All Shortcuts",
    description="Get all shortcuts with their linked audio messages",
)
async def get_all_shortcuts(
    db: AsyncSession = Depends(get_db),
):
    """Get all shortcuts for Shortcut Manager"""
    try:
        logger.info("📋 Fetching all shortcuts")

        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .order_by(Shortcut.position.asc().nullslast(), Shortcut.id.asc())
        )
        shortcuts = result.scalars().all()

        logger.info(f"✅ Retrieved {len(shortcuts)} shortcuts")

        return [serialize_shortcut(s) for s in shortcuts]

    except Exception as e:
        logger.error(f"❌ Failed to fetch shortcuts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shortcuts: {str(e)}",
        )


@router.get(
    "/shortcuts/{shortcut_id}",
    summary="Get Single Shortcut",
    description="Get a single shortcut by ID",
)
async def get_shortcut(
    shortcut_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get single shortcut by ID"""
    try:
        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one_or_none()

        if not shortcut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shortcut with ID {shortcut_id} not found",
            )

        return serialize_shortcut(shortcut)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch shortcut: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shortcut: {str(e)}",
        )


@router.post(
    "/shortcuts",
    status_code=status.HTTP_201_CREATED,
    summary="Create Shortcut",
    description="Create a new shortcut from an audio message",
)
async def create_shortcut(
    shortcut_data: ShortcutCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new shortcut"""
    try:
        logger.info(f"➕ Creating shortcut for audio {shortcut_data.audio_message_id}")

        # Verify audio message exists
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == shortcut_data.audio_message_id)
        )
        audio = result.scalar_one_or_none()

        if not audio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio message with ID {shortcut_data.audio_message_id} not found",
            )

        # Check if shortcut already exists for this audio
        result = await db.execute(
            select(Shortcut).filter(Shortcut.audio_message_id == shortcut_data.audio_message_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shortcut already exists for audio message {shortcut_data.audio_message_id}",
            )

        # If position is specified, clear it from any existing shortcut
        if shortcut_data.position:
            await _clear_position(db, shortcut_data.position)

        # Create shortcut
        shortcut = Shortcut(
            audio_message_id=shortcut_data.audio_message_id,
            custom_name=shortcut_data.custom_name,
            custom_icon=shortcut_data.custom_icon,
            custom_color=shortcut_data.custom_color,
            position=shortcut_data.position,
            active=True,
        )

        db.add(shortcut)
        await db.commit()

        # Reload with audio_message relationship
        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(Shortcut.id == shortcut.id)
        )
        shortcut = result.scalar_one()

        logger.info(f"✅ Shortcut created: {shortcut.id}")

        return serialize_shortcut(shortcut)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create shortcut: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create shortcut: {str(e)}",
        )


@router.patch(
    "/shortcuts/{shortcut_id}",
    summary="Update Shortcut",
    description="Update shortcut settings (name, icon, color, position)",
)
async def update_shortcut(
    shortcut_id: int,
    shortcut_data: ShortcutUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing shortcut"""
    try:
        logger.info(f"📝 Updating shortcut {shortcut_id}")

        result = await db.execute(
            select(Shortcut).filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one_or_none()

        if not shortcut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shortcut with ID {shortcut_id} not found",
            )

        # If position is being changed, clear it from any existing shortcut
        if shortcut_data.position is not None and shortcut_data.position != shortcut.position:
            if shortcut_data.position:  # Only clear if setting a new position (not clearing to null)
                await _clear_position(db, shortcut_data.position, exclude_id=shortcut_id)

        # Update fields
        update_data = shortcut_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shortcut, field, value)

        await db.commit()

        # Reload with audio_message relationship
        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one()

        logger.info(f"✅ Shortcut updated: {shortcut.id}")

        return serialize_shortcut(shortcut)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update shortcut: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update shortcut: {str(e)}",
        )


@router.patch(
    "/shortcuts/{shortcut_id}/position",
    summary="Update Shortcut Position",
    description="Assign or remove shortcut position (1-6)",
)
async def update_shortcut_position(
    shortcut_id: int,
    position_data: ShortcutPositionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Assign shortcut to a slot (1-6) or remove from grid (null)"""
    try:
        logger.info(f"🔢 Setting shortcut {shortcut_id} to position {position_data.position}")

        result = await db.execute(
            select(Shortcut).filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one_or_none()

        if not shortcut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shortcut with ID {shortcut_id} not found",
            )

        # Clear position from any existing shortcut if setting a new position
        if position_data.position:
            await _clear_position(db, position_data.position, exclude_id=shortcut_id)

        shortcut.position = position_data.position
        await db.commit()

        # Reload with audio_message relationship
        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one()

        logger.info(f"✅ Shortcut position updated: {shortcut.id} -> {shortcut.position}")

        return serialize_shortcut(shortcut)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update position: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update position: {str(e)}",
        )


@router.delete(
    "/shortcuts/{shortcut_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Shortcut",
    description="Delete a shortcut (does not delete the audio message)",
)
async def delete_shortcut(
    shortcut_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a shortcut"""
    try:
        logger.info(f"🗑️ Deleting shortcut {shortcut_id}")

        result = await db.execute(
            select(Shortcut).filter(Shortcut.id == shortcut_id)
        )
        shortcut = result.scalar_one_or_none()

        if not shortcut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shortcut with ID {shortcut_id} not found",
            )

        await db.delete(shortcut)
        await db.commit()

        logger.info(f"✅ Shortcut deleted: {shortcut_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete shortcut: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete shortcut: {str(e)}",
        )


async def _clear_position(db: AsyncSession, position: int, exclude_id: Optional[int] = None):
    """Clear a position from any shortcut that currently has it"""
    query = select(Shortcut).filter(Shortcut.position == position)
    if exclude_id:
        query = query.filter(Shortcut.id != exclude_id)

    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.position = None
        logger.info(f"🔄 Cleared position {position} from shortcut {existing.id}")
