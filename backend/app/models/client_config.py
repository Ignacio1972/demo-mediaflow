from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from app.db.base import Base, TimestampMixin


class ClientConfig(Base, TimestampMixin):
    """Multi-client AI context configuration"""
    __tablename__ = "client_configs"

    id = Column(String(50), primary_key=True)  # e.g., 'mall_costanera'
    name = Column(String(100), nullable=False)  # e.g., 'Mall Costanera'
    description = Column(String(500), nullable=True)

    # AI Context
    context = Column(Text, nullable=False)  # Main context for Claude
    tone = Column(String(50), default="professional")  # professional, friendly, casual
    max_words = Column(Integer, default=30)

    # Settings
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Additional metadata
    extra_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ClientConfig {self.name} ({self.id})>"
