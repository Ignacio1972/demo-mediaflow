from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Shortcut(Base, TimestampMixin):
    """
    Shortcuts for quick audio playback on mobile.
    Links to AudioMessage with custom display settings.
    Only 6 shortcuts can have a position (1-6) at a time.
    """
    __tablename__ = "shortcuts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Link to audio message (one shortcut per audio)
    audio_message_id = Column(
        Integer,
        ForeignKey("audio_messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    audio_message = relationship("AudioMessage", backref="shortcut")

    # Custom display settings for the button
    custom_name = Column(String(50), nullable=False)
    custom_icon = Column(String(10), nullable=True)  # Emoji
    custom_color = Column(String(7), nullable=True)  # Hex color e.g. #10B981

    # Position in the 6-slot grid (1-6 or NULL for inactive)
    position = Column(Integer, nullable=True)

    # Active status
    active = Column(Boolean, default=True, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('position IS NULL OR (position >= 1 AND position <= 6)', name='position_range'),
    )

    def __repr__(self):
        return f"<Shortcut {self.custom_name} (pos={self.position})>"
