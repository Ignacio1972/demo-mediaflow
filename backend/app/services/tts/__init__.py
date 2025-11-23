"""TTS Services"""
from app.services.tts.elevenlabs import elevenlabs_service
from app.services.tts.voice_manager import voice_manager

__all__ = ["elevenlabs_service", "voice_manager"]
