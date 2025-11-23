from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from datetime import datetime


class AudioMessage(Base, TimestampMixin):
    """Audio messages with favorites and category - v2.1"""
    __tablename__ = "audio_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # File information
    filename = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes

    # Audio metadata
    duration = Column(Float, nullable=True)  # seconds
    sample_rate = Column(Integer, nullable=True)
    bitrate = Column(String(20), nullable=True)
    format = Column(String(10), default="mp3")

    # Content
    original_text = Column(Text, nullable=False)
    voice_id = Column(String(50), nullable=False)  # Reference to VoiceSettings

    # Category (nullable - assigned later in Library) - v2.1
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", backref="messages")

    # Favorites - v2.1 NEW
    is_favorite = Column(Boolean, default=False, nullable=False)

    # Generation settings (stored for reference)
    voice_settings_snapshot = Column(Text, nullable=True)  # JSON snapshot
    volume_adjustment = Column(Float, default=0.0)

    # Jingle information
    has_jingle = Column(Boolean, default=False)
    music_file = Column(String(255), nullable=True)

    # Status
    status = Column(String(20), default="ready")  # ready, processing, error

    # Player delivery tracking
    sent_to_player = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)

    # Priority for player queue
    priority = Column(Integer, default=4)  # 1-5 (1=critical, 5=low)

    def __repr__(self):
        return f"<AudioMessage {self.display_name} (favorite={self.is_favorite})>"
