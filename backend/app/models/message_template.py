"""
Message Template Model
Stores customizable message templates for TTS announcements
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, JSON
from app.db.base import Base, TimestampMixin


class MessageTemplate(Base, TimestampMixin):
    """
    Message templates for various announcement types.

    Templates use placeholders like {marca}, {color}, {patente} that
    get replaced with actual values during text generation.
    """
    __tablename__ = "message_templates"

    id = Column(String(50), primary_key=True)  # e.g., 'vehiculos_default'
    name = Column(String(100), nullable=False)  # e.g., 'Vehiculos - Estandar'
    description = Column(String(255), nullable=True)  # Brief description
    template_text = Column(Text, nullable=False)  # The template with {placeholders}
    variables = Column(JSON, nullable=False, default=list)  # List of variable names
    module = Column(String(50), nullable=False)  # e.g., 'vehicles', 'lost_child'
    order = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Default for this module

    def __repr__(self):
        return f"<MessageTemplate {self.name} ({self.id})>"
