from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Dynamic categories configuration - v2.1"""
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)  # e.g., 'pedidos'
    name = Column(String(100), nullable=False)  # e.g., 'Pedidos Listos'
    icon = Column(String(50), nullable=True)  # Emoji or icon class
    color = Column(String(7), nullable=True)  # Hex color e.g., '#FF4444'
    order = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Category {self.name} ({self.id})>"
