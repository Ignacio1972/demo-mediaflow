"""
Settings API Endpoints
Handles voice settings management and configuration - v2.1 Playground
"""
import io
import os
import logging
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, Field
from pydub import AudioSegment

from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.models.music_track import MusicTrack
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

        # Apply volume adjustment if configured
        volume_adjustment = voice.volume_adjustment or 0
        if volume_adjustment != 0:
            logger.info(f"🔊 Applying volume adjustment: {volume_adjustment} dB")
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            audio_segment = audio_segment + volume_adjustment  # pydub uses + for dB gain

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


# ==================== MUSIC ENDPOINTS ====================

class MusicTrackResponse(BaseModel):
    id: int
    filename: str
    display_name: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    bitrate: Optional[str] = None
    is_default: bool
    active: bool
    order: int
    artist: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    audio_url: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MusicTrackUpdate(BaseModel):
    display_name: Optional[str] = None
    is_default: Optional[bool] = None
    active: Optional[bool] = None
    order: Optional[int] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None


class MusicReorderRequest(BaseModel):
    track_ids: List[int]


def get_audio_metadata(file_path: str) -> dict:
    """Extract audio metadata using pydub"""
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio) / 1000.0  # ms to seconds

        # Estimate bitrate from file size and duration
        file_size = os.path.getsize(file_path)
        if duration > 0:
            bitrate_kbps = int((file_size * 8) / (duration * 1000))
            bitrate = f"{bitrate_kbps}kbps"
        else:
            bitrate = "unknown"

        return {
            "duration": round(duration, 2),
            "bitrate": bitrate,
            "sample_rate": audio.frame_rate,
            "file_size": file_size,
        }
    except Exception as e:
        logger.warning(f"Could not extract audio metadata: {e}")
        return {
            "duration": None,
            "bitrate": None,
            "sample_rate": None,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else None,
        }


