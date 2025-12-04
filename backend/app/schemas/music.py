"""
Music Track API Schemas
Pydantic models for music track management - v2.1 Playground
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class MusicTrackResponse(BaseModel):
    """Response schema for a music track"""
    id: int
    filename: str
    display_name: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    bitrate: Optional[str] = None
    is_default: bool
    active: bool
    order: int
    artist: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    audio_url: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class MusicTrackUpdate(BaseModel):
    """Schema for updating a music track"""
    display_name: Optional[str] = None
    is_default: Optional[bool] = None
    active: Optional[bool] = None
    order: Optional[int] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None


class MusicReorderRequest(BaseModel):
    """Request schema for reordering music tracks"""
    track_ids: List[int]
