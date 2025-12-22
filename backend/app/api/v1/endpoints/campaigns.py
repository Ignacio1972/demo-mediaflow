"""
Campaigns API Endpoints
Campaign Manager module - uses Categories as campaigns
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.category import Category
from app.models.audio import AudioMessage
from app.schemas.campaign import (
    CampaignResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignListResponse,
    CampaignAudioResponse,
    CampaignAudiosListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


def serialize_campaign(category: Category, audio_count: int) -> CampaignResponse:
    """Convert Category model to CampaignResponse"""
    return CampaignResponse(
        id=category.id,
        name=category.name,
        icon=category.icon,
        color=category.color,
        order=category.order,
        active=category.active,
        ai_instructions=category.ai_instructions,
        audio_count=audio_count,
        has_ai_training=bool(category.ai_instructions),
        created_at=category.created_at,
        updated_at=category.updated_at
    )


def serialize_audio(audio: AudioMessage) -> CampaignAudioResponse:
    """Convert AudioMessage model to CampaignAudioResponse"""
    return CampaignAudioResponse(
        id=audio.id,
        filename=audio.filename,
        display_name=audio.display_name,
        original_text=audio.original_text,
        voice_id=audio.voice_id,
        duration=audio.duration,
        has_jingle=audio.has_jingle,
        music_file=audio.music_file,
        is_favorite=audio.is_favorite,
        status=audio.status,
        audio_url=f"/storage/audio/{audio.filename}",
        created_at=audio.created_at
    )


@router.get("", response_model=CampaignListResponse)
async def get_campaigns(
    db: AsyncSession = Depends(get_db),
    active_only: bool = True
):
    """
    List all campaigns (categories) with audio count.

    Each campaign includes:
    - audio_count: number of associated audios
    - has_ai_training: whether ai_instructions is defined
    """
    query = select(Category)
    if active_only:
        query = query.filter(Category.active == True)
    query = query.order_by(Category.order.asc())

    result = await db.execute(query)
    categories = result.scalars().all()

    campaigns = []
    for cat in categories:
        # Count audios for this category
        count_query = select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == cat.id
        )
        count_result = await db.execute(count_query)
        audio_count = count_result.scalar() or 0

        campaigns.append(serialize_campaign(cat, audio_count))

    logger.info(f"Listed {len(campaigns)} campaigns")
    return CampaignListResponse(campaigns=campaigns, total=len(campaigns))


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a campaign by ID with its audio count."""
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found"
        )

    # Count audios
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id
        )
    )
    audio_count = count_result.scalar() or 0

    return serialize_campaign(category, audio_count)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new campaign.

    This creates a new Category that can be used both as a
    library category and as a campaign.
    """
    # Check if ID already exists
    existing = await db.execute(
        select(Category).filter(Category.id == data.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Campaign with ID '{data.id}' already exists"
        )

    # Create new category
    category = Category(
        id=data.id,
        name=data.name,
        icon=data.icon,
        color=data.color,
        order=data.order,
        active=data.active,
        ai_instructions=data.ai_instructions
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)

    logger.info(f"Created campaign: {category.id}")
    return serialize_campaign(category, audio_count=0)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a campaign.

    All fields are optional. Only provided fields will be updated.
    Use this endpoint to update ai_instructions for AI training.
    """
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found"
        )

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    # Get audio count
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id
        )
    )
    audio_count = count_result.scalar() or 0

    logger.info(f"Updated campaign: {campaign_id}")
    return serialize_campaign(category, audio_count)


@router.get("/{campaign_id}/audios", response_model=CampaignAudiosListResponse)
async def get_campaign_audios(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """List audios belonging to a specific campaign."""
    # Verify campaign exists
    result = await db.execute(
        select(Category).filter(Category.id == campaign_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found"
        )

    # Get audios (exclude deleted)
    query = (
        select(AudioMessage)
        .filter(
            AudioMessage.category_id == campaign_id,
            AudioMessage.status != "deleted"
        )
        .order_by(AudioMessage.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    audios = result.scalars().all()

    # Count total (exclude deleted)
    count_result = await db.execute(
        select(func.count(AudioMessage.id)).filter(
            AudioMessage.category_id == campaign_id,
            AudioMessage.status != "deleted"
        )
    )
    total = count_result.scalar() or 0

    return CampaignAudiosListResponse(
        audios=[serialize_audio(a) for a in audios],
        total=total,
        limit=limit,
        offset=offset
    )
