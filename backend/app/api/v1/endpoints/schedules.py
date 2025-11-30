"""
Schedules API Endpoints
CRUD operations for audio message scheduling - v2.1
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.schedule import Schedule
from app.models.audio import AudioMessage

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas for request/response
class ScheduleCreateRequest(BaseModel):
    """Request schema for creating a schedule"""
    audio_message_id: int = Field(..., description="ID of the audio message to schedule")
    schedule_type: str = Field(..., description="Type: 'interval', 'specific', or 'once'")

    # For interval type - accept both formats from frontend
    interval_minutes: Optional[int] = Field(None, ge=0, description="Interval in minutes")
    interval_hours: Optional[int] = Field(None, ge=0, description="Interval hours (converted to minutes)")

    # For specific times - accept both field names
    specific_times: Optional[List[str]] = Field(None, description="List of times like ['09:00', '12:00']")
    schedule_times: Optional[List[str]] = Field(None, description="Alias for specific_times")

    # For days of week - accept both field names
    days_of_week: Optional[List[int]] = Field(None, description="Days of week [0-6]")
    schedule_days: Optional[List[int]] = Field(None, description="Alias for days_of_week")

    # For once type
    once_datetime: Optional[str] = Field(None, description="Datetime for once type")

    # Date range - accept string format
    start_date: str = Field(..., description="Start date for the schedule")
    end_date: Optional[str] = Field(None, description="Optional end date")

    # Optional notes
    notes: Optional[str] = Field(None, description="Optional notes")

    # Priority
    priority: int = Field(default=4, ge=1, le=5, description="Priority 1-5")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_message_id": 1,
                "schedule_type": "interval",
                "interval_hours": 4,
                "interval_minutes": 0,
                "schedule_days": [1, 2, 3, 4, 5],
                "schedule_times": ["09:00", "18:00"],
                "start_date": "2025-12-01",
                "priority": 3
            }
        }


class ScheduleResponse(BaseModel):
    """Response schema for schedule"""
    id: int
    audio_message_id: Optional[int]
    schedule_type: str
    interval_minutes: Optional[int]
    specific_times: Optional[List[str]]
    days_of_week: Optional[List[int]]
    start_date: datetime
    end_date: Optional[datetime]
    active: bool
    priority: int
    last_executed_at: Optional[datetime]
    next_execution_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


def schedule_to_dict(schedule: Schedule) -> dict:
    """Convert Schedule model to response dictionary"""
    return {
        "id": schedule.id,
        "audio_message_id": schedule.audio_message_id,
        "schedule_type": schedule.schedule_type,
        "interval_minutes": schedule.interval_minutes,
        "specific_times": schedule.specific_times,
        "days_of_week": schedule.days_of_week,
        "start_date": schedule.start_date.isoformat() if schedule.start_date else None,
        "end_date": schedule.end_date.isoformat() if schedule.end_date else None,
        "active": schedule.active,
        "priority": schedule.priority,
        "last_executed_at": schedule.last_executed_at.isoformat() if schedule.last_executed_at else None,
        "next_execution_at": schedule.next_execution_at.isoformat() if schedule.next_execution_at else None,
        "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
        "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
    }


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime, handling various formats"""
    if not date_str:
        return None
    # Try ISO format first
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    # Try date only format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    raise ValueError(f"Cannot parse date: {date_str}")


