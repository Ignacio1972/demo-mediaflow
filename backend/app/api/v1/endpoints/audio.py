"""
Audio API Endpoints
Handles TTS generation with automatic voice settings - v2.1
"""
import os
import asyncio
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.schemas.audio import (
    AudioGenerateRequest,
    AudioGenerateResponse,
    VoiceResponse,
    ErrorResponse,
)
from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.models.shortcut import Shortcut
from app.services.audio.generator import (
    generate_audio as generate_audio_core,
    VoiceNotFoundError,
    VoiceInactiveError,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Maximum number of temporary (unsaved) messages to keep
MAX_RECENT_MESSAGES = 50


async def cleanup_old_temporary_messages(db: AsyncSession) -> int:
    """
    Delete old temporary messages (is_favorite=False) when limit is exceeded.

    Keeps only the MAX_RECENT_MESSAGES most recent temporary messages.
    Deletes both database records and physical audio files.

    Returns:
        Number of messages deleted
    """
    try:
        # Count temporary messages
        count_query = select(func.count()).where(AudioMessage.is_favorite == False)
        result = await db.execute(count_query)
        total_temp = result.scalar() or 0

        if total_temp <= MAX_RECENT_MESSAGES:
            return 0  # No cleanup needed

        # Calculate how many to delete
        to_delete_count = total_temp - MAX_RECENT_MESSAGES

        logger.info(
            f"🧹 Cleanup: {total_temp} temporary messages found, "
            f"deleting {to_delete_count} oldest"
        )

        # Get IDs of messages used by shortcuts (cannot delete these)
        shortcut_query = select(Shortcut.audio_message_id).where(Shortcut.audio_message_id.isnot(None))
        shortcut_result = await db.execute(shortcut_query)
        shortcut_audio_ids = {row[0] for row in shortcut_result.fetchall()}

        # Get oldest temporary messages to delete (excluding those used by shortcuts)
        query = (
            select(AudioMessage)
            .where(AudioMessage.is_favorite == False)
            .where(AudioMessage.id.notin_(shortcut_audio_ids) if shortcut_audio_ids else True)
            .order_by(AudioMessage.created_at.asc())
            .limit(to_delete_count)
        )
        result = await db.execute(query)
        messages_to_delete = result.scalars().all()

        deleted_count = 0
        for msg in messages_to_delete:
            # Delete physical audio file if it exists
            if msg.file_path and os.path.exists(msg.file_path):
                try:
                    os.remove(msg.file_path)
                    logger.debug(f"🗑️ Deleted file: {msg.file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete file {msg.file_path}: {e}")

            # Delete from database
            await db.delete(msg)
            deleted_count += 1

        await db.commit()

        logger.info(f"✅ Cleanup completed: {deleted_count} messages deleted")
        return deleted_count

    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}", exc_info=True)
        await db.rollback()
        return 0


