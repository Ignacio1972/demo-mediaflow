"""
Shared audio generation logic.

Both the REST endpoint (audio.py) and the chat tool (tool_executor.py)
delegate here to avoid duplicating TTS generation, file handling, and
AudioMessage persistence.
"""
import os
import logging
from datetime import datetime
from typing import Optional, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydub import AudioSegment

from app.models.audio import AudioMessage
from app.models.voice_settings import VoiceSettings
from app.services.tts import voice_manager
from app.services.audio.jingle import jingle_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceNotFoundError(ValueError):
    """Raised when the requested voice does not exist."""

    def __init__(self, voice_id: str):
        self.voice_id = voice_id
        super().__init__(f"Voz '{voice_id}' no encontrada")


class VoiceInactiveError(ValueError):
    """Raised when the requested voice is inactive."""

    def __init__(self, voice_id: str):
        self.voice_id = voice_id
        super().__init__(f"Voz '{voice_id}' está inactiva")


async def generate_audio(
    text: str,
    voice_id: str,
    db: AsyncSession,
    add_jingles: bool = False,
    music_file: Optional[str] = None,
    priority: int = 4,
    category_id: Optional[str] = None,
    settings_override: Optional[Dict] = None,
    commit: bool = True,
) -> AudioMessage:
    """
    Generate TTS audio and persist an AudioMessage record.

    Args:
        text: Text to convert to speech.
        voice_id: Voice identifier (must exist and be active).
        db: Async database session.
        add_jingles: Mix the TTS with background music.
        music_file: Filename of the music track for the jingle.
        priority: Player queue priority (1=critical ... 5=low).
        category_id: Optional category to assign immediately.
        settings_override: Per-generation voice settings overrides.
        commit: True  -> db.commit() + db.refresh() (REST endpoint path).
                False -> db.flush() only (chat tool path, transaction managed externally).

    Returns:
        Persisted AudioMessage instance.

    Raises:
        VoiceNotFoundError: voice_id not found in database.
        VoiceInactiveError: voice exists but is inactive.
    """
    logger.info(
        f"🎙️ Audio generation request: voice={voice_id}, "
        f"text_length={len(text)}"
    )

    # ------------------------------------------------------------------
    # 1. Look up and validate voice
    # ------------------------------------------------------------------
    result = await db.execute(
        select(VoiceSettings).filter(VoiceSettings.id == voice_id)
    )
    voice = result.scalar_one_or_none()

    if not voice:
        raise VoiceNotFoundError(voice_id)
    if not voice.active:
        raise VoiceInactiveError(voice_id)

    # ------------------------------------------------------------------
    # 2. Generate TTS via voice_manager (applies settings automatically)
    # ------------------------------------------------------------------
    logger.info(f"🎛️ Using voice settings: {voice.name}")
    audio_bytes, voice_used, effective_settings = await voice_manager.generate_with_voice(
        text=text,
        voice_id=voice_id,
        db=db,
        settings_override=settings_override,
    )

    # ------------------------------------------------------------------
    # 3. Save raw TTS to file
    # ------------------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tts_{timestamp}_{voice.id}.mp3"
    file_path = os.path.join(settings.AUDIO_PATH, filename)
    os.makedirs(settings.AUDIO_PATH, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    logger.info(f"💾 TTS audio saved: {filename}")

    # ------------------------------------------------------------------
    # 4. Audio post-processing
    # ------------------------------------------------------------------
    audio = AudioSegment.from_file(file_path)
    duration = len(audio) / 1000.0
    file_size = os.path.getsize(file_path)

    # Volume adjustment
    volume_adj = effective_settings.get("volume_adjustment", voice.volume_adjustment)
    if volume_adj != 0:
        logger.info(f"🔊 Applying volume adjustment: {volume_adj} dB")
        adjusted_audio = audio + volume_adj
        adjusted_audio.export(file_path, format="mp3", bitrate="192k")
        file_size = os.path.getsize(file_path)

    # TTS silence padding (only when NOT creating a jingle)
    if not (add_jingles and music_file):
        tts_settings = voice.tts_settings or {}
        intro_silence = tts_settings.get("intro_silence", 0)
        outro_silence = tts_settings.get("outro_silence", 0)
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

    # ------------------------------------------------------------------
    # 5. Jingle creation (mix TTS with background music)
    # ------------------------------------------------------------------
    if add_jingles and music_file:
        logger.info(f"🎵 Creating jingle with music: {music_file}")
        jingle_filename = f"jingle_{timestamp}_{voice.id}.mp3"
        jingle_path = os.path.join(settings.AUDIO_PATH, jingle_filename)
        voice_jingle_settings = voice.jingle_settings if voice.jingle_settings else None

        jingle_result = await jingle_service.create_jingle(
            voice_audio_path=file_path,
            music_filename=music_file,
            output_path=jingle_path,
            voice_jingle_settings=voice_jingle_settings,
        )

        if jingle_result["success"]:
            os.remove(file_path)
            filename = jingle_filename
            file_path = jingle_path
            duration = jingle_result["duration"]
            file_size = os.path.getsize(file_path)
            logger.info(f"🎉 Jingle created successfully: {filename} ({duration:.2f}s)")
        else:
            logger.warning(
                f"⚠️ Jingle creation failed: {jingle_result.get('error')}, "
                f"using TTS-only audio"
            )

    # ------------------------------------------------------------------
    # 6. Build and persist AudioMessage
    # ------------------------------------------------------------------
    display_name = text[:50] + "..." if len(text) > 50 else text
    settings_snapshot = voice_manager.get_voice_settings_snapshot(voice)

    audio_message = AudioMessage(
        filename=filename,
        display_name=display_name,
        file_path=file_path,
        file_size=file_size,
        duration=duration,
        format="mp3",
        original_text=text,
        voice_id=voice.id,
        voice_settings_snapshot=settings_snapshot,
        volume_adjustment=effective_settings.get("volume_adjustment", voice.volume_adjustment),
        has_jingle=add_jingles,
        music_file=music_file,
        status="ready",
        priority=priority,
        category_id=category_id,
    )

    db.add(audio_message)

    if commit:
        await db.commit()
        await db.refresh(audio_message)
    else:
        await db.flush()

    logger.info(f"✅ Audio message created: ID={audio_message.id}")
    return audio_message
