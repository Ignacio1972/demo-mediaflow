"""
Campaign Schemas
Pydantic models for Campaign Manager API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CampaignResponse(BaseModel):
    """Campaign = Category + audio_count + has_ai_training"""
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int
    active: bool
    ai_instructions: Optional[str] = None

    # Computed fields
    audio_count: int = 0
    has_ai_training: bool = False

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    """For POST /campaigns"""
    id: str = Field(..., min_length=1, max_length=50, pattern="^[a-z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, pattern="^#[0-9A-Fa-f]{6}$")
    order: int = Field(default=0, ge=0)
    active: bool = True
    ai_instructions: Optional[str] = None


class CampaignUpdate(BaseModel):
    """For PATCH /campaigns/:id - all fields optional"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, pattern="^#[0-9A-Fa-f]{6}$")
    order: Optional[int] = Field(default=None, ge=0)
    active: Optional[bool] = None
    ai_instructions: Optional[str] = None


class CampaignListResponse(BaseModel):
    """List of campaigns"""
    campaigns: List[CampaignResponse]
    total: int


class CampaignAudioResponse(BaseModel):
    """Audio message in a campaign"""
    id: int
    filename: str
    display_name: str
    original_text: str
    voice_id: str
    duration: Optional[float] = None
    has_jingle: bool = False
    music_file: Optional[str] = None
    is_favorite: bool = False
    status: str = "ready"
    audio_url: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignAudiosListResponse(BaseModel):
    """List of audios in a campaign"""
    audios: List[CampaignAudioResponse]
    total: int
    limit: int
    offset: int
