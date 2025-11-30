"""
Library API Endpoints
Handles audio message library with filtering, pagination, and favorites - v2.1
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.models.audio import AudioMessage
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    summary="Get Library Messages",
    description="Get paginated list of audio messages with optional filters",
)
async def get_library_messages(
    search: Optional[str] = Query(None, description="Search in display_name and original_text"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get library messages with filtering and pagination.

    Supports:
    - Text search in display_name and original_text
    - Category filter
    - Favorite filter
    - Sorting by any field
    - Pagination
    """
    try:
        logger.info(f"📚 Library request: page={page}, per_page={per_page}, search={search}")

        # Build base query
        query = select(AudioMessage)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    AudioMessage.display_name.ilike(search_term),
                    AudioMessage.original_text.ilike(search_term)
                )
            )

        if category_id:
            query = query.filter(AudioMessage.category_id == category_id)

        if is_favorite is not None:
            query = query.filter(AudioMessage.is_favorite == is_favorite)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(AudioMessage, sort_by, AudioMessage.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        messages = result.scalars().all()

        logger.info(f"✅ Retrieved {len(messages)} messages (total: {total})")

        return {
            "messages": [
                {
                    "id": msg.id,
                    "filename": msg.filename,
                    "display_name": msg.display_name,
                    "file_path": msg.file_path,
                    "file_size": msg.file_size,
                    "duration": msg.duration,
                    "format": msg.format,
                    "original_text": msg.original_text,
                    "voice_id": msg.voice_id,
                    "category_id": msg.category_id,
                    "is_favorite": msg.is_favorite,
                    "volume_adjustment": msg.volume_adjustment,
                    "has_jingle": msg.has_jingle,
                    "music_file": msg.music_file,
                    "status": msg.status,
                    "sent_to_player": msg.sent_to_player,
                    "priority": msg.priority,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "updated_at": msg.updated_at.isoformat() if msg.updated_at else None,
                    "audio_url": f"/storage/audio/{msg.filename}",
                }
                for msg in messages
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch library: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch library: {str(e)}",
        )


@router.get(
    "/{message_id}",
    summary="Get Single Message",
    description="Get a single audio message by ID",
)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single audio message by ID"""
    try:
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()

        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found",
            )

        return {
            "id": msg.id,
            "filename": msg.filename,
            "display_name": msg.display_name,
            "file_path": msg.file_path,
            "file_size": msg.file_size,
            "duration": msg.duration,
            "format": msg.format,
            "original_text": msg.original_text,
            "voice_id": msg.voice_id,
            "category_id": msg.category_id,
            "is_favorite": msg.is_favorite,
            "volume_adjustment": msg.volume_adjustment,
            "has_jingle": msg.has_jingle,
            "music_file": msg.music_file,
            "status": msg.status,
            "sent_to_player": msg.sent_to_player,
            "priority": msg.priority,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "updated_at": msg.updated_at.isoformat() if msg.updated_at else None,
            "audio_url": f"/storage/audio/{msg.filename}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch message: {str(e)}",
        )


@router.patch(
    "/{message_id}",
    summary="Update Message",
    description="Update message fields (display_name, category_id, is_favorite)",
)
async def update_message(
    message_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update a message's editable fields"""
    try:
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()

        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found",
            )

        # Update allowed fields
        allowed_fields = ["display_name", "category_id", "is_favorite"]
        for field in allowed_fields:
            if field in data:
                setattr(msg, field, data[field])

        await db.commit()
        await db.refresh(msg)

        logger.info(f"✅ Updated message {message_id}")

        return {
            "id": msg.id,
            "filename": msg.filename,
            "display_name": msg.display_name,
            "category_id": msg.category_id,
            "is_favorite": msg.is_favorite,
            "updated_at": msg.updated_at.isoformat() if msg.updated_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update message: {str(e)}",
        )


@router.delete(
    "/{message_id}",
    summary="Delete Message",
    description="Soft delete a message",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a message (sets status to 'deleted')"""
    try:
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()

        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found",
            )

        # Soft delete by setting status
        msg.status = "deleted"
        await db.commit()

        logger.info(f"✅ Deleted message {message_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}",
        )


@router.post(
    "/batch-delete",
    summary="Batch Delete Messages",
    description="Delete multiple messages at once",
)
async def batch_delete_messages(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple messages by IDs"""
    try:
        ids = data.get("ids", [])
        if not ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No IDs provided",
            )

        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id.in_(ids))
        )
        messages = result.scalars().all()

        deleted_count = 0
        for msg in messages:
            msg.status = "deleted"
            deleted_count += 1

        await db.commit()

        logger.info(f"✅ Batch deleted {deleted_count} messages")

        return {"deleted_count": deleted_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to batch delete: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to batch delete: {str(e)}",
        )
