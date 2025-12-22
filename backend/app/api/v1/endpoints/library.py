"""
Library API Endpoints
Handles audio message library with filtering, pagination, and favorites - v2.1
"""
import os
import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from pydub import AudioSegment

from app.db.session import get_db
from app.models.audio import AudioMessage
from app.models.category import Category
from app.core.config import settings

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

        # Build base query - ALWAYS filter by is_favorite=True (only show saved messages)
        query = select(AudioMessage).filter(AudioMessage.is_favorite == True)

        # Apply additional filters
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

        # Note: is_favorite parameter is kept for API compatibility but ignored
        # Library always shows only saved messages (is_favorite=True)

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

        # Return complete message object (same structure as GET)
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


# Allowed audio formats for upload
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/flac": "flac",
    "audio/aac": "aac",
    "audio/ogg": "ogg",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/opus": "opus",
}

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB


@router.post(
    "/upload",
    summary="Upload External Audio",
    description="Upload an external audio file (MP3, WAV, FLAC, AAC, OGG, M4A) to the library",
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio(
    audio: UploadFile = File(..., description="Audio file to upload"),
    display_name: Optional[str] = Form(None, description="Optional display name"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an external audio file to the library.

    - Validates format (MP3, WAV, FLAC, AAC, OGG, M4A, Opus)
    - Validates size (max 50MB)
    - Extracts metadata (duration, size) using pydub
    - Creates AudioMessage record with voice_id=null
    """
    try:
        logger.info(f"📤 Upload request: {audio.filename}, content_type={audio.content_type}")

        # Validate content type
        content_type = audio.content_type
        if content_type not in ALLOWED_AUDIO_TYPES:
            logger.warning(f"⚠️ Invalid audio format: {content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato no permitido. Use: MP3, WAV, FLAC, AAC, OGG, M4A, Opus",
            )

        # Read file content
        file_content = await audio.read()
        file_size = len(file_content)

        # Validate size
        if file_size > MAX_UPLOAD_SIZE:
            logger.warning(f"⚠️ File too large: {file_size} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo excede el límite de 50MB (tamaño: {file_size / 1024 / 1024:.1f}MB)",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío",
            )

        # Generate unique filename
        ext = ALLOWED_AUDIO_TYPES[content_type]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"upload_{timestamp}_{unique_id}.{ext}"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"💾 File saved: {filename}")

        # Extract audio metadata using pydub
        try:
            audio_segment = AudioSegment.from_file(file_path)
            duration = len(audio_segment) / 1000.0  # milliseconds to seconds
        except Exception as e:
            # If pydub fails, still save but without duration
            logger.warning(f"⚠️ Could not extract audio metadata: {e}")
            duration = None

        # Determine display name
        if not display_name:
            # Use original filename without extension
            original_name = audio.filename or "Audio subido"
            display_name = os.path.splitext(original_name)[0][:100]

        # Create database record
        audio_message = AudioMessage(
            filename=filename,
            display_name=display_name,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            format=ext,
            original_text="[Audio subido]",  # Marker for uploaded files
            voice_id="uploaded",  # Special marker for uploaded files
            status="ready",
            priority=4,
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"✅ Audio uploaded: ID={audio_message.id}, filename={filename}")

        return {
            "success": True,
            "data": {
                "id": audio_message.id,
                "filename": audio_message.filename,
                "display_name": audio_message.display_name,
                "file_size": audio_message.file_size,
                "duration": audio_message.duration,
                "format": audio_message.format,
                "original_text": audio_message.original_text,
                "voice_id": audio_message.voice_id,
                "category_id": audio_message.category_id,
                "is_favorite": audio_message.is_favorite,
                "status": audio_message.status,
                "created_at": audio_message.created_at.isoformat() if audio_message.created_at else None,
                "audio_url": f"/storage/audio/{audio_message.filename}",
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}", exc_info=True)
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.post(
    "/{message_id}/send-to-radio",
    summary="Send Audio to Radio",
    description="Send audio for immediate playback on radio/player",
)
async def send_to_radio(
    message_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Send an audio message to the radio for immediate playback.

    This marks the message as sent to the player and records the delivery time.
    The actual integration with AzuraCast/player is for future implementation.
    """
    try:
        logger.info(f"📻 Send to radio request: ID={message_id}")

        # Find the audio message
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()

        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found",
            )

        if msg.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send deleted message to radio",
            )

        # Mark as sent to player
        msg.sent_to_player = True
        msg.delivered_at = datetime.utcnow()

        await db.commit()
        await db.refresh(msg)

        logger.info(f"✅ Audio sent to radio: {msg.filename}")

        return {
            "success": True,
            "message": "Audio enviado a la radio",
            "data": {
                "id": msg.id,
                "filename": msg.filename,
                "display_name": msg.display_name,
                "sent_to_player": msg.sent_to_player,
                "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Send to radio failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Send to radio failed: {str(e)}",
        )
