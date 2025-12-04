"""
Category Settings API Endpoints
Handles category management for Category Editor - v2.1 Playground
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db.session import get_db
from app.models.category import Category
from app.models.audio import AudioMessage
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryReorderRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="Get All Categories",
    description="Get all categories for the Category Editor (includes inactive)",
)
async def get_all_categories_settings(
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get all categories for settings management"""
    try:
        logger.info("📂 Fetching all categories for settings")

        query = select(Category).order_by(Category.order.asc())
        if not include_inactive:
            query = query.filter(Category.active == True)

        result = await db.execute(query)
        categories = result.scalars().all()

        # Get message counts for each category
        response_list = []
        for cat in categories:
            # Count messages in this category
            count_result = await db.execute(
                select(AudioMessage)
                .filter(AudioMessage.category_id == cat.id)
            )
            message_count = len(count_result.scalars().all())

            response_list.append(
                CategoryResponse(
                    id=cat.id,
                    name=cat.name,
                    icon=cat.icon,
                    color=cat.color,
                    order=cat.order,
                    active=cat.active,
                    created_at=cat.created_at,
                    updated_at=cat.updated_at,
                    message_count=message_count,
                )
            )

        logger.info(f"✅ Retrieved {len(categories)} categories")
        return response_list

    except Exception as e:
        logger.error(f"❌ Failed to fetch categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}",
        )


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Get Single Category",
)
async def get_category_settings(
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

        # Get message count
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == cat.id)
        )
        message_count = len(count_result.scalars().all())

        return CategoryResponse(
            id=cat.id,
            name=cat.name,
            icon=cat.icon,
            color=cat.color,
            order=cat.order,
            active=cat.active,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            message_count=message_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}",
        )


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Create a new category for organizing audio messages",
)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new category"""
    try:
        logger.info(f"➕ Creating category: {category_data.id}")

        # Check if ID already exists
        result = await db.execute(
            select(Category).filter(Category.id == category_data.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID '{category_data.id}' already exists",
            )

        # Get next order number if not provided
        order = category_data.order
        if order is None:
            result = await db.execute(select(Category))
            all_categories = result.scalars().all()
            order = max([c.order for c in all_categories], default=-1) + 1

        # Create category
        category = Category(
            id=category_data.id,
            name=category_data.name,
            icon=category_data.icon or "📁",
            color=category_data.color or "#6B7280",
            order=order,
            active=category_data.active,
        )

        db.add(category)
        await db.commit()
        await db.refresh(category)

        logger.info(f"✅ Category created: {category.id}")

        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            color=category.color,
            order=category.order,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            message_count=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}",
        )


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update Category",
    description="Update an existing category",
)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update existing category"""
    try:
        logger.info(f"📝 Updating category: {category_id}")

        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)

        # Get message count
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == category.id)
        )
        message_count = len(count_result.scalars().all())

        logger.info(f"✅ Category updated: {category.id}")

        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            color=category.color,
            order=category.order,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at,
            message_count=message_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}",
        )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="Delete a category (only if it has no associated messages)",
)
async def delete_category(
    category_id: str,
    force: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Delete a category"""
    try:
        logger.info(f"🗑️ Deleting category: {category_id}")

        result = await db.execute(
            select(Category).filter(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found",
            )

        # Check if category has messages
        count_result = await db.execute(
            select(AudioMessage)
            .filter(AudioMessage.category_id == category_id)
        )
        message_count = len(count_result.scalars().all())

        if message_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category '{category.name}' because it has {message_count} associated messages. Set force=true to delete anyway (messages will be uncategorized).",
            )

        # If force delete, uncategorize all messages
        if message_count > 0 and force:
            logger.info(f"⚠️ Force delete: uncategorizing {message_count} messages")
            await db.execute(
                update(AudioMessage)
                .where(AudioMessage.category_id == category_id)
                .values(category_id=None)
            )

        # Delete category
        await db.delete(category)
        await db.commit()

        logger.info(f"✅ Category deleted: {category_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}",
        )


@router.put(
    "/categories/reorder",
    summary="Reorder Categories",
    description="Update the display order of categories",
)
async def reorder_categories(
    request: CategoryReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reorder categories"""
    try:
        logger.info(f"🔄 Reordering categories: {request.category_ids}")

        # Update order for each category
        for index, category_id in enumerate(request.category_ids):
            await db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(order=index)
            )

        await db.commit()

        logger.info("✅ Categories reordered")

        return {"success": True, "message": "Categories reordered successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to reorder categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder categories: {str(e)}",
        )
