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
from sqlalchemy import select
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
from app.services.tts import voice_manager, elevenlabs_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


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

        # Generate audio with automatic settings
        logger.info(f"🎛️ Using voice settings: {voice.name}")
        audio_bytes, voice_used = await voice_manager.generate_with_voice(
            text=request.text, voice_id=request.voice_id, db=db
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}_{voice.id}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        # Save audio file
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"💾 Audio saved: {filename}")

        # Get audio metadata
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0  # milliseconds to seconds
        file_size = os.path.getsize(file_path)

        # Apply volume adjustment if configured
        if voice.volume_adjustment != 0:
            logger.info(
                f"🔊 Applying volume adjustment: {voice.volume_adjustment} dB"
            )
            adjusted_audio = audio + voice.volume_adjustment
            adjusted_audio.export(file_path, format="mp3", bitrate="192k")
            file_size = os.path.getsize(file_path)

        # Create display name from text (first 50 chars)
        display_name = (
            request.text[:50] + "..." if len(request.text) > 50 else request.text
        )

        # Get settings snapshot for storage
        settings_snapshot = voice_manager.get_voice_settings_snapshot(voice)

        # Save to database
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
            volume_adjustment=voice.volume_adjustment,
            has_jingle=request.add_jingles,
            music_file=request.music_file,
            status="ready",
            priority=request.priority,
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"✅ Audio message created: ID={audio_message.id}")

        # Build audio URL (relative for frontend proxy)
        audio_url = f"/storage/audio/{filename}"

        # Build response
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
                "style": voice.style,
                "stability": voice.stability,
                "similarity_boost": voice.similarity_boost,
                "volume_adjustment": voice.volume_adjustment,
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
                "display_name": msg.display_name,
                "voice_id": msg.voice_id,
                "duration": msg.duration,
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
