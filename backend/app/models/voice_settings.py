from sqlalchemy import Column, Integer, String, Boolean, Float, JSON
from app.db.base import Base, TimestampMixin


class VoiceSettings(Base, TimestampMixin):
    """Voice configuration with individual settings - v2.1"""
    __tablename__ = "voice_settings"

    id = Column(String(50), primary_key=True)  # e.g., 'juan_carlos'
    name = Column(String(100), nullable=False)  # e.g., 'Juan Carlos'
    elevenlabs_id = Column(String(100), nullable=False)  # ElevenLabs voice ID

    # Status
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Gender and metadata
    gender = Column(String(1), nullable=True)  # 'M' or 'F'
    accent = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)

    # Voice Settings (individual per voice) - CRITICAL v2.1
    # ElevenLabs 2025 API recommendations:
    # - style: 0% recommended (avoid instability)
    # - stability: ~50% for natural speech (100% = monotone)
    # - similarity_boost: ~75% for voice clarity
    # - speed: 0.7-1.2 range (1.0 = normal)
    style = Column(Float, default=0.0, nullable=False)  # 0-100
    stability = Column(Float, default=50.0, nullable=False)  # 0-100
    similarity_boost = Column(Float, default=75.0, nullable=False)  # 0-100
    use_speaker_boost = Column(Boolean, default=True, nullable=False)
    speed = Column(Float, default=1.0, nullable=False)  # 0.7-1.2 (ElevenLabs 2025)

    # Volume adjustment in dB - CRITICAL v2.1
    volume_adjustment = Column(Float, default=0.0, nullable=False)  # -20 to +20 dB

    # Jingle settings per voice (JSON) - v2.1
    jingle_settings = Column(JSON, nullable=True)
    # Example: {"music_volume": 1.65, "voice_volume": 2.8, "duck_level": 0.95, ...}

    def __repr__(self):
        return f"<VoiceSettings {self.name} (active={self.active})>"
