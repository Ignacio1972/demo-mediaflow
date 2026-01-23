"""
Shortcuts Public API Endpoints
Returns active shortcuts for mobile page
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.shortcut import Shortcut
from app.models.audio import AudioMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_shortcut_public(shortcut: Shortcut) -> dict:
    """Serialize shortcut for public mobile page"""
    audio = shortcut.audio_message
    return {
        "id": shortcut.id,
        "audio_message_id": shortcut.audio_message_id,
        "custom_name": shortcut.custom_name,
        "custom_icon": shortcut.custom_icon,
        "custom_color": shortcut.custom_color,
        "position": shortcut.position,
        "audio_url": f"{settings.API_URL}/api/v1/library/{audio.id}/stream" if audio else None,
        "duration": audio.duration if audio else None,
    }


@router.get(
    "",
    summary="Get Active Shortcuts",
    description="Get shortcuts that have a position assigned (1-6) for mobile display",
)
async def get_active_shortcuts(
    db: AsyncSession = Depends(get_db),
):
    """Get only shortcuts with assigned positions (max 6) for mobile page"""
    try:
        logger.info("📱 Fetching active shortcuts for mobile")

        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(
                and_(
                    Shortcut.position.isnot(None),
                    Shortcut.active == True
                )
            )
            .order_by(Shortcut.position.asc())
        )
        shortcuts = result.scalars().all()

        logger.info(f"✅ Retrieved {len(shortcuts)} active shortcuts")

        return [serialize_shortcut_public(s) for s in shortcuts]

    except Exception as e:
        logger.error(f"❌ Failed to fetch shortcuts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shortcuts: {str(e)}",
        )


@router.get(
    "/{shortcut_id}",
    summary="Get Single Shortcut",
    description="Get a single active shortcut by ID",
)
async def get_shortcut(
    shortcut_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single shortcut for playback"""
    try:
        result = await db.execute(
            select(Shortcut)
            .options(selectinload(Shortcut.audio_message))
            .filter(
                and_(
                    Shortcut.id == shortcut_id,
                    Shortcut.active == True
                )
            )
        )
        shortcut = result.scalar_one_or_none()

        if not shortcut:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shortcut with ID {shortcut_id} not found or inactive",
            )

        return serialize_shortcut_public(shortcut)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch shortcut: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shortcut: {str(e)}",
        )
