from sqlalchemy import Column, Integer, String, Boolean, Text
from app.db.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Dynamic categories configuration - v2.1

    Also used as Campaigns in the Campaign Manager module.
    The ai_instructions field allows per-category AI training.
    """
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)  # e.g., 'pedidos' or 'navidad'
    name = Column(String(100), nullable=False)  # e.g., 'Pedidos Listos' or 'Navidad 2025'
    icon = Column(String(50), nullable=True)  # Emoji or icon class
    color = Column(String(7), nullable=True)  # Hex color e.g., '#FF4444'
    order = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Campaign Manager: AI training instructions (v2.2)
    ai_instructions = Column(Text, nullable=True)  # Custom instructions for AI generation

    def __repr__(self):
        return f"<Category {self.name} ({self.id})>"
