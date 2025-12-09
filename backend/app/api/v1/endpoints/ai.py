"""
AI API Endpoints
Handles AI-powered suggestions and improvements
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.ai.claude import claude_service
from app.services.ai.client_manager import ai_client_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class SuggestionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=200)
    tone: str = Field(default="professional", pattern="^(professional|casual|urgent|friendly)$")
    max_words: int = Field(default=30, ge=10, le=100)
    context: Optional[str] = Field(default=None, max_length=500)


class SuggestionResponse(BaseModel):
    suggestions: List[str]  # Changed to list of suggestions
    prompt: str
    tone: str


class ImproveRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=500)
    tone: Optional[str] = Field(default=None, pattern="^(professional|casual|urgent|friendly)$")
    max_words: Optional[int] = Field(default=None, ge=10, le=100)


class VariationsRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=500)
    count: int = Field(default=3, ge=1, le=5)
    tone: Optional[str] = Field(default=None)


class VariationsResponse(BaseModel):
    variations: List[str]
    original: str


# New announcement generation models
class GenerateAnnouncementsRequest(BaseModel):
    """Request for generating announcement suggestions"""
    context: str = Field(..., min_length=5, max_length=1000, description="Description of the announcement")
    category: str = Field(default="general", description="Announcement category")
    tone: str = Field(default="profesional", description="Message tone")
    duration: int = Field(default=10, ge=5, le=30, description="Duration in seconds")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to include")
    temperature: float = Field(default=0.8, ge=0, le=1, description="Creativity level")
    mode: str = Field(default="normal", pattern="^(normal|automatic)$", description="Generation mode")
    word_limit: Optional[List[int]] = Field(default=None, description="[min, max] words for automatic mode")


class AnnouncementSuggestion(BaseModel):
    """A single announcement suggestion"""
    id: str
    text: str
    char_count: int
    word_count: int
    created_at: str


class GenerateAnnouncementsResponse(BaseModel):
    """Response with generated announcement suggestions"""
    success: bool
    suggestions: List[AnnouncementSuggestion]
    model: str
    active_client_id: Optional[str] = None


@router.post(
    "/suggest",
    response_model=SuggestionResponse,
    summary="Generate AI Suggestions",
    description="Generate multiple text suggestions based on user prompt using Claude AI",
)
async def generate_suggestion(request: SuggestionRequest):
    """
    Generate AI-powered text suggestions

    This endpoint uses Claude AI to generate 2 professional message suggestions
    based on user input and preferences.
    """
    try:
        logger.info(f"🤖 AI suggestion request: {request.prompt[:50]}...")

        # Generate 2 variations of suggestions
        suggestions = await claude_service.generate_multiple_suggestions(
            prompt=request.prompt,
            tone=request.tone,
            max_words=request.max_words,
            context=request.context,
            count=2,
        )

        logger.info(f"✅ Generated {len(suggestions)} suggestions")

        return SuggestionResponse(
            suggestions=suggestions,
            prompt=request.prompt,
            tone=request.tone,
        )

    except Exception as e:
        logger.error(f"❌ Suggestion generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestion: {str(e)}",
        )


@router.post(
    "/improve",
    response_model=dict,
    summary="Improve Text",
    description="Improve existing text using AI",
)
async def improve_text(request: ImproveRequest):
    """Improve existing text while maintaining its message"""
    try:
        logger.info(f"🔧 Improving text: {len(request.text)} chars")

        improved = await claude_service.improve_text(
            text=request.text,
            tone=request.tone,
            max_words=request.max_words,
        )

        return {
            "original": request.text,
            "improved": improved,
            "word_count_before": len(request.text.split()),
            "word_count_after": len(improved.split()),
        }

    except Exception as e:
        logger.error(f"❌ Text improvement failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to improve text: {str(e)}",
        )


@router.post(
    "/variations",
    response_model=VariationsResponse,
    summary="Generate Variations",
    description="Generate multiple variations of a text",
)
async def generate_variations(request: VariationsRequest):
    """Generate multiple variations of a message"""
    try:
        logger.info(
            f"🎲 Generating {request.count} variations of: {request.text[:50]}..."
        )

        variations = await claude_service.generate_variations(
            text=request.text,
            count=request.count,
            tone=request.tone,
        )

        return VariationsResponse(
            variations=variations,
            original=request.text,
        )

    except Exception as e:
        logger.error(f"❌ Variations generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate variations: {str(e)}",
        )


@router.post(
    "/generate",
    response_model=GenerateAnnouncementsResponse,
    summary="Generate Announcements",
    description="Generate announcement suggestions using Claude AI with client context",
)
async def generate_announcements(
    request: GenerateAnnouncementsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate announcement suggestions using Claude AI.

    This endpoint replicates the legacy system functionality:
    - Gets context from the active AI client automatically
    - Generates 2 suggestions in normal mode, 1 in automatic mode
    - Returns metadata for each suggestion (word count, char count)
    """
    try:
        logger.info(f"🤖 Generating announcements: mode={request.mode}, tone={request.tone}")

        # Get active client context
        active_client = await ai_client_manager.get_active_client(db)
        client_context = active_client.context if active_client else None
        active_client_id = active_client.id if active_client else None

        # Generate suggestions
        suggestions = await claude_service.generate_announcements(
            context=request.context,
            category=request.category,
            tone=request.tone,
            duration=request.duration,
            keywords=request.keywords,
            temperature=request.temperature,
            client_context=client_context,
            mode=request.mode,
            word_limit=request.word_limit
        )

        logger.info(f"✅ Generated {len(suggestions)} announcements")

        return GenerateAnnouncementsResponse(
            success=True,
            suggestions=suggestions,
            model=claude_service.model,
            active_client_id=active_client_id
        )

    except Exception as e:
        logger.error(f"❌ Announcement generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate announcements: {str(e)}",
        )
