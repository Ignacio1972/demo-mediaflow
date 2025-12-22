"""
Voice Manager Service
Manages voice settings and automatically applies them during TTS generation
"""
import json
import logging
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.voice_settings import VoiceSettings
from app.services.tts.elevenlabs import elevenlabs_service

logger = logging.getLogger(__name__)


class VoiceManager:
    """
    Manages voice configurations with automatic settings application
    Critical component for v2.1 architecture
    """

    def __init__(self):
        self._cache: Dict[str, VoiceSettings] = {}
        self._cache_loaded = False

    async def get_voice_with_settings(
        self, voice_id: str, db: AsyncSession
    ) -> Optional[VoiceSettings]:
        """
        Get voice configuration with all predefined settings

        Args:
            voice_id: Voice identifier (e.g., 'juan_carlos')
            db: Database session

        Returns:
            VoiceSettings object or None if not found
        """
        # Check cache first
        if voice_id in self._cache:
            logger.debug(f"✅ Voice '{voice_id}' loaded from cache")
            return self._cache[voice_id]

        # Query database with async
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if voice:
            # Update cache
            self._cache[voice_id] = voice
            logger.info(f"✅ Voice '{voice_id}' loaded from database")
            return voice

        logger.warning(f"⚠️ Voice '{voice_id}' not found")
        return None

    async def get_all_active_voices(self, db: AsyncSession) -> List[VoiceSettings]:
        """
        Get all active voices ordered by priority

        Args:
            db: Database session

        Returns:
            List of active VoiceSettings
        """
        result = await db.execute(
            select(VoiceSettings)
            .filter(VoiceSettings.active == True)
            .order_by(VoiceSettings.order.asc())
        )
        voices = result.scalars().all()

        logger.info(f"📋 Retrieved {len(voices)} active voices")
        return voices

    async def get_default_voice(self, db: AsyncSession) -> Optional[VoiceSettings]:
        """
        Get the default voice

        Args:
            db: Database session

        Returns:
            Default VoiceSettings or None
        """
        result = await db.execute(
            select(VoiceSettings).filter(
                VoiceSettings.is_default == True, VoiceSettings.active == True
            )
        )
        voice = result.scalar_one_or_none()

        if voice:
            logger.info(f"✅ Default voice: {voice.name}")
        else:
            logger.warning("⚠️ No default voice configured")

        return voice

    def get_elevenlabs_settings(self, voice: VoiceSettings) -> Dict:
        """
        Convert VoiceSettings to ElevenLabs API format

        Args:
            voice: VoiceSettings object

        Returns:
            dict: Settings ready for ElevenLabs API
        """
        settings = {
            "style": voice.style / 100.0,  # Convert from 0-100 to 0-1
            "stability": voice.stability / 100.0,
            "similarity_boost": voice.similarity_boost / 100.0,
            "use_speaker_boost": voice.use_speaker_boost,
            "speed": voice.speed,  # ElevenLabs 2025: already in 0.7-1.2 range
        }

        logger.debug(
            f"🎛️ Voice '{voice.name}' settings: "
            f"style={settings['style']:.2f}, "
            f"stability={settings['stability']:.2f}, "
            f"similarity={settings['similarity_boost']:.2f}, "
            f"speed={settings['speed']:.2f}"
        )

        return settings

    async def generate_with_voice(
        self,
        text: str,
        voice_id: str,
        db: AsyncSession,
        model_id: Optional[str] = None,
    ) -> tuple[bytes, VoiceSettings]:
        """
        Generate TTS with automatic voice settings application

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier
            db: Database session
            model_id: Optional ElevenLabs model override

        Returns:
            tuple: (audio_bytes, voice_settings_used)

        Raises:
            ValueError: If voice not found or inactive
        """
        # Get voice configuration
        voice = await self.get_voice_with_settings(voice_id, db)

        if not voice:
            raise ValueError(f"Voice '{voice_id}' not found")

        if not voice.active:
            raise ValueError(f"Voice '{voice_id}' is inactive")

        # Get settings for ElevenLabs
        voice_settings = self.get_elevenlabs_settings(voice)

        logger.info(
            f"🎙️ Generating TTS with voice '{voice.name}' "
            f"(elevenlabs_id={voice.elevenlabs_id})"
        )

        # Generate audio with ElevenLabs
        audio_bytes = await elevenlabs_service.generate_speech(
            text=text,
            voice_id=voice.elevenlabs_id,
            voice_settings=voice_settings,
            model_id=model_id,
        )

        logger.info(
            f"✅ TTS generated successfully with voice '{voice.name}', "
            f"size={len(audio_bytes)} bytes"
        )

        return audio_bytes, voice

    def get_voice_settings_snapshot(self, voice: VoiceSettings) -> str:
        """
        Create a JSON snapshot of voice settings for storage

        Args:
            voice: VoiceSettings object

        Returns:
            str: JSON string with settings snapshot
        """
        snapshot = {
            "voice_id": voice.id,
            "voice_name": voice.name,
            "elevenlabs_id": voice.elevenlabs_id,
            "style": voice.style,
            "stability": voice.stability,
            "similarity_boost": voice.similarity_boost,
            "use_speaker_boost": voice.use_speaker_boost,
            "speed": voice.speed,  # ElevenLabs 2025
            "volume_adjustment": voice.volume_adjustment,
            "jingle_settings": voice.jingle_settings,
        }

        return json.dumps(snapshot)

    async def create_voice(self, db: AsyncSession, voice_data: Dict) -> VoiceSettings:
        """
        Create a new voice configuration

        Args:
            db: Database session
            voice_data: Voice configuration data

        Returns:
            VoiceSettings: Created voice
        """
        voice = VoiceSettings(**voice_data)
        db.add(voice)
        await db.commit()
        await db.refresh(voice)

        # Update cache
        self._cache[voice.id] = voice

        logger.info(f"✅ Created new voice: {voice.name} (id={voice.id})")
        return voice

    async def update_voice(
        self, db: AsyncSession, voice_id: str, voice_data: Dict
    ) -> Optional[VoiceSettings]:
        """
        Update voice configuration

        Args:
            db: Database session
            voice_id: Voice identifier
            voice_data: Updated configuration data

        Returns:
            VoiceSettings: Updated voice or None
        """
        result = await db.execute(
            select(VoiceSettings).filter(VoiceSettings.id == voice_id)
        )
        voice = result.scalar_one_or_none()

        if not voice:
            logger.warning(f"⚠️ Voice '{voice_id}' not found for update")
            return None

        # Update fields
        for key, value in voice_data.items():
            if hasattr(voice, key):
                setattr(voice, key, value)

        await db.commit()
        await db.refresh(voice)

        # Invalidate cache
        if voice_id in self._cache:
            del self._cache[voice_id]

        logger.info(f"✅ Updated voice: {voice.name} (id={voice_id})")
        return voice

    def invalidate_cache(self, voice_id: Optional[str] = None):
        """
        Invalidate voice cache

        Args:
            voice_id: Specific voice to invalidate, or None for all
        """
        if voice_id:
            self._cache.pop(voice_id, None)
            logger.debug(f"🗑️ Cache invalidated for voice: {voice_id}")
        else:
            self._cache.clear()
            logger.debug("🗑️ All voice cache cleared")


# Singleton instance
voice_manager = VoiceManager()
