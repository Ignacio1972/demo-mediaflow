"""
Automatic Mode API Endpoints
Handles automatic jingle generation with AI text improvement - v2.1 Playground
"""
import os
import uuid
import shutil
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.voice_settings import VoiceSettings
from app.models.music_track import MusicTrack
from app.models.audio import AudioMessage
from app.core.config import settings
from app.schemas.automatic import (
    AutomaticGenerateRequest,
    AutomaticGenerateResponse,
    AutomaticConfigResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Word limits configuration (based on target duration)
WORD_LIMITS = {
    5: {"min": 5, "max": 8},
    10: {"min": 10, "max": 15},
    15: {"min": 15, "max": 20},
    20: {"min": 20, "max": 30},
    25: {"min": 30, "max": 40},
}

AVAILABLE_DURATIONS = [5, 10, 15, 20, 25]


@router.get(
    "/automatic/config",
    response_model=AutomaticConfigResponse,
    summary="Get Automatic Mode Config",
    description="Get default configuration for automatic mode",
)
async def get_automatic_config(
    db: AsyncSession = Depends(get_db),
):
    """Get configuration for automatic mode"""
    try:
        logger.info("⚙️ Fetching automatic mode configuration")

        # Get default voice
        result = await db.execute(
            select(VoiceSettings)
            .filter(VoiceSettings.is_default == True, VoiceSettings.active == True)
        )
        default_voice = result.scalar_one_or_none()

        # Get default music
        result = await db.execute(
            select(MusicTrack)
            .filter(MusicTrack.is_default == True, MusicTrack.active == True)
        )
        default_music = result.scalar_one_or_none()

        return AutomaticConfigResponse(
            default_voice_id=default_voice.id if default_voice else None,
            default_music=default_music.filename if default_music else None,
            available_durations=AVAILABLE_DURATIONS,
            word_limits=WORD_LIMITS,
        )

    except Exception as e:
        logger.error(f"❌ Failed to fetch automatic config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch automatic config: {str(e)}",
        )


@router.post(
    "/automatic/generate",
    response_model=AutomaticGenerateResponse,
    summary="Generate Automatic Jingle",
    description="Generate a jingle from text input using AI improvement and TTS",
)
async def generate_automatic_jingle(
    request: AutomaticGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate automatic jingle with the full pipeline:
    1. Improve text with Claude AI (optional)
    2. Generate TTS with ElevenLabs
    3. Mix with background music (optional)
    """
    try:
        logger.info(f"🎙️ Starting automatic generation: voice={request.voice_id}, duration={request.target_duration}s")

        # 1. Get voice settings
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == request.voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{request.voice_id}' not found",
            )

        if not voice.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Voice '{voice.name}' is not active",
            )

        original_text = request.text.strip()
        improved_text = original_text

        # 2. Improve text with Claude AI (if enabled)
        if request.improve_text:
            logger.info("🤖 Improving text with Claude AI...")
            from app.services.ai.claude import claude_service

            # Get word limits for target duration
            word_limit = WORD_LIMITS.get(request.target_duration, {"min": 20, "max": 30})
            min_words, max_words = word_limit["min"], word_limit["max"]

            try:
                improved_text = await claude_service.improve_text(
                    text=original_text,
                    max_words=max_words,
                )

                # Validate word count
                word_count = len(improved_text.split())
                logger.info(f"✅ Text improved: {word_count} words (target: {min_words}-{max_words})")

            except Exception as ai_error:
                logger.warning(f"⚠️ AI improvement failed, using original text: {ai_error}")
                improved_text = original_text

        # 3. Generate TTS with ElevenLabs
        logger.info("🔊 Generating TTS audio...")
        from app.services.tts.elevenlabs import elevenlabs_service

        voice_settings = {
            "style": voice.style,
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "use_speaker_boost": voice.use_speaker_boost,
        }

        tts_audio = await elevenlabs_service.generate_speech(
            text=improved_text,
            voice_id=voice.elevenlabs_id,
            voice_settings=voice_settings,
        )

        # 4. Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"auto_{timestamp}_{request.voice_id}_{unique_id}.mp3"

        # 5. Save TTS audio (temporarily)
        temp_voice_path = os.path.join(settings.TEMP_PATH, f"voice_{unique_id}.mp3")
        with open(temp_voice_path, "wb") as f:
            f.write(tts_audio)

        output_path = os.path.join(settings.AUDIO_PATH, filename)
        final_duration = None

        # 6. Mix with music if provided
        has_music = request.music_file and request.music_file.lower() not in ['none', '', 'null']

        if has_music:
            logger.info(f"🎵 Mixing with music: {request.music_file}")
            from app.services.audio.jingle import jingle_service, JingleConfig

            # Get voice-specific jingle settings or use defaults
            jingle_config = JingleConfig()
            if voice.jingle_settings:
                jingle_config.music_volume = voice.jingle_settings.get('music_volume', 1.65)
                jingle_config.voice_volume = voice.jingle_settings.get('voice_volume', 2.8)
                jingle_config.duck_level = voice.jingle_settings.get('duck_level', 0.95)
                jingle_config.intro_silence = voice.jingle_settings.get('intro_silence', 7.0)
                jingle_config.outro_silence = voice.jingle_settings.get('outro_silence', 4.5)

            jingle_result = await jingle_service.create_jingle(
                voice_audio_path=temp_voice_path,
                music_filename=request.music_file,
                output_path=output_path,
                config=jingle_config,
            )

            if not jingle_result['success']:
                # Fallback: save TTS audio without music
                logger.warning(f"⚠️ Jingle creation failed: {jingle_result.get('error')}, saving TTS only")
                shutil.copy(temp_voice_path, output_path)
            else:
                final_duration = jingle_result.get('duration')
        else:
            # No music - just copy TTS audio
            shutil.copy(temp_voice_path, output_path)

        # Get final duration if not set
        if final_duration is None:
            from app.services.audio.jingle import jingle_service
            final_duration = jingle_service._get_audio_duration(output_path)

        # Clean up temp file
        if os.path.exists(temp_voice_path):
            os.remove(temp_voice_path)

        # Build audio URL
        audio_url = f"/storage/audio/{filename}"

        # Get file size
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else None

        # Create display name from improved text (first 50 chars)
        display_name = (
            improved_text[:50] + "..." if len(improved_text) > 50 else improved_text
        )

        # Save to database
        audio_message = AudioMessage(
            filename=filename,
            display_name=display_name,
            file_path=output_path,
            file_size=file_size,
            duration=final_duration,
            format="mp3",
            original_text=original_text,
            voice_id=voice.id,
            volume_adjustment=voice.volume_adjustment,
            has_jingle=has_music,
            music_file=request.music_file if has_music else None,
            status="ready",
            is_favorite=False,
        )

        db.add(audio_message)
        await db.commit()
        await db.refresh(audio_message)

        logger.info(f"✅ Automatic jingle generated: {filename} ({final_duration:.2f}s) - ID={audio_message.id}")

        return AutomaticGenerateResponse(
            success=True,
            original_text=original_text,
            improved_text=improved_text,
            voice_used=voice.name,
            audio_url=audio_url,
            filename=filename,
            duration=final_duration,
            error=None,
            audio_id=audio_message.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Automatic generation failed: {str(e)}", exc_info=True)
        return AutomaticGenerateResponse(
            success=False,
            original_text=request.text,
            improved_text=request.text,
            voice_used=request.voice_id,
            audio_url="",
            filename="",
            duration=None,
            error=str(e),
            audio_id=None,
        )
