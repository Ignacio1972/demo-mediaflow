"""
Category API Schemas
Pydantic models for category management - v2.1
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class CategoryBase(BaseModel):
    """Base schema for category data"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for the category",
        examples=["Pedidos Listos", "Ofertas Especiales"],
    )

    icon: Optional[str] = Field(
        default="📁",
        max_length=10,
        description="Emoji or icon for the category",
        examples=["📦", "🎉", "📢", "🎵"],
    )

    color: Optional[str] = Field(
        default="#6B7280",
        description="Hex color for the category badge",
        examples=["#FF4444", "#00AA00", "#0088FF"],
    )

    active: bool = Field(
        default=True,
        description="Whether category is visible in the app",
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format"""
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Color must be a valid hex color (e.g., #FF4444)")
        return v.upper() if v else "#6B7280"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Clean and validate name"""
        return v.strip()


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^[a-z0-9_]+$',
        description="Unique identifier (lowercase, underscores allowed)",
        examples=["pedidos", "ofertas_especiales", "musica"],
    )

    order: Optional[int] = Field(
        default=None,
        ge=0,
        description="Display order (auto-assigned if not provided)",
    )


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category"""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Display name for the category",
    )

    icon: Optional[str] = Field(
        None,
        max_length=10,
        description="Emoji or icon for the category",
    )

    color: Optional[str] = Field(
        None,
        description="Hex color for the category badge",
    )

    active: Optional[bool] = Field(
        None,
        description="Whether category is visible",
    )

    order: Optional[int] = Field(
        None,
        ge=0,
        description="Display order",
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color format"""
        if v is None:
            return v
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Color must be a valid hex color (e.g., #FF4444)")
        return v.upper()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Clean and validate name"""
        return v.strip() if v else v


class CategoryResponse(BaseModel):
    """Response schema for category"""

    id: str = Field(..., description="Category identifier")
    name: str = Field(..., description="Display name")
    icon: Optional[str] = Field(None, description="Emoji/icon")
    color: Optional[str] = Field(None, description="Hex color")
    order: int = Field(..., description="Display order")
    active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Statistics (optional, for editor view)
    message_count: Optional[int] = Field(
        None,
        description="Number of messages using this category",
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "pedidos",
                "name": "Pedidos Listos",
                "icon": "📦",
                "color": "#FF4444",
                "order": 1,
                "active": True,
                "created_at": "2024-11-22T10:00:00",
                "updated_at": "2024-11-22T10:00:00",
                "message_count": 42,
            }
        }


class CategoryReorderRequest(BaseModel):
    """Request schema for reordering categories"""

    category_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Ordered list of category IDs",
        examples=[["pedidos", "ofertas", "avisos", "musica"]],
    )


class CategoryListResponse(BaseModel):
    """Response schema for category list"""

    categories: list[CategoryResponse] = Field(
        ...,
        description="List of categories",
    )
    total: int = Field(..., description="Total number of categories")
