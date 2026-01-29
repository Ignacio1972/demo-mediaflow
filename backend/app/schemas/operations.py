"""
Operations API Schemas
Pydantic models for operations module - vehicle announcements and templates
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


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
    template: str = Field(
        "default",
        description="Template ID to use (from database or hardcoded)"
    )
    number_mode: NumberMode = Field(
        NumberMode.WORDS,
        description="How to pronounce plate numbers"
    )
    use_announcement_sound: Optional[bool] = Field(
        None,
        description="Override template's announcement sound setting. If None, uses template default."
    )
    custom_text: Optional[str] = Field(
        None,
        description="Custom text to use instead of generating from template. Used for regeneration with edited text."
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
    template: str = Field("default", description="Template ID to use")
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
    use_announcement_sound: bool = Field(
        False,
        description="Whether this template uses intro/outro announcement sounds"
    )


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
    is_default: bool = False


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
    tts_name: Optional[str] = None  # Accented version for TTS pronunciation


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
    default_template_id: Optional[str] = None
    default_voice_id: Optional[str] = None


# ============================================
# Schedule Announcement Schemas
# ============================================

class ScheduleType(str, Enum):
    """Type of schedule announcement."""
    OPENING = "opening"    # Apertura
    CLOSING = "closing"    # Cierre


class ScheduleVariant(str, Enum):
    """Variant of the announcement."""
    NORMAL = "normal"           # Standard message
    IN_MINUTES = "in_minutes"   # "Cerrará en X minutos"
    IMMEDIATE = "immediate"     # "Ha cerrado" / "Está abierto"


class ScheduleAnnouncementRequest(BaseModel):
    """Request schema for generating a schedule announcement."""
    schedule_type: ScheduleType = Field(
        ...,
        description="Type: opening or closing"
    )
    variant: ScheduleVariant = Field(
        ScheduleVariant.NORMAL,
        description="Message variant"
    )
    minutes: Optional[int] = Field(
        None,
        ge=5,
        le=60,
        description="Minutes until closing (only for in_minutes variant)"
    )
    voice_id: str = Field(
        ...,
        description="Voice ID for TTS generation"
    )
    music_file: Optional[str] = Field(
        None,
        description="Background music filename (optional)"
    )
    use_announcement_sound: Optional[bool] = Field(
        None,
        description="Override template's announcement sound setting. If None, uses template default."
    )


class SchedulePreviewRequest(BaseModel):
    """Request schema for previewing schedule announcement text."""
    schedule_type: ScheduleType
    variant: ScheduleVariant = ScheduleVariant.NORMAL
    minutes: Optional[int] = Field(None, ge=5, le=60)


class SchedulePreviewResponse(BaseModel):
    """Response schema for schedule text preview."""
    text: str = Field(..., description="The announcement text")
    schedule_type: str
    variant: str
    minutes: Optional[int] = None
    use_announcement_sound: bool = Field(
        False,
        description="Whether this template uses intro/outro announcement sounds"
    )


class ScheduleAnnouncementResponse(BaseModel):
    """Response schema for schedule announcement generation."""
    success: bool
    text: str = Field(..., description="The announcement text")
    audio_url: str = Field(..., description="URL to the generated audio file")
    audio_id: int = Field(..., description="Database ID of the audio message")
    filename: str
    duration: Optional[float] = None
    voice_id: str
    voice_name: str
    schedule_type: str
    variant: str
    error: Optional[str] = None


class MinutesOption(BaseModel):
    """Minutes option for the form."""
    value: int
    label: str


class ScheduleOptionsResponse(BaseModel):
    """Response with options for the schedule form."""
    types: List[dict]  # [{id, name}]
    variants: List[dict]  # [{id, name, description}]
    minutes_options: List[MinutesOption]
    default_voice_id: Optional[str] = None


# ============================================
# Employee/Client Call Schemas
# ============================================

class CallType(str, Enum):
    """Type of person being called."""
    EMPLEADO = "empleado"
    CLIENTE = "cliente"


class LocationOption(BaseModel):
    """Predefined location option."""
    id: str
    name: str


class EmployeeCallRequest(BaseModel):
    """Request schema for generating an employee/client call announcement."""
    call_type: CallType = Field(
        ...,
        description="Type of call: employee or client"
    )
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the person being called"
    )
    ubicacion: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Location where they should go"
    )
    voice_id: str = Field(
        ...,
        description="Voice ID for TTS generation"
    )
    template: str = Field(
        "employee_call_default",
        description="Template ID to use"
    )
    use_announcement_sound: Optional[bool] = Field(
        None,
        description="Override template's announcement sound setting"
    )
    custom_text: Optional[str] = Field(
        None,
        description="Custom text for regeneration"
    )


class EmployeeCallPreviewRequest(BaseModel):
    """Request schema for previewing employee call text."""
    call_type: CallType
    nombre: str = Field(..., min_length=2, max_length=100)
    ubicacion: str = Field(..., min_length=2, max_length=100)
    template: str = Field("employee_call_default")


class EmployeeCallPreviewResponse(BaseModel):
    """Response schema for employee call text preview."""
    original: str = Field(..., description="The announcement text")
    call_type: str
    nombre: str
    ubicacion: str
    use_announcement_sound: bool = Field(
        False,
        description="Whether this template uses intro/outro announcement sounds"
    )


class EmployeeCallResponse(BaseModel):
    """Response schema for employee call announcement generation."""
    success: bool
    text: str = Field(..., description="The announcement text")
    audio_url: str = Field(..., description="URL to the generated audio file")
    audio_id: int = Field(..., description="Database ID of the audio message")
    filename: str
    duration: Optional[float] = None
    voice_id: str
    voice_name: str
    call_type: str
    error: Optional[str] = None


class EmployeeCallOptionsResponse(BaseModel):
    """Response with options for the employee call form."""
    call_types: List[dict]  # [{id, name}]
    locations: List[LocationOption]
    templates: List[TemplateInfo]
    default_template_id: Optional[str] = None
    default_voice_id: Optional[str] = None
