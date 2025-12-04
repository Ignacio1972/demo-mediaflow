"""
Voice Serializer
Converts VoiceSettings model to API response format
"""
from typing import Dict, Any
from app.models.voice_settings import VoiceSettings


def serialize_voice(voice: VoiceSettings) -> Dict[str, Any]:
    """
    Serialize a VoiceSettings model to a dictionary for API response.

    Args:
        voice: VoiceSettings model instance

    Returns:
        Dictionary with voice data formatted for API response
    """
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
