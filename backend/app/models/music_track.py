"""
MusicTrack Model
Stores music tracks for jingle generation - v2.1 Playground
"""
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base, TimestampMixin


class MusicTrack(Base, TimestampMixin):
    """Music tracks available for jingle generation"""
    __tablename__ = "music_tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # File information
    filename = Column(String(255), nullable=False, unique=True)  # "Cool.mp3"
    display_name = Column(String(100), nullable=False)           # "Cool"
    file_path = Column(String(500), nullable=False)

    # Audio metadata
    file_size = Column(Integer, nullable=True)      # bytes
    duration = Column(Float, nullable=True)          # seconds
    bitrate = Column(String(20), nullable=True)      # "320kbps"
    sample_rate = Column(Integer, nullable=True)     # 44100
    format = Column(String(10), default="mp3")

    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Optional metadata
    artist = Column(String(100), nullable=True)
    genre = Column(String(50), nullable=True)
    mood = Column(String(50), nullable=True)  # calm, energetic, happy, etc.

    def __repr__(self):
        return f"<MusicTrack {self.display_name} ({self.filename})>"
