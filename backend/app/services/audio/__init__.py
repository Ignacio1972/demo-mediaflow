"""
Audio processing services
"""
from app.services.audio.jingle import jingle_service
from app.services.audio.generator import generate_audio

__all__ = ["jingle_service", "generate_audio"]
