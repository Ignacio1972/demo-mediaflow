from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at to models"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
