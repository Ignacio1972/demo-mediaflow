"""
Audio API Endpoints
Handles TTS generation with automatic voice settings - v2.1
"""
import os
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydub import AudioSegment

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
from app.services.tts import voice_manager, elevenlabs_service
from app.services.audio import jingle_service
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
        logger.info(
            f"🎙️ Audio generation request: voice={request.voice_id}, "
            f"text_length={len(request.text)}"
        )

        # Get voice configuration with settings
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == request.voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            logger.warning(f"⚠️ Voice not found: {request.voice_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{request.voice_id}' not found",
            )

        if not voice.active:
            logger.warning(f"⚠️ Voice inactive: {request.voice_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voice '{request.voice_id}' is inactive",
            )

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

        # Generate audio with automatic settings (and optional override)
        logger.info(f"🎛️ Using voice settings: {voice.name}")
        audio_bytes, voice_used, effective_settings = await voice_manager.generate_with_voice(
            text=request.text,
            voice_id=request.voice_id,
            db=db,
            settings_override=settings_override,
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}_{voice.id}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        # Save audio file (TTS only first)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"💾 TTS audio saved: {filename}")

        # Get audio metadata
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0  # milliseconds to seconds
        file_size = os.path.getsize(file_path)

        # Apply volume adjustment if configured (use override if provided)
        volume_adj = effective_settings.get("volume_adjustment", voice.volume_adjustment)
        if volume_adj != 0:
            logger.info(
                f"🔊 Applying volume adjustment: {volume_adj} dB"
            )
            adjusted_audio = audio + volume_adj
            adjusted_audio.export(file_path, format="mp3", bitrate="192k")
            file_size = os.path.getsize(file_path)

        # Apply TTS silence padding if configured and NOT using jingle
        if not (request.add_jingles and request.music_file):
            tts_settings = voice.tts_settings or {}
            intro_silence = tts_settings.get('intro_silence', 0)
            outro_silence = tts_settings.get('outro_silence', 0)

            if intro_silence > 0 or outro_silence > 0:
                logger.info(
                    f"🔇 Applying TTS padding: intro={intro_silence}s, outro={outro_silence}s"
                )
                audio = AudioSegment.from_file(file_path)
                if intro_silence > 0:
                    audio = AudioSegment.silent(duration=int(intro_silence * 1000)) + audio
                if outro_silence > 0:
                    audio = audio + AudioSegment.silent(duration=int(outro_silence * 1000))
                audio.export(file_path, format="mp3", bitrate="192k")
                duration = len(audio) / 1000.0
                file_size = os.path.getsize(file_path)
                logger.info(f"✅ TTS padding applied, new duration: {duration:.2f}s")

        # If jingle is requested and music file is provided, mix with music
        if request.add_jingles and request.music_file:
            logger.info(f"🎵 Creating jingle with music: {request.music_file}")

            # Generate jingle filename
            jingle_filename = f"jingle_{timestamp}_{voice.id}.mp3"
            jingle_path = os.path.join(settings.AUDIO_PATH, jingle_filename)

            # Get voice-specific jingle settings if available
            voice_jingle_settings = voice.jingle_settings if voice.jingle_settings else None

            # Create jingle
            jingle_result = await jingle_service.create_jingle(
                voice_audio_path=file_path,
                music_filename=request.music_file,
                output_path=jingle_path,
                voice_jingle_settings=voice_jingle_settings
            )

            if jingle_result['success']:
                # Remove original TTS file, use jingle instead
                os.remove(file_path)
                filename = jingle_filename
                file_path = jingle_path
                duration = jingle_result['duration']
                file_size = os.path.getsize(file_path)
                logger.info(f"🎉 Jingle created successfully: {filename} ({duration:.2f}s)")
            else:
                # Jingle creation failed, keep original TTS
                logger.warning(
                    f"⚠️ Jingle creation failed: {jingle_result.get('error')}, "
                    f"using TTS-only audio"
                )

        # Create display name from text (first 50 chars)
        display_name = (
            request.text[:50] + "..." if len(request.text) > 50 else request.text
        )

        # Get settings snapshot for storage
        settings_snapshot = voice_manager.get_voice_settings_snapshot(voice)

        # Save to database (use effective settings for volume_adjustment)
        audio_message = AudioMessage(
            filename=filename,
            display_name=display_name,
            file_path=file_path,
            file_size=file_size,
            duration=duration,
            format="mp3",
            original_text=request.text,
            voice_id=voice.id,
            voice_settings_snapshot=settings_snapshot,
            volume_adjustment=effective_settings.get("volume_adjustment", voice.volume_adjustment),
            has_jingle=request.add_jingles,
            music_file=request.music_file,
            status="ready",
            priority=request.priority,
            category_id=request.category_id,
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"✅ Audio message created: ID={audio_message.id}")

        # Cleanup old temporary messages if limit exceeded
        deleted_count = await cleanup_old_temporary_messages(db)
        if deleted_count > 0:
            logger.info(f"🧹 Auto-cleanup: {deleted_count} old temporary messages deleted")

        # Build audio URL (relative for frontend proxy)
        audio_url = f"/storage/audio/{filename}"

        # Build response (use effective_settings which includes any overrides)
        response = AudioGenerateResponse(
            audio_id=audio_message.id,
            filename=filename,
            display_name=display_name,
            audio_url=audio_url,
            file_size=file_size,
            duration=duration,
            status=audio_message.status,
            voice_id=voice.id,
            voice_name=voice.name,
            settings_applied={
                "style": effective_settings.get("style", voice.style),
                "stability": effective_settings.get("stability", voice.stability),
                "similarity_boost": effective_settings.get("similarity_boost", voice.similarity_boost),
                "speed": effective_settings.get("speed", voice.speed),
                "volume_adjustment": effective_settings.get("volume_adjustment", voice.volume_adjustment),
            },
            created_at=audio_message.created_at,
        )

        logger.info(f"🎉 Audio generation completed successfully: {filename}")
        return response

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
