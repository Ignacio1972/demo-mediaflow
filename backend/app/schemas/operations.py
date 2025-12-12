"""
Operations API Schemas
Pydantic models for operations module - vehicle announcements and templates
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AnnouncementTemplate(str, Enum):
    """Available announcement templates."""
    DEFAULT = "default"
    FORMAL = "formal"
    URGENTE = "urgente"
    AMABLE = "amable"


class NumberMode(str, Enum):
    """Number pronunciation modes for license plates."""
    WORDS = "words"      # 45 -> "cuarenta y cinco"
    DIGITS = "digits"    # 45 -> "cuatro cinco"


# ============================================
# Vehicle Announcement Schemas
# ============================================

class VehicleAnnouncementRequest(BaseModel):
    """Request schema for generating a vehicle announcement."""
    marca: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Vehicle brand (e.g., Toyota, Chevrolet)"
    )
    color: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="Vehicle color (e.g., rojo, azul)"
    )
    patente: str = Field(
        ...,
        min_length=4,
        max_length=10,
        description="License plate (e.g., BBCL-45)"
    )
    voice_id: str = Field(
        ...,
        description="Voice ID for TTS generation"
    )
    music_file: Optional[str] = Field(
        None,
        description="Background music filename (optional)"
    )
    template: AnnouncementTemplate = Field(
        AnnouncementTemplate.DEFAULT,
        description="Message template to use"
    )
    number_mode: NumberMode = Field(
        NumberMode.WORDS,
        description="How to pronounce plate numbers"
    )


class PlateInfo(BaseModel):
    """License plate validation info."""
    valid: bool
    format: Optional[str] = None
    letters: Optional[str] = None
    numbers: Optional[str] = None
    normalized: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None


class AnnouncementComponents(BaseModel):
    """Components of the vehicle announcement."""
    marca: str
    color: str
    patente_original: str
    patente_normalized: str


class VehicleAnnouncementResponse(BaseModel):
    """Response schema for vehicle announcement generation."""
    success: bool
    original_text: str = Field(
        ...,
        description="Text before normalization (with raw plate)"
    )
    normalized_text: str = Field(
        ...,
        description="Text normalized for TTS (with spelled-out plate)"
    )
    audio_url: str = Field(
        ...,
        description="URL to the generated audio file"
    )
    audio_id: int = Field(
        ...,
        description="Database ID of the audio message"
    )
    filename: str
    duration: Optional[float] = None
    voice_id: str
    voice_name: str
    template_used: str
    plate_info: PlateInfo
    error: Optional[str] = None


# ============================================
# Text Preview Schemas
# ============================================

class TextPreviewRequest(BaseModel):
    """Request schema for previewing normalized text."""
    marca: str = Field(..., min_length=2, max_length=50)
    color: str = Field(..., min_length=2, max_length=30)
    patente: str = Field(..., min_length=1, max_length=10)
    template: AnnouncementTemplate = Field(AnnouncementTemplate.DEFAULT)
    number_mode: NumberMode = Field(NumberMode.WORDS)


class TextPreviewResponse(BaseModel):
    """Response schema for text preview."""
    original: str = Field(
        ...,
        description="Original text with raw plate"
    )
    normalized: str = Field(
        ...,
        description="Normalized text for TTS pronunciation"
    )
    plate_info: PlateInfo
    components: AnnouncementComponents


# ============================================
# Plate Validation Schemas
# ============================================

class PlateValidationRequest(BaseModel):
    """Request schema for validating a license plate."""
    patente: str = Field(..., min_length=1, max_length=10)


class PlateValidationResponse(BaseModel):
    """Response schema for plate validation."""
    valid: bool
    format: Optional[str] = None
    letters: Optional[str] = None
    numbers: Optional[str] = None
    normalized: Optional[str] = None
    pronunciation: Optional[str] = Field(
        None,
        description="How the plate will be pronounced"
    )
    warning: Optional[str] = None
    error: Optional[str] = None


# ============================================
# Template Schemas
# ============================================

class TemplateInfo(BaseModel):
    """Information about an announcement template."""
    id: str
    name: str
    description: str


class TemplatesResponse(BaseModel):
    """Response schema for listing templates."""
    templates: List[TemplateInfo]


# ============================================
# Common Options Schemas
# ============================================

class VehicleBrand(BaseModel):
    """Vehicle brand suggestion."""
    id: str
    name: str


class VehicleColor(BaseModel):
    """Vehicle color option."""
    id: str
    name: str
    hex_color: Optional[str] = None


class OperationsOptionsResponse(BaseModel):
    """Response with common options for the form."""
    brands: List[VehicleBrand]
    colors: List[VehicleColor]
    templates: List[TemplateInfo]