@router.get(
    "/music",
    response_model=List[MusicTrackResponse],
    summary="Get All Music Tracks",
    description="Get all music tracks for jingle generation",
)
async def get_all_music(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all music tracks ordered by order field"""
    try:
        logger.info("🎵 Fetching all music tracks")

        query = select(MusicTrack).order_by(MusicTrack.order.asc())
        if active_only:
            query = query.filter(MusicTrack.active == True)

        result = await db.execute(query)
        tracks = result.scalars().all()

        logger.info(f"✅ Retrieved {len(tracks)} music tracks")

        return [
            MusicTrackResponse(
                id=t.id,
                filename=t.filename,
                display_name=t.display_name,
                file_size=t.file_size,
                duration=t.duration,
                bitrate=t.bitrate,
                is_default=t.is_default,
                active=t.active,
                order=t.order,
                artist=t.artist,
                genre=t.genre,
                mood=t.mood,
                audio_url=f"/storage/music/{t.filename}",
                created_at=t.created_at.isoformat() if t.created_at else None,
                updated_at=t.updated_at.isoformat() if t.updated_at else None,
            )
            for t in tracks
        ]

    except Exception as e:
        logger.error(f"❌ Failed to fetch music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch music: {str(e)}",
        )


@router.get(
    "/music/{track_id}",
    response_model=MusicTrackResponse,
    summary="Get Single Music Track",
)
async def get_music_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single music track by ID"""
    try:
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        return MusicTrackResponse(
            id=track.id,
            filename=track.filename,
            display_name=track.display_name,
            file_size=track.file_size,
            duration=track.duration,
            bitrate=track.bitrate,
            is_default=track.is_default,
            active=track.active,
            order=track.order,
            artist=track.artist,
            genre=track.genre,
            mood=track.mood,
            audio_url=f"/storage/music/{track.filename}",
            created_at=track.created_at.isoformat() if track.created_at else None,
            updated_at=track.updated_at.isoformat() if track.updated_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch track: {str(e)}",
        )


@router.post(
    "/music",
    response_model=MusicTrackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Music Track",
    description="Upload a new music track for jingle generation",
)
async def upload_music(
    file: UploadFile = File(...),
    display_name: Optional[str] = Form(None),
    artist: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    mood: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new music track"""
    try:
        logger.info(f"📤 Uploading music: {file.filename}")

        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        allowed_extensions = {".mp3", ".wav", ".ogg", ".m4a"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
            )

        # Check if filename already exists
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.filename == file.filename)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A track with filename '{file.filename}' already exists",
            )

        # Ensure music directory exists
        os.makedirs(settings.MUSIC_PATH, exist_ok=True)

        # Save file
        file_path = os.path.join(settings.MUSIC_PATH, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"💾 File saved: {file_path}")

        # Get audio metadata
        metadata = get_audio_metadata(file_path)

        # Get next order number
        result = await db.execute(select(MusicTrack))
        all_tracks = result.scalars().all()
        next_order = max([t.order for t in all_tracks], default=-1) + 1

        # Create display name from filename if not provided
        if not display_name:
            display_name = os.path.splitext(file.filename)[0]

        # Create database record
        track = MusicTrack(
            filename=file.filename,
            display_name=display_name,
            file_path=file_path,
            file_size=metadata.get("file_size"),
            duration=metadata.get("duration"),
            bitrate=metadata.get("bitrate"),
            sample_rate=metadata.get("sample_rate"),
            format=file_ext[1:],  # Remove the dot
            is_default=False,
            active=True,
            order=next_order,
            artist=artist,
            genre=genre,
            mood=mood,
        )

        db.add(track)
        await db.commit()
        await db.refresh(track)

        logger.info(f"✅ Music track created: {track.display_name} (ID={track.id})")

        return MusicTrackResponse(
            id=track.id,
            filename=track.filename,
            display_name=track.display_name,
            file_size=track.file_size,
            duration=track.duration,
            bitrate=track.bitrate,
            is_default=track.is_default,
            active=track.active,
            order=track.order,
            artist=track.artist,
            genre=track.genre,
            mood=track.mood,
            audio_url=f"/storage/music/{track.filename}",
            created_at=track.created_at.isoformat() if track.created_at else None,
            updated_at=track.updated_at.isoformat() if track.updated_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to upload music: {str(e)}", exc_info=True)
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload music: {str(e)}",
        )


@router.patch(
    "/music/{track_id}",
    response_model=MusicTrackResponse,
    summary="Update Music Track",
)
async def update_music_track(
    track_id: int,
    update_data: MusicTrackUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update music track metadata"""
    try:
        logger.info(f"📝 Updating music track: {track_id}")

        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(track, field, value)

        await db.commit()
        await db.refresh(track)

        logger.info(f"✅ Music track updated: {track.display_name}")

        return MusicTrackResponse(
            id=track.id,
            filename=track.filename,
            display_name=track.display_name,
            file_size=track.file_size,
            duration=track.duration,
            bitrate=track.bitrate,
            is_default=track.is_default,
            active=track.active,
            order=track.order,
            artist=track.artist,
            genre=track.genre,
            mood=track.mood,
            audio_url=f"/storage/music/{track.filename}",
            created_at=track.created_at.isoformat() if track.created_at else None,
            updated_at=track.updated_at.isoformat() if track.updated_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update track: {str(e)}",
        )


@router.delete(
    "/music/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Music Track",
)
async def delete_music_track(
    track_id: int,
    delete_file: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Delete a music track"""
    try:
        logger.info(f"🗑️ Deleting music track: {track_id}")

        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Delete file if requested
        if delete_file and track.file_path and os.path.exists(track.file_path):
            os.remove(track.file_path)
            logger.info(f"🗑️ File deleted: {track.file_path}")

        # Delete database record
        await db.delete(track)
        await db.commit()

        logger.info(f"✅ Music track deleted: {track.display_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete track: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete track: {str(e)}",
        )


@router.patch(
    "/music/{track_id}/set-default",
    summary="Set Default Music Track",
)
async def set_default_music(
    track_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Set a music track as the default"""
    try:
        logger.info(f"⭐ Setting default music: {track_id}")

        # Check track exists
        result = await db.execute(
            select(MusicTrack).filter(MusicTrack.id == track_id)
        )
        track = result.scalar_one_or_none()

        if not track:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Music track with ID {track_id} not found",
            )

        # Unset all defaults
        await db.execute(
            update(MusicTrack).values(is_default=False)
        )

        # Set new default
        track.is_default = True
        await db.commit()

        logger.info(f"✅ Default music set: {track.display_name}")

        return {"success": True, "message": f"'{track.display_name}' is now the default music"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set default music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default music: {str(e)}",
        )


@router.put(
    "/music/reorder",
    summary="Reorder Music Tracks",
)
async def reorder_music(
    request: MusicReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder music tracks"""
    try:
        logger.info(f"🔄 Reordering music tracks: {request.track_ids}")

        for index, track_id in enumerate(request.track_ids):
            await db.execute(
                update(MusicTrack)
                .where(MusicTrack.id == track_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Music tracks reordered")

        return {"success": True, "message": "Music tracks reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder music: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder music: {str(e)}",
        )


# ==================== CATEGORY ENDPOINTS ====================

from app.models.category import Category
from app.models.audio import AudioMessage
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryReorderRequest,
)


@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="Get All Categories",
    description="Get all categories for the Category Editor (includes inactive)",
)
async def get_all_categories_settings(
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get all categories for settings management"""
    try:
        logger.info("📂 Fetching all categories for settings")

        query = select(Category).order_by(Category.order.asc())
        if not include_inactive:
            query = query.filter(Category.active == True)

        result = await db.execute(query)
        categories = result.scalars().all()

        # Get message counts for each category
        response_list = []
        for cat in categories:
            # Count messages in this category
            count_result = await db.execute(
                select(AudioMessage)
                .filter(AudioMessage.category_id == cat.id)
            )
            message_count = len(count_result.scalars().all())

            response_list.append(
                CategoryResponse(
                    id=cat.id,
                    name=cat.name,
                    icon=cat.icon,
                    color=cat.color,
                    order=cat.order,
                    active=cat.active,
                    created_at=cat.created_at,
                    updated_at=cat.updated_at,
                    message_count=message_count,
                )
            )

        logger.info(f"✅ Retrieved {len(categories)} categories")
        return response_list

    except Exception as e:
        logger.error(f"❌ Failed to fetch categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}",
        )


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Get Single Category",
)
async def get_category_settings(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single category by ID"""
    try:
        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        cat = result.scalar_one_or_none()

        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        # Get message count
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == cat.id)
        )
        message_count = len(count_result.scalars().all())

        return CategoryResponse(
            id=cat.id,
            name=cat.name,
            icon=cat.icon,
            color=cat.color,
            order=cat.order,
            active=cat.active,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            message_count=message_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}",
        )


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Create a new category for organizing audio messages",
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new category"""
    try:
        logger.info(f"➕ Creating category: {category_data.id}")

        # Check if ID already exists
        result = await db.execute(
            select(Category).filter(Category.id == category_data.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID '{category_data.id}' already exists",
            )

        # Get next order number if not provided
        order = category_data.order
        if order is None:
            result = await db.execute(select(Category))
            all_categories = result.scalars().all()
            order = max([c.order for c in all_categories], default=-1) + 1

        # Create category
        category = Category(
            id=category_data.id,
            name=category_data.name,
            icon=category_data.icon or "📁",
            color=category_data.color or "#6B7280",
            order=order,
            active=category_data.active,
        )

        db.add(category)
        await db.commit()
        await db.refresh(category)

        logger.info(f"✅ Category created: {category.id}")

        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            color=category.color,
            order=category.order,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            message_count=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}",
        )


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update Category",
    description="Update an existing category",
)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing category"""
    try:
        logger.info(f"📝 Updating category: {category_id}")

        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)

        # Get message count
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == category.id)
        )
        message_count = len(count_result.scalars().all())

        logger.info(f"✅ Category updated: {category.id}")

        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            color=category.color,
            order=category.order,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            message_count=message_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}",
        )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="Delete a category (only if it has no associated messages)",
)
async def delete_category(
    category_id: str,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Delete a category"""
    try:
        logger.info(f"🗑️ Deleting category: {category_id}")

        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        # Check if category has messages
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == category_id)
        )
        message_count = len(count_result.scalars().all())

        if message_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category '{category.name}' because it has {message_count} associated messages. Set force=true to delete anyway (messages will be uncategorized).",
            )

        # If force delete, uncategorize all messages
        if message_count > 0 and force:
            logger.info(f"⚠️ Force delete: uncategorizing {message_count} messages")
            await db.execute(
                update(AudioMessage)
                .where(AudioMessage.category_id == category_id)
                .values(category_id=None)
            )

        # Delete category
        await db.delete(category)
        await db.commit()

        logger.info(f"✅ Category deleted: {category_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}",
        )


@router.put(
    "/categories/reorder",
    summary="Reorder Categories",
    description="Update the display order of categories",
)
async def reorder_categories(
    request: CategoryReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder categories"""
    try:
        logger.info(f"🔄 Reordering categories: {request.category_ids}")

        # Update order for each category
        for index, category_id in enumerate(request.category_ids):
            await db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Categories reordered")

        return {"success": True, "message": "Categories reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder categories: {str(e)}",
        )
