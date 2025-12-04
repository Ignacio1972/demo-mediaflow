"""
Voice API Schemas
Pydantic models for voice management - v2.1 Playground
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JingleSettingsSchema(BaseModel):
    """Voice-specific jingle settings"""
    music_volume: float = Field(1.0, ge=0, le=5)
    voice_volume: float = Field(1.0, ge=0, le=5)
    duck_level: float = Field(0.2, ge=0, le=1)
    intro_silence: float = Field(3, ge=0, le=15)
    outro_silence: float = Field(5, ge=0, le=20)


class VoiceSettingsCreate(BaseModel):
    """Schema for creating a new voice"""
    id: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9_]+$')
    name: str = Field(..., min_length=1, max_length=100)
    elevenlabs_id: str = Field(..., min_length=1)
    gender: Optional[str] = Field(None, pattern=r'^[MF]?$')
    description: Optional[str] = None
    active: bool = True
    is_default: bool = False
    style: float = Field(50.0, ge=0, le=100)
    stability: float = Field(55.0, ge=0, le=100)
    similarity_boost: float = Field(80.0, ge=0, le=100)
    use_speaker_boost: bool = True
    volume_adjustment: float = Field(0.0, ge=-20, le=20)
    jingle_settings: Optional[JingleSettingsSchema] = None


class VoiceSettingsUpdate(BaseModel):
    """Schema for updating an existing voice"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    elevenlabs_id: Optional[str] = None
    gender: Optional[str] = Field(None, pattern=r'^[MF]?$')
    description: Optional[str] = None
    active: Optional[bool] = None
    is_default: Optional[bool] = None
    style: Optional[float] = Field(None, ge=0, le=100)
    stability: Optional[float] = Field(None, ge=0, le=100)
    similarity_boost: Optional[float] = Field(None, ge=0, le=100)
    use_speaker_boost: Optional[bool] = None
    volume_adjustment: Optional[float] = Field(None, ge=-20, le=20)
    jingle_settings: Optional[dict] = None


class VoiceReorderRequest(BaseModel):
    """Request schema for reordering voices"""
    voice_ids: List[str]


class VoiceTestRequest(BaseModel):
    """Request schema for testing a voice"""
    text: str = Field(..., min_length=1, max_length=500)


class VoiceTestResponse(BaseModel):
    """Response schema for voice test"""
    audio_url: str
    duration: float
    filename: str


class VoiceResponse(BaseModel):
    """Response schema for a voice"""
    id: str
    name: str
    elevenlabs_id: str
    active: bool
    is_default: bool
    order: int
    gender: Optional[str] = None
    accent: Optional[str] = None
    description: Optional[str] = None
    style: float
    stability: float
    similarity_boost: float
    use_speaker_boost: bool
    volume_adjustment: float
    jingle_settings: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
