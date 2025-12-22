"""
Audio API Schemas
Pydantic models for audio generation requests and responses
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime


class AudioGenerateRequest(BaseModel):
    """Request schema for audio generation - v2.1 (simplified)"""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to convert to speech",
        examples=["Atención: El pedido número 42 está listo"],
    )

    voice_id: str = Field(
        ...,
        description="Voice identifier (settings applied automatically)",
        examples=["juan_carlos", "maria", "veronica"],
    )

    # Optional jingle configuration
    add_jingles: bool = Field(
        default=False,
        description="Whether to add intro/outro jingles",
    )

    music_file: Optional[str] = Field(
        default=None,
        description="Music file to use for jingle (optional)",
        examples=["music_01.mp3"],
    )

    # Priority for player queue (1=critical, 5=low)
    priority: int = Field(
        default=4,
        ge=1,
        le=5,
        description="Priority level for player queue",
    )

    # Category ID (optional - for campaign context)
    category_id: Optional[str] = Field(
        default=None,
        description="Category/Campaign ID to assign on generation",
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate and clean text"""
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atención clientes: Oferta especial en el sector de electrónica",
                "voice_id": "juan_carlos",
                "add_jingles": True,
                "music_file": "music_01.mp3",
                "priority": 3,
            }
        }


class AudioGenerateResponse(BaseModel):
    """Response schema for audio generation"""

    audio_id: int = Field(..., description="Audio message ID")
    filename: str = Field(..., description="Generated filename")
    display_name: str = Field(..., description="Display name for the audio")
    audio_url: str = Field(..., description="URL to access the audio file")
    file_size: int = Field(..., description="File size in bytes")
    duration: float = Field(..., description="Audio duration in seconds")
    status: str = Field(..., description="Generation status")

    # Voice information
    voice_id: str = Field(..., description="Voice used for generation")
    voice_name: str = Field(..., description="Voice display name")

    # Settings applied (for reference)
    settings_applied: Dict = Field(
        ..., description="Voice settings that were applied"
    )

    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_id": 123,
                "filename": "tts_20241122_123456.mp3",
                "display_name": "Oferta especial en electrónica",
                "audio_url": "http://localhost:8000/storage/audio/tts_20241122_123456.mp3",
                "file_size": 45678,
                "duration": 5.2,
                "status": "ready",
                "voice_id": "juan_carlos",
                "voice_name": "Juan Carlos",
                "settings_applied": {
                    "style": 15.0,
                    "stability": 100.0,
                    "similarity_boost": 40.0,
                    "volume_adjustment": 0.0,
                },
                "created_at": "2024-11-22T15:30:00",
            }
        }


class VoiceResponse(BaseModel):
    """Response schema for voice information"""

    id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Voice display name")
    elevenlabs_id: str = Field(..., description="ElevenLabs voice ID")
    active: bool = Field(..., description="Whether voice is active")
    is_default: bool = Field(..., description="Whether this is the default voice")
    order: int = Field(..., description="Display order")

    # Metadata
    gender: Optional[str] = Field(None, description="Voice gender (M/F)")
    accent: Optional[str] = Field(None, description="Voice accent")
    description: Optional[str] = Field(None, description="Voice description")

    # Voice settings (for display in UI)
    style: float = Field(..., description="Style setting (0-100)")
    stability: float = Field(..., description="Stability setting (0-100)")
    similarity_boost: float = Field(..., description="Similarity boost (0-100)")
    use_speaker_boost: bool = Field(..., description="Use speaker boost")

    # Volume adjustment
    volume_adjustment: float = Field(..., description="Volume adjustment in dB")

    # Jingle settings (optional)
    jingle_settings: Optional[Dict] = Field(
        None, description="Jingle configuration for this voice"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "juan_carlos",
                "name": "Juan Carlos",
                "elevenlabs_id": "G4IAP30yc6c1gK0csDfu",
                "active": True,
                "is_default": True,
                "order": 1,
                "gender": "M",
                "accent": "Neutral Spanish",
                "description": "Professional male voice",
                "style": 15.0,
                "stability": 100.0,
                "similarity_boost": 40.0,
                "use_speaker_boost": True,
                "volume_adjustment": 0.0,
                "jingle_settings": {
                    "music_volume": 1.65,
                    "voice_volume": 2.8,
                    "duck_level": 0.95,
                },
            }
        }


class AudioMessageResponse(BaseModel):
    """Response schema for audio message (Library)"""

    id: int
    filename: str
    display_name: str
    file_path: str
    file_size: Optional[int]
    duration: Optional[float]
    format: str

    # Content
    original_text: str
    voice_id: str

    # Category (nullable in v2.1)
    category_id: Optional[str]

    # Favorites (v2.1)
    is_favorite: bool

    # Status
    status: str
    sent_to_player: bool
    priority: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AudioListResponse(BaseModel):
    """Response schema for audio list with pagination"""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    items: list[AudioMessageResponse] = Field(..., description="Audio messages")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 20,
                "items": [],
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid voice_id",
                "details": {"voice_id": "Voice 'invalid' not found"},
            }
        }
