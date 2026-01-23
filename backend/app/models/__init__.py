"""
Models Package
Import all models here to ensure relationships are resolved
"""
from app.db.base import Base
from app.models.voice_settings import VoiceSettings
from app.models.category import Category
from app.models.audio import AudioMessage
from app.models.schedule import Schedule, ScheduleLog
from app.models.player import PlayerStatus
from app.models.client_config import ClientConfig
from app.models.music_track import MusicTrack
from app.models.ai_client import AIClient
from app.models.message_template import MessageTemplate
from app.models.shortcut import Shortcut

__all__ = [
    "Base",
    "VoiceSettings",
    "Category",
    "AudioMessage",
    "Schedule",
    "ScheduleLog",
    "PlayerStatus",
    "ClientConfig",
    "MusicTrack",
    "AIClient",
    "MessageTemplate",
    "Shortcut",
]
