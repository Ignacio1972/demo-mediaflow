"""
Categories API Endpoints
Handles category management for library organization - v2.1
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.category import Category

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    summary="Get All Categories",
    description="Get all active categories ordered by order field",
)
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active categories for library organization.

    Returns categories ordered by the 'order' field.
    """
    try:
        logger.info("📂 Fetching categories")

        result = await db.execute(
            select(Category)
            .filter(Category.active == True)
            .order_by(Category.order.asc())
        )
        categories = result.scalars().all()

        logger.info(f"✅ Retrieved {len(categories)} categories")

        return [
            {
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "order": cat.order,
                "active": cat.active,
            }
            for cat in categories
        ]

    except Exception as e:
        logger.error(f"❌ Failed to fetch categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}",
        )


@router.get(
    "/{category_id}",
    summary="Get Category by ID",
    description="Get a single category by its ID",
)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single category by ID"""
    try:
        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        cat = result.scalar_one_or_none()

        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        return {
            "id": cat.id,
            "name": cat.name,
            "icon": cat.icon,
            "color": cat.color,
            "order": cat.order,
            "active": cat.active,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}",
        )
