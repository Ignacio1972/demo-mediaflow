"""
AI API Endpoints
Handles AI-powered suggestions and improvements
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.ai.claude import claude_service

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
