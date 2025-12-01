"""
Settings API Endpoints
Handles voice settings management and configuration - v2.1 Playground
"""
import os
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.services.tts import elevenlabs_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== SCHEMAS ====================

class JingleSettingsSchema(BaseModel):
    music_volume: float = Field(1.0, ge=0, le=5)
    voice_volume: float = Field(1.0, ge=0, le=5)
    duck_level: float = Field(0.2, ge=0, le=1)
    intro_silence: float = Field(3, ge=0, le=15)
    outro_silence: float = Field(5, ge=0, le=20)


class VoiceSettingsCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9_]+$')
    name: str = Field(..., min_length=1, max_length=100)
    elevenlabs_id: str = Field(..., min_length=1)
    gender: Optional[str] = Field(None, pattern=r'^[MF]?$')
    description: Optional[str] = None
    active: bool = True
    is_default: bool = False
    style: float = Field(50.0, ge=0, le=100)
    stability: float = Field(55.0, ge=0, le=100)
    similarity_boost: float = Field(80.0, ge=0, le=100)
    use_speaker_boost: bool = True
    volume_adjustment: float = Field(0.0, ge=-20, le=20)
    jingle_settings: Optional[JingleSettingsSchema] = None


class VoiceSettingsUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    elevenlabs_id: Optional[str] = None
    gender: Optional[str] = Field(None, pattern=r'^[MF]?$')
    description: Optional[str] = None
    active: Optional[bool] = None
    is_default: Optional[bool] = None
    style: Optional[float] = Field(None, ge=0, le=100)
    stability: Optional[float] = Field(None, ge=0, le=100)
    similarity_boost: Optional[float] = Field(None, ge=0, le=100)
    use_speaker_boost: Optional[bool] = None
    volume_adjustment: Optional[float] = Field(None, ge=-20, le=20)
    jingle_settings: Optional[dict] = None


class VoiceReorderRequest(BaseModel):
    voice_ids: List[str]


class VoiceTestRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class VoiceTestResponse(BaseModel):
    audio_url: str
    duration: float
    filename: str


# ==================== VOICE ENDPOINTS ====================

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

        return [
            {
                "id": v.id,
                "name": v.name,
                "elevenlabs_id": v.elevenlabs_id,
                "active": v.active,
                "is_default": v.is_default,
                "order": v.order,
                "gender": v.gender,
                "accent": v.accent,
                "description": v.description,
                "style": v.style,
                "stability": v.stability,
                "similarity_boost": v.similarity_boost,
                "use_speaker_boost": v.use_speaker_boost,
                "volume_adjustment": v.volume_adjustment,
                "jingle_settings": v.jingle_settings,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "updated_at": v.updated_at.isoformat() if v.updated_at else None,
            }
            for v in voices
        ]

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

        return {
            "id": voice.id,
            "name": voice.name,
            "elevenlabs_id": voice.elevenlabs_id,
            "active": voice.active,
            "is_default": voice.is_default,
            "order": voice.order,
            "gender": voice.gender,
            "accent": voice.accent,
            "description": voice.description,
            "style": voice.style,
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "use_speaker_boost": voice.use_speaker_boost,
            "volume_adjustment": voice.volume_adjustment,
            "jingle_settings": voice.jingle_settings,
            "created_at": voice.created_at.isoformat() if voice.created_at else None,
            "updated_at": voice.updated_at.isoformat() if voice.updated_at else None,
        }

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
            volume_adjustment=voice_data.volume_adjustment,
            jingle_settings=voice_data.jingle_settings.model_dump() if voice_data.jingle_settings else None,
        )

        db.add(voice)
        await db.commit()
        await db.refresh(voice)

        logger.info(f"✅ Voice created: {voice.id}")

        return {
            "id": voice.id,
            "name": voice.name,
            "elevenlabs_id": voice.elevenlabs_id,
            "active": voice.active,
            "is_default": voice.is_default,
            "order": voice.order,
            "gender": voice.gender,
            "accent": voice.accent,
            "description": voice.description,
            "style": voice.style,
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "use_speaker_boost": voice.use_speaker_boost,
            "volume_adjustment": voice.volume_adjustment,
            "jingle_settings": voice.jingle_settings,
            "created_at": voice.created_at.isoformat() if voice.created_at else None,
            "updated_at": voice.updated_at.isoformat() if voice.updated_at else None,
        }

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

        return {
            "id": voice.id,
            "name": voice.name,
            "elevenlabs_id": voice.elevenlabs_id,
            "active": voice.active,
            "is_default": voice.is_default,
            "order": voice.order,
            "gender": voice.gender,
            "accent": voice.accent,
            "description": voice.description,
            "style": voice.style,
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "use_speaker_boost": voice.use_speaker_boost,
            "volume_adjustment": voice.volume_adjustment,
            "jingle_settings": voice.jingle_settings,
            "created_at": voice.created_at.isoformat() if voice.created_at else None,
            "updated_at": voice.updated_at.isoformat() if voice.updated_at else None,
        }

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
        voice_settings = {
            "stability": voice.stability,  # Will be normalized by service
            "similarity_boost": voice.similarity_boost,
            "style": voice.style,
            "use_speaker_boost": voice.use_speaker_boost,
        }

        audio_bytes = await elevenlabs_service.generate_speech(
            text=request.text,
            voice_id=voice.elevenlabs_id,
            voice_settings=voice_settings,
        )

        # Save to temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_{voice_id}_{timestamp}.mp3"
        file_path = os.path.join(settings.AUDIO_PATH, filename)

        # Ensure directory exists
        os.makedirs(settings.AUDIO_PATH, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Get duration (simple estimate based on file size, ~16KB per second for MP3 128kbps)
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
