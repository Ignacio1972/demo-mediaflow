"""
ElevenLabs TTS Service
Handles text-to-speech generation with ElevenLabs API
"""
import httpx
import logging
from typing import Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for ElevenLabs TTS API integration"""

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.model_id = settings.ELEVENLABS_MODEL_ID
        self.base_url = settings.ELEVENLABS_BASE_URL
        self.timeout = 60.0  # 60 seconds for TTS generation

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        voice_settings: Optional[Dict[str, float]] = None,
        model_id: Optional[str] = None,
    ) -> bytes:
        """
        Generate speech audio from text using ElevenLabs API

        Args:
            text: The text to convert to speech
            voice_id: ElevenLabs voice ID (e.g., 'G4IAP30yc6c1gK0csDfu')
            voice_settings: Voice configuration with style, stability, similarity_boost
            model_id: Optional ElevenLabs model (defaults to ELEVENLABS_MODEL_ID)

        Returns:
            bytes: MP3 audio data

        Raises:
            httpx.HTTPError: If API request fails
        """
        # Default voice settings if not provided
        # ElevenLabs 2025 recommended defaults
        if not voice_settings:
            voice_settings = {
                "stability": 0.5,  # 50% for natural speech
                "similarity_boost": 0.75,  # 75% for clarity
                "style": 0.0,  # 0% recommended
                "use_speaker_boost": True,
                "speed": 1.0,  # Normal speed
            }
        else:
            # Convert from percentage (0-100) to decimal (0-1) if needed
            voice_settings = self._normalize_voice_settings(voice_settings)

        # Prepare API payload
        # ElevenLabs 2025 API: voice_settings now includes speed parameter
        # Use provided model_id or fall back to default
        effective_model = model_id or self.model_id
        payload = {
            "text": text,
            "model_id": effective_model,
            "voice_settings": {
                "stability": voice_settings.get("stability", 0.5),
                "similarity_boost": voice_settings.get("similarity_boost", 0.75),
                "style": voice_settings.get("style", 0.0),
                "use_speaker_boost": voice_settings.get("use_speaker_boost", True),
                "speed": voice_settings.get("speed", 1.0),  # ElevenLabs 2025
            },
        }

        logger.info(f"🎙️ Generating TTS: voice_id={voice_id}, model={effective_model}, text_length={len(text)}")
        logger.debug(f"Voice settings: {payload['voice_settings']}")

        # Make API request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                json=payload,
                headers={"xi-api-key": self.api_key},
            )

            # Check for errors
            if response.status_code != 200:
                error_msg = f"ElevenLabs API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                response.raise_for_status()

            audio_bytes = response.content
            logger.info(f"✅ TTS generated successfully, size={len(audio_bytes)} bytes")

            return audio_bytes

    async def get_available_voices(self) -> list:
        """
        Fetch available voices from ElevenLabs API

        Returns:
            list: List of available voices with metadata
        """
        logger.info("📋 Fetching available voices from ElevenLabs")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key},
            )

            response.raise_for_status()
            data = response.json()

            voices = data.get("voices", [])
            logger.info(f"✅ Retrieved {len(voices)} voices from ElevenLabs")

            return voices

    async def get_voice_info(self, voice_id: str) -> Dict:
        """
        Get information about a specific voice

        Args:
            voice_id: ElevenLabs voice ID

        Returns:
            dict: Voice metadata
        """
        logger.info(f"🔍 Fetching info for voice_id={voice_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/voices/{voice_id}",
                headers={"xi-api-key": self.api_key},
            )

            response.raise_for_status()
            voice_data = response.json()

            logger.info(f"✅ Retrieved info for voice: {voice_data.get('name', 'Unknown')}")

            return voice_data

    def _normalize_voice_settings(self, settings: Dict) -> Dict:
        """
        Normalize voice settings from percentage (0-100) to decimal (0-1)
        Note: speed is NOT normalized (already in 0.7-1.2 range)

        Args:
            settings: Voice settings dict

        Returns:
            dict: Normalized settings
        """
        normalized = {}

        for key, value in settings.items():
            if key in ["style", "stability", "similarity_boost"]:
                # Convert from 0-100 to 0-1 if value is > 1
                if isinstance(value, (int, float)) and value > 1:
                    normalized[key] = value / 100.0
                else:
                    normalized[key] = value
            elif key == "speed":
                # Speed is already in correct range (0.7-1.2), don't normalize
                # Just ensure it's within valid bounds
                normalized[key] = max(0.7, min(1.2, float(value)))
            else:
                normalized[key] = value

        return normalized


# Singleton instance
elevenlabs_service = ElevenLabsService()
