"""
Voice Settings API Endpoints
Handles voice configuration management - v2.1 Playground
"""
import io
import os
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydub import AudioSegment

from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.services.tts import elevenlabs_service
from app.core.config import settings
from app.schemas.voice import (
    VoiceSettingsCreate,
    VoiceSettingsUpdate,
    VoiceReorderRequest,
    VoiceTestRequest,
    VoiceTestResponse,
)
from app.api.v1.serializers import serialize_voice

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/voices",
    summary="Get All Voices",
    description="Get all voice configurations ordered by their order field",
)
async def get_all_voices(
    db: AsyncSession = Depends(get_db),
):
    """Get all voices for Voice Manager"""
    try:
        logger.info("📋 Fetching all voices for settings")

        result = await db.execute(
            select(VoiceSettings).order_by(VoiceSettings.order.asc())
        )
        voices = result.scalars().all()

        logger.info(f"✅ Retrieved {len(voices)} voices")

        return [serialize_voice(v) for v in voices]

    except Exception as e:
        logger.error(f"❌ Failed to fetch voices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voices: {str(e)}",
        )


@router.get(
    "/voices/{voice_id}",
    summary="Get Single Voice",
    description="Get a single voice configuration by ID",
)
async def get_voice(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get single voice by ID"""
    try:
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        return serialize_voice(voice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch voice: {str(e)}",
        )


@router.post(
    "/voices",
    status_code=status.HTTP_201_CREATED,
    summary="Create Voice",
    description="Create a new voice configuration",
)
async def create_voice(
    voice_data: VoiceSettingsCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new voice"""
    try:
        logger.info(f"➕ Creating voice: {voice_data.id}")

        # Check if ID already exists
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_data.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voice with ID '{voice_data.id}' already exists",
            )

        # Get next order number
        result = await db.execute(select(VoiceSettings))
        all_voices = result.scalars().all()
        next_order = max([v.order for v in all_voices], default=-1) + 1

        # Create voice
        voice = VoiceSettings(
            id=voice_data.id,
            name=voice_data.name,
            elevenlabs_id=voice_data.elevenlabs_id,
            active=voice_data.active,
            is_default=voice_data.is_default,
            order=next_order,
            gender=voice_data.gender,
            description=voice_data.description,
            style=voice_data.style,
            stability=voice_data.stability,
            similarity_boost=voice_data.similarity_boost,
            use_speaker_boost=voice_data.use_speaker_boost,
            speed=voice_data.speed,  # ElevenLabs 2025
            volume_adjustment=voice_data.volume_adjustment,
            jingle_settings=voice_data.jingle_settings.model_dump() if voice_data.jingle_settings else None,
        )

        db.add(voice)
        await db.commit()
        await db.refresh(voice)

        logger.info(f"✅ Voice created: {voice.id}")

        return serialize_voice(voice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create voice: {str(e)}",
        )


@router.patch(
    "/voices/{voice_id}",
    summary="Update Voice",
    description="Update an existing voice configuration",
)
async def update_voice(
    voice_id: str,
    voice_data: VoiceSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing voice"""
    try:
        logger.info(f"📝 Updating voice: {voice_id}")

        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        # Update fields
        update_data = voice_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(voice, field, value)

        await db.commit()
        await db.refresh(voice)

        logger.info(f"✅ Voice updated: {voice.id}")

        return serialize_voice(voice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update voice: {str(e)}",
        )


@router.delete(
    "/voices/{voice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Voice",
    description="Delete a voice configuration",
)
async def delete_voice(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a voice"""
    try:
        logger.info(f"🗑️ Deleting voice: {voice_id}")

        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        # Don't allow deleting default voice
        if voice.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete default voice. Set another voice as default first.",
            )

        await db.delete(voice)
        await db.commit()

        logger.info(f"✅ Voice deleted: {voice_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete voice: {str(e)}",
        )


@router.patch(
    "/voices/{voice_id}/set-default",
    summary="Set Default Voice",
    description="Set a voice as the default voice",
)
async def set_default_voice(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Set a voice as default"""
    try:
        logger.info(f"⭐ Setting default voice: {voice_id}")

        # Check voice exists
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        # Unset all defaults
        await db.execute(
            update(VoiceSettings).values(is_default=False)
        )

        # Set new default
        voice.is_default = True
        await db.commit()

        logger.info(f"✅ Default voice set: {voice_id}")

        return {"success": True, "message": f"Voice '{voice.name}' is now the default"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set default voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default voice: {str(e)}",
        )


@router.put(
    "/voices/reorder",
    summary="Reorder Voices",
    description="Update the order of voices",
)
async def reorder_voices(
    request: VoiceReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder voices"""
    try:
        logger.info(f"🔄 Reordering voices: {request.voice_ids}")

        # Update order for each voice
        for index, voice_id in enumerate(request.voice_ids):
            await db.execute(
                update(VoiceSettings)
                .where(VoiceSettings.id == voice_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Voices reordered")

        return {"success": True, "message": "Voices reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder voices: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder voices: {str(e)}",
        )


@router.post(
    "/voices/{voice_id}/test",
    response_model=VoiceTestResponse,
    summary="Test Voice",
    description="Generate a test audio using ElevenLabs with current voice settings",
)
async def test_voice(
    voice_id: str,
    request: VoiceTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """Test a voice with ElevenLabs"""
    try:
        logger.info(f"🔊 Testing voice: {voice_id}")

        # Get voice
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )

        # Generate audio using ElevenLabs with voice settings
        # Including speed parameter (ElevenLabs 2025 API)
        voice_settings = {
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "style": voice.style,
            "use_speaker_boost": voice.use_speaker_boost,
            "speed": voice.speed,
        }

        audio_bytes = await elevenlabs_service.generate_speech(
            text=request.text,
            voice_id=voice.elevenlabs_id,
            voice_settings=voice_settings,
        )

        # Apply volume adjustment if configured
        volume_adjustment = voice.volume_adjustment or 0
        if volume_adjustment != 0:
            logger.info(f"🔊 Applying volume adjustment: {volume_adjustment} dB")
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            audio_segment = audio_segment + volume_adjustment

            # Export back to bytes
            output_buffer = io.BytesIO()
            audio_segment.export(output_buffer, format="mp3", bitrate="192k")
            audio_bytes = output_buffer.getvalue()
            logger.info(f"✅ Volume adjusted by {volume_adjustment} dB")

        # Save to temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_{voice_id}_{timestamp}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Get duration (simple estimate based on file size)
        file_size = os.path.getsize(file_path)
        estimated_duration = file_size / 16000

        logger.info(f"✅ Test audio generated: {filename}")

        return VoiceTestResponse(
            audio_url=f"/storage/audio/{filename}",
            duration=round(estimated_duration, 2),
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to test voice: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test voice: {str(e)}",
        )
