"""
AI Client API Schemas
Pydantic models for AI client/context management - v2.1
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class AIClientCreate(BaseModel):
    """Schema for creating a new AI client"""
    id: Optional[str] = Field(None, min_length=1, max_length=50, pattern=r'^[a-z0-9_]+$')
    name: str = Field(..., min_length=1, max_length=100)
    context: str = Field(..., min_length=10, max_length=5000)
    category: str = Field(default="general", max_length=50)
    active: bool = True
    settings: Optional[Dict] = None
    custom_prompts: Optional[Dict[str, str]] = None


class AIClientUpdate(BaseModel):
    """Schema for updating an existing AI client"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    context: Optional[str] = Field(None, min_length=10, max_length=5000)
    category: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None
    settings: Optional[Dict] = None
    custom_prompts: Optional[Dict[str, str]] = None


class AIClientReorderRequest(BaseModel):
    """Request schema for reordering AI clients"""
    client_ids: List[str]


class AIClientResponse(BaseModel):
    """Response schema for an AI client"""
    id: str
    name: str
    context: str
    category: str
    active: bool
    is_default: bool
    order: int
    settings: Optional[Dict] = None
    custom_prompts: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class AIClientListResponse(BaseModel):
    """Response schema for listing AI clients"""
    clients: List[AIClientResponse]
    active_client_id: Optional[str] = None
    total: int
