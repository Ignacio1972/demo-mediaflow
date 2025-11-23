from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from datetime import datetime


class Schedule(Base, TimestampMixin):
    """Scheduled audio playback"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference to audio or text to generate
    audio_message_id = Column(Integer, ForeignKey("audio_messages.id"), nullable=True)
    audio_message = relationship("AudioMessage", backref="schedules")

    # Or generate on the fly
    text_to_generate = Column(Text, nullable=True)
    voice_id = Column(String(50), nullable=True)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=True)

    # Schedule type
    schedule_type = Column(String(20), nullable=False)  # interval, specific, once

    # Timing
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    # For interval type
    interval_minutes = Column(Integer, nullable=True)

    # For specific times
    specific_times = Column(JSON, nullable=True)  # ["09:00", "12:00", "15:00"]

    # For days of week
    days_of_week = Column(JSON, nullable=True)  # [0,1,2,3,4] = Mon-Fri

    # Status
    active = Column(Boolean, default=True, nullable=False)
    last_executed_at = Column(DateTime, nullable=True)
    next_execution_at = Column(DateTime, nullable=True)

    # Priority
    priority = Column(Integer, default=4)

    def __repr__(self):
        return f"<Schedule {self.schedule_type} (active={self.active})>"


class ScheduleLog(Base, TimestampMixin):
    """Log of schedule executions"""
    __tablename__ = "schedule_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    schedule = relationship("Schedule", backref="logs")

    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    audio_generated_id = Column(Integer, ForeignKey("audio_messages.id"), nullable=True)

    def __repr__(self):
        return f"<ScheduleLog {self.executed_at} (success={self.success})>"
