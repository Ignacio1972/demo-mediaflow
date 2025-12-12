"""
Message Template API Schemas
Pydantic models for message template management - v2.1
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class TemplateBase(BaseModel):
    """Base schema for template data"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for the template",
        examples=["Vehiculos - Estandar", "Nino Perdido - Urgente"],
    )

    description: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Brief description of when to use this template",
        examples=["Solicita acercarse a informaciones en Planta Baja"],
    )

    template_text: str = Field(
        ...,
        min_length=10,
        description="The template text with {placeholders}",
        examples=["Atencion: El vehiculo {marca} color {color}, patente {patente}..."],
    )

    variables: List[str] = Field(
        default_factory=list,
        description="List of variable names used in the template",
        examples=[["marca", "color", "patente"]],
    )

    module: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Module this template belongs to",
        examples=["vehicles", "lost_child", "promotions"],
    )

    active: bool = Field(
        default=True,
        description="Whether template is available for use",
    )

    is_default: bool = Field(
        default=False,
        description="Whether this is the default template for its module",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Clean and validate name"""
        return v.strip()

    @field_validator("template_text")
    @classmethod
    def validate_template_text(cls, v: str) -> str:
        """Clean template text"""
        return v.strip()

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: str) -> str:
        """Validate module name"""
        return v.strip().lower()


class TemplateCreate(TemplateBase):
    """Schema for creating a new template"""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^[a-z0-9_]+$',
        description="Unique identifier (lowercase, underscores allowed)",
        examples=["vehiculos_estandar", "nino_perdido_urgente"],
    )

    order: Optional[int] = Field(
        default=None,
        ge=0,
        description="Display order (auto-assigned if not provided)",
    )


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template"""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Display name for the template",
    )

    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Brief description",
    )

    template_text: Optional[str] = Field(
        None,
        min_length=10,
        description="The template text with {placeholders}",
    )

    variables: Optional[List[str]] = Field(
        None,
        description="List of variable names",
    )

    module: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Module this template belongs to",
    )

    active: Optional[bool] = Field(
        None,
        description="Whether template is available",
    )

    is_default: Optional[bool] = Field(
        None,
        description="Whether this is the default for its module",
    )

    order: Optional[int] = Field(
        None,
        ge=0,
        description="Display order",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Clean and validate name"""
        return v.strip() if v else v

    @field_validator("template_text")
    @classmethod
    def validate_template_text(cls, v: Optional[str]) -> Optional[str]:
        """Clean template text"""
        return v.strip() if v else v

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: Optional[str]) -> Optional[str]:
        """Validate module name"""
        return v.strip().lower() if v else v


class TemplateResponse(BaseModel):
    """Response schema for template"""

    id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Brief description")
    template_text: str = Field(..., description="Template with placeholders")
    variables: List[str] = Field(..., description="Variable names")
    module: str = Field(..., description="Module name")
    order: int = Field(..., description="Display order")
    active: bool = Field(..., description="Is active")
    is_default: bool = Field(..., description="Is default for module")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "vehiculos_estandar",
                "name": "Vehiculos - Estandar",
                "description": "Solicita acercarse a informaciones en Planta Baja",
                "template_text": "Atencion clientes: Se solicita al dueno del vehiculo...",
                "variables": ["marca", "color", "patente"],
                "module": "vehicles",
                "order": 0,
                "active": True,
                "is_default": True,
                "created_at": "2024-12-12T10:00:00",
                "updated_at": "2024-12-12T10:00:00",
            }
        }


class TemplateReorderRequest(BaseModel):
    """Request schema for reordering templates"""

    template_ids: List[str] = Field(
        ...,
        min_length=1,
        description="Ordered list of template IDs",
        examples=[["vehiculos_estandar", "vehiculos_formal", "vehiculos_urgente"]],
    )


class TemplateListResponse(BaseModel):
    """Response schema for template list"""

    templates: List[TemplateResponse] = Field(
        ...,
        description="List of templates",
    )
    total: int = Field(..., description="Total number of templates")


class TemplatePreviewRequest(BaseModel):
    """Request to preview a template with variables"""

    template_text: str = Field(..., description="Template text to preview")
    variables: dict = Field(
        default_factory=dict,
        description="Variable values for preview",
        examples=[{"marca": "Toyota", "color": "rojo", "patente": "BBCL-45"}],
    )


class TemplatePreviewResponse(BaseModel):
    """Response for template preview"""

    original: str = Field(..., description="Original template text")
    rendered: str = Field(..., description="Template with variables replaced")
    missing_variables: List[str] = Field(
        default_factory=list,
        description="Variables in template not provided in request",
    )