@router.post(
    "/generate",
    response_model=AudioGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate TTS Audio",
    description="Generate audio from text using automatic voice settings (v2.1)",
    responses={
        201: {"description": "Audio generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Voice not found"},
        500: {"model": ErrorResponse, "description": "Generation failed"},
    },
)
async def generate_audio(
    request: AudioGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate TTS audio with automatic voice settings application

    This endpoint:
    1. Gets voice configuration with predefined settings
    2. Generates TTS using ElevenLabs with those settings
    3. Applies volume adjustment if configured
    4. Saves to storage and database
    5. Returns audio URL and metadata

    NO manual voice settings needed - everything is automatic!
    """
    try:
        # Prepare settings override if provided
        settings_override = None
        if request.voice_settings:
            settings_override = {}
            if request.voice_settings.style is not None:
                settings_override["style"] = request.voice_settings.style
            if request.voice_settings.stability is not None:
                settings_override["stability"] = request.voice_settings.stability
            if request.voice_settings.similarity_boost is not None:
                settings_override["similarity_boost"] = request.voice_settings.similarity_boost
            if request.voice_settings.speed is not None:
                settings_override["speed"] = request.voice_settings.speed
            if request.voice_settings.volume_adjustment is not None:
                settings_override["volume_adjustment"] = request.voice_settings.volume_adjustment

            if settings_override:
                logger.info(f"🎛️ Voice settings override provided: {settings_override}")

        # Delegate to shared generator
        audio_message = await generate_audio_core(
            text=request.text,
            voice_id=request.voice_id,
            db=db,
            add_jingles=request.add_jingles,
            music_file=request.music_file,
            priority=request.priority,
            category_id=request.category_id,
            settings_override=settings_override,
            commit=True,
        )

        # Cleanup old temporary messages if limit exceeded
        deleted_count = await cleanup_old_temporary_messages(db)
        if deleted_count > 0:
            logger.info(f"🧹 Auto-cleanup: {deleted_count} old temporary messages deleted")

        # Build response from AudioMessage
        audio_url = f"/storage/audio/{audio_message.filename}"
        snapshot = json.loads(audio_message.voice_settings_snapshot)

        # Reconstruct effective settings_applied
        settings_applied = {
            "style": snapshot["style"],
            "stability": snapshot["stability"],
            "similarity_boost": snapshot["similarity_boost"],
            "speed": snapshot["speed"],
            "volume_adjustment": audio_message.volume_adjustment,
        }
        if settings_override:
            for key in settings_override:
                if key in settings_applied:
                    settings_applied[key] = settings_override[key]

        response = AudioGenerateResponse(
            audio_id=audio_message.id,
            filename=audio_message.filename,
            display_name=audio_message.display_name,
            audio_url=audio_url,
            file_size=audio_message.file_size,
            duration=audio_message.duration,
            status=audio_message.status,
            voice_id=audio_message.voice_id,
            voice_name=snapshot["voice_name"],
            settings_applied=settings_applied,
            created_at=audio_message.created_at,
        )

        logger.info(f"🎉 Audio generation completed successfully: {audio_message.filename}")
        return response

    except VoiceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice '{request.voice_id}' not found",
        )
    except VoiceInactiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Voice '{request.voice_id}' is inactive",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Audio generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio generation failed: {str(e)}",
        )


@router.get(
    "/voices",
    response_model=List[VoiceResponse],
    summary="Get Available Voices",
    description="Get all active voices with their settings",
)
async def get_voices(db: AsyncSession = Depends(get_db)):
    """
    Get all active voices ordered by priority

    Returns voice configurations with all settings that will be
    automatically applied during generation.
    """
    try:
        logger.info("📋 Fetching available voices")

        result = await db.execute(
            select(VoiceSettings)
            .filter(VoiceSettings.active == True)
            .order_by(VoiceSettings.order.asc())
        )
        voices = result.scalars().all()

        logger.info(f"✅ Retrieved {len(voices)} active voices")

        return [VoiceResponse.model_validate(voice) for voice in voices]

    except Exception as e:
        logger.error(f"❌ Failed to fetch voices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voices: {str(e)}",
        )


@router.get(
    "/voices/{voice_id}",
    response_model=VoiceResponse,
    summary="Get Voice Details",
    description="Get detailed information about a specific voice",
    responses={404: {"model": ErrorResponse, "description": "Voice not found"}},
)
async def get_voice(voice_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific voice"""
    try:
        logger.info(f"🔍 Fetching voice: {voice_id}")

        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            logger.warning(f"⚠️ Voice not found: {voice_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        logger.info(f"✅ Voice found: {voice.name}")
        return VoiceResponse.model_validate(voice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voice: {str(e)}",
        )


@router.get(
    "/recent",
    response_model=List[dict],
    summary="Get Recent Messages",
    description="Get recently generated messages for Dashboard display",
)
async def get_recent_messages(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent audio messages (for Dashboard display)

    Returns the most recent generated messages with basic info
    """
    try:
        logger.info(f"📋 Fetching {limit} recent messages")

        result = await db.execute(
            select(AudioMessage)
            .order_by(AudioMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        logger.info(f"✅ Retrieved {len(messages)} recent messages")

        return [
            {
                "id": msg.id,
                "filename": msg.filename,
                "display_name": msg.display_name,
                "original_text": msg.original_text,
                "voice_id": msg.voice_id,
                "category_id": msg.category_id,
                "duration": msg.duration,
                "is_favorite": msg.is_favorite,
                "created_at": msg.created_at.isoformat(),
                "audio_url": f"/storage/audio/{msg.filename}",
            }
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"❌ Failed to fetch recent messages: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent messages: {str(e)}",
        )


@router.patch(
    "/{audio_id}/save-to-library",
    summary="Save Audio to Library",
    description="Mark an audio message as saved/favorite for the Library",
    responses={
        200: {"description": "Audio saved to library successfully"},
        404: {"model": ErrorResponse, "description": "Audio not found"},
    },
)
async def save_to_library(
    audio_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Save an audio message to the library by marking it as favorite.

    This is used from the Dashboard after generating an audio to
    save it to the Library for later use.
    """
    try:
        logger.info(f"💾 Saving audio to library: ID={audio_id}")

        # Find the audio message
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == audio_id)
        )
        audio_message = result.scalar_one_or_none()

        if not audio_message:
            logger.warning(f"⚠️ Audio not found: {audio_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio message with ID {audio_id} not found",
            )

        # Mark as favorite (saved to library)
        audio_message.is_favorite = True
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"✅ Audio saved to library: {audio_message.filename}")

        return {
            "success": True,
            "message": "Audio guardado en biblioteca",
            "data": {
                "id": audio_message.id,
                "filename": audio_message.filename,
                "display_name": audio_message.display_name,
                "is_favorite": audio_message.is_favorite,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to save to library: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save to library: {str(e)}",
        )


@router.delete(
    "/{audio_id}",
    summary="Delete Audio Message",
    description="Delete an audio message from the recent messages list",
    responses={
        200: {"description": "Audio deleted successfully"},
        404: {"model": ErrorResponse, "description": "Audio not found"},
    },
)
async def delete_audio_message(
    audio_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an audio message and its associated file.

    This removes the message from both the database and filesystem.
    """
    try:
        logger.info(f"Deleting audio message: ID={audio_id}")

        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == audio_id)
        )
        audio_message = result.scalar_one_or_none()

        if not audio_message:
            logger.warning(f"Audio not found: {audio_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio message with ID {audio_id} not found",
            )

        filename = audio_message.filename
        file_path = audio_message.file_path

        # Delete physical file if exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {file_path}: {e}")

        # Delete from database
        await db.delete(audio_message)
        await db.commit()

        logger.info(f"Audio deleted: {filename}")

        return {
            "success": True,
            "message": "Audio eliminado",
            "data": {
                "id": audio_id,
                "filename": filename,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete audio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete audio: {str(e)}",
        )


# --- Audio Stream with Format Conversion ---

AUDIO_CACHE_DIR = os.path.join(settings.AUDIO_PATH, "cache")


async def convert_mp3_to_ogg(source_path: str, output_path: str) -> bool:
    """Convert MP3 to OGG/Opus using FFmpeg."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", source_path,
        "-map_metadata", "-1",
        "-c:a", "libopus",
        "-b:a", "128k",
        "-ar", "48000",
        "-ac", "1",
        output_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.error(f"FFmpeg conversion failed: {stderr.decode()}")
        return False
    return True


@router.get(
    "/stream/{filename}",
    summary="Stream Audio (with optional format conversion)",
    description="Serve an audio file, optionally converting to OGG/Opus for WhatsApp compatibility",
    responses={
        200: {"description": "Audio file"},
        404: {"description": "Audio file not found"},
    },
)
async def stream_audio(
    filename: str,
    format: Optional[str] = Query(None, description="Output format: 'ogg' for OGG/Opus conversion"),
):
    """
    Stream an audio file with optional format conversion.

    - Without ?format: serves the original file as-is.
    - With ?format=ogg: serves OGG/Opus version (converts and caches if needed).

    Used by OpenClaw to send WhatsApp-compatible voice notes.
    """
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    source_path = os.path.join(settings.AUDIO_PATH, safe_filename)

    if not os.path.isfile(source_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    # No conversion requested — serve original
    if format != "ogg":
        return FileResponse(source_path, media_type="audio/mpeg", filename=safe_filename)

    # Build cached OGG path
    ogg_filename = os.path.splitext(safe_filename)[0] + ".ogg"
    cached_path = os.path.join(AUDIO_CACHE_DIR, ogg_filename)

    # Serve from cache if it exists and is newer than source
    if os.path.isfile(cached_path):
        source_mtime = os.path.getmtime(source_path)
        cache_mtime = os.path.getmtime(cached_path)
        if cache_mtime >= source_mtime:
            return FileResponse(cached_path, media_type="audio/ogg", filename=ogg_filename)

    # Convert and cache
    success = await convert_mp3_to_ogg(source_path, cached_path)
    if not success:
        raise HTTPException(status_code=500, detail="Audio format conversion failed")

    return FileResponse(cached_path, media_type="audio/ogg", filename=ogg_filename)
