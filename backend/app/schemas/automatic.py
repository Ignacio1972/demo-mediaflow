"""
Automatic Mode API Schemas
Pydantic models for automatic jingle generation - v2.1 Playground
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class AutomaticGenerateRequest(BaseModel):
    """Request for automatic jingle generation"""
    text: str = Field(..., min_length=1, max_length=2000, description="Transcribed text or direct input")
    voice_id: str = Field(..., description="Voice ID to use for TTS")
    music_file: Optional[str] = Field(None, description="Music file for jingle (null for no music)")
    target_duration: int = Field(20, ge=5, le=30, description="Target duration in seconds (5, 10, 15, 20, 25)")
    improve_text: bool = Field(True, description="Whether to improve text with AI")


class AutomaticGenerateResponse(BaseModel):
    """Response from automatic jingle generation"""
    success: bool
    original_text: str
    improved_text: str
    voice_used: str
    audio_url: str
    filename: str
    duration: Optional[float] = None
    error: Optional[str] = None
    audio_id: Optional[int] = None


class AutomaticConfigResponse(BaseModel):
    """Response with automatic mode configuration"""
    default_voice_id: Optional[str]
    default_music: Optional[str]
    available_durations: List[int]
    word_limits: Dict[int, Dict[str, int]]
