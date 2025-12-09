"""
AI Client Model - v2.1
Manages AI contexts for different clients/businesses
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON
from app.db.base import Base, TimestampMixin


class AIClient(Base, TimestampMixin):
    """AI Client/Context configuration for Claude API"""
    __tablename__ = "ai_clients"

    id = Column(String(50), primary_key=True)  # e.g., 'supermercado_lider'
    name = Column(String(100), nullable=False)  # Display name
    context = Column(Text, nullable=False)  # System prompt for Claude
    category = Column(String(50), default="general")  # Business type

    # Status
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Additional settings (optional JSON)
    settings = Column(JSON, nullable=True)
    # Example: {"default_tone": "profesional", "language": "es-CL", "max_length": 100}

    # Custom prompts per category (optional JSON)
    custom_prompts = Column(JSON, nullable=True)
    # Example: {"ofertas": "Enfócate en el ahorro...", "eventos": "Destaca la experiencia..."}

    def __repr__(self):
        return f"<AIClient {self.name} (default={self.is_default})>"
