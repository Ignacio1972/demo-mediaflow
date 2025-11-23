from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON
from app.db.base import Base, TimestampMixin
from datetime import datetime


class PlayerStatus(Base, TimestampMixin):
    """Player connection and status tracking"""
    __tablename__ = "player_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(100), unique=True, nullable=False)

    # Connection status
    is_online = Column(Boolean, default=False, nullable=False)
    last_heartbeat = Column(DateTime, nullable=True)
    connection_type = Column(String(20), default="http")  # http, websocket

    # Current state
    is_playing_music = Column(Boolean, default=False)
    current_track = Column(String(255), nullable=True)
    music_volume = Column(Float, default=0.3)
    tts_queue_size = Column(Integer, default=0)

    # Metadata
    player_version = Column(String(20), nullable=True)
    ip_address = Column(String(50), nullable=True)
    last_error = Column(String(500), nullable=True)

    @property
    def is_alive(self) -> bool:
        """Check if player is alive based on last heartbeat"""
        if not self.last_heartbeat:
            return False
        age = (datetime.utcnow() - self.last_heartbeat).seconds
        return age < 60  # Offline if >1min without heartbeat

    def __repr__(self):
        return f"<PlayerStatus {self.player_id} (online={self.is_online})>"