@router.post(
    "",
    summary="Create Schedule",
    description="Create a new schedule for an audio message",
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    data: ScheduleCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new schedule for audio playback.

    Schedule types:
    - interval: Play every X minutes
    - specific: Play at specific times on specific days
    - once: Play once at a specific datetime
    """
    try:
        logger.info(f"📅 Create schedule request: audio_id={data.audio_message_id}, type={data.schedule_type}")

        # Validate schedule type
        if data.schedule_type not in ["interval", "specific", "once"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid schedule_type. Must be 'interval', 'specific', or 'once'",
            )

        # Validate audio message exists
        result = await db.execute(
            select(AudioMessage).filter(AudioMessage.id == data.audio_message_id)
        )
        audio_msg = result.scalar_one_or_none()

        if not audio_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio message {data.audio_message_id} not found",
            )

        if audio_msg.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot schedule a deleted audio message",
            )

        # Normalize field names (frontend sends schedule_days/schedule_times)
        days = data.days_of_week or data.schedule_days
        times = data.specific_times or data.schedule_times

        # Calculate total interval in minutes
        total_interval_minutes = (data.interval_hours or 0) * 60 + (data.interval_minutes or 0)

        # Validate required fields based on schedule type
        if data.schedule_type == "interval":
            if total_interval_minutes < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total interval must be at least 1 minute",
                )
        elif data.schedule_type == "specific":
            if not times or not days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="specific_times/schedule_times and days_of_week/schedule_days are required for specific schedule type",
                )
            # Validate days values
            if any(d < 0 or d > 6 for d in days):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="days values must be between 0 and 6",
                )
        # For 'once' type, just start_date is sufficient

        # Parse dates
        try:
            start_dt = parse_date(data.start_date)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        end_dt = None
        if data.end_date:
            try:
                end_dt = parse_date(data.end_date)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

        # Create schedule
        schedule = Schedule(
            audio_message_id=data.audio_message_id,
            schedule_type=data.schedule_type,
            interval_minutes=total_interval_minutes if total_interval_minutes > 0 else None,
            specific_times=times,
            days_of_week=days,
            start_date=start_dt,
            end_date=end_dt,
            priority=data.priority,
            active=True,
        )

        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)

        logger.info(f"✅ Schedule created: ID={schedule.id}")

        return {
            "success": True,
            "data": schedule_to_dict(schedule),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}",
        )


@router.get(
    "",
    summary="List Schedules",
    description="Get all schedules with optional filtering",
)
async def list_schedules(
    audio_message_id: Optional[int] = Query(None, description="Filter by audio message ID"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    schedule_type: Optional[str] = Query(None, description="Filter by schedule type"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all schedules with optional filters.

    Can filter by:
    - audio_message_id: Get schedules for a specific audio
    - active: Get only active or inactive schedules
    - schedule_type: Filter by type (interval, specific, once)
    """
    try:
        logger.info(f"📋 List schedules: audio_id={audio_message_id}, active={active}")

        # Build query
        query = select(Schedule)

        # Apply filters
        if audio_message_id is not None:
            query = query.filter(Schedule.audio_message_id == audio_message_id)

        if active is not None:
            query = query.filter(Schedule.active == active)

        if schedule_type is not None:
            query = query.filter(Schedule.schedule_type == schedule_type)

        # Order by created_at desc
        query = query.order_by(Schedule.created_at.desc())

        result = await db.execute(query)
        schedules = result.scalars().all()

        logger.info(f"✅ Retrieved {len(schedules)} schedules")

        return {
            "success": True,
            "data": [schedule_to_dict(s) for s in schedules],
            "total": len(schedules),
        }

    except Exception as e:
        logger.error(f"❌ Failed to list schedules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}",
        )


@router.get(
    "/{schedule_id}",
    summary="Get Schedule",
    description="Get a single schedule by ID",
)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single schedule by ID"""
    try:
        result = await db.execute(
            select(Schedule).filter(Schedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found",
            )

        return {
            "success": True,
            "data": schedule_to_dict(schedule),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule: {str(e)}",
        )


@router.patch(
    "/{schedule_id}",
    summary="Update Schedule",
    description="Update a schedule's active status or other fields",
)
async def update_schedule(
    schedule_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update a schedule (typically to activate/deactivate)"""
    try:
        logger.info(f"📝 Update schedule: ID={schedule_id}")

        result = await db.execute(
            select(Schedule).filter(Schedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found",
            )

        # Update allowed fields
        allowed_fields = ["active", "priority", "end_date"]
        for field in allowed_fields:
            if field in data:
                setattr(schedule, field, data[field])

        await db.commit()
        await db.refresh(schedule)

        logger.info(f"✅ Schedule updated: ID={schedule_id}")

        return {
            "success": True,
            "data": schedule_to_dict(schedule),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {str(e)}",
        )


@router.delete(
    "/{schedule_id}",
    summary="Delete Schedule",
    description="Delete a schedule",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a schedule permanently"""
    try:
        logger.info(f"🗑️ Delete schedule: ID={schedule_id}")

        result = await db.execute(
            select(Schedule).filter(Schedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found",
            )

        await db.delete(schedule)
        await db.commit()

        logger.info(f"✅ Schedule deleted: ID={schedule_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {str(e)}",
        )
