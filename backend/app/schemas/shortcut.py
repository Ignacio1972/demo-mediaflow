"""
Shortcut API Schemas
Pydantic models for shortcut management
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AudioMessageInfo(BaseModel):
    """Nested audio message info for shortcut responses"""
    id: int
    filename: str
    display_name: str
    duration: Optional[float] = None
    audio_url: str

    class Config:
        from_attributes = True


class ShortcutCreate(BaseModel):
    """Schema for creating a new shortcut"""
    audio_message_id: int = Field(..., description="ID of the audio message to link")
    custom_name: str = Field(..., min_length=1, max_length=50)
    custom_icon: Optional[str] = Field(None, max_length=10, description="Emoji icon")
    custom_color: Optional[str] = Field(
        None,
        pattern=r'^#[0-9A-Fa-f]{6}$',
        description="Hex color e.g. #10B981"
    )
    position: Optional[int] = Field(None, ge=1, le=6, description="Slot position 1-6")


class ShortcutUpdate(BaseModel):
    """Schema for updating an existing shortcut"""
    custom_name: Optional[str] = Field(None, min_length=1, max_length=50)
    custom_icon: Optional[str] = Field(None, max_length=10)
    custom_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    position: Optional[int] = Field(None, ge=1, le=6)
    active: Optional[bool] = None


class ShortcutResponse(BaseModel):
    """Response schema for a shortcut"""
    id: int
    audio_message_id: int
    custom_name: str
    custom_icon: Optional[str] = None
    custom_color: Optional[str] = None
    position: Optional[int] = None
    active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    audio_message: Optional[AudioMessageInfo] = None

    class Config:
        from_attributes = True


class ShortcutPositionUpdate(BaseModel):
    """Schema for assigning/removing position"""
    position: Optional[int] = Field(None, ge=1, le=6, description="Slot 1-6 or null to remove")
