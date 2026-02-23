"""
Schedule execution time calculator.

Calculates the next execution time for each schedule type:
- interval: last_executed_at + interval_minutes
- specific: Next day+hour matching days_of_week and specific_times
- once: start_date if not executed, None if already executed

All times stored in DB are naive UTC. The specific_times field contains
local (Chile) times, so we convert to/from UTC when calculating.
"""
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Timezone for interpreting user-facing times (specific_times, once_datetime)
LOCAL_TZ = ZoneInfo(settings.TIMEZONE)
UTC_TZ = ZoneInfo("UTC")


def _utc_to_local(dt: datetime) -> datetime:
    """Convert naive UTC datetime to naive local datetime."""
    return dt.replace(tzinfo=UTC_TZ).astimezone(LOCAL_TZ).replace(tzinfo=None)


def _local_to_utc(dt: datetime) -> datetime:
    """Convert naive local datetime to naive UTC datetime."""
    return dt.replace(tzinfo=LOCAL_TZ).astimezone(UTC_TZ).replace(tzinfo=None)


def calculate_next_execution(
    schedule_type: str,
    start_date: datetime,
    end_date: Optional[datetime],
    last_executed_at: Optional[datetime],
    interval_minutes: Optional[int] = None,
    days_of_week: Optional[list[int]] = None,
    specific_times: Optional[list[str]] = None,
    now: Optional[datetime] = None,
) -> Optional[datetime]:
    """
    Calculate the next execution time for a schedule.

    Args:
        schedule_type: 'interval', 'specific', or 'once'
        start_date: When the schedule becomes active
        end_date: When the schedule expires (optional)
        last_executed_at: Last time this schedule was executed
        interval_minutes: Minutes between executions (for interval type)
        days_of_week: List of weekday numbers 0-6 (JS convention: Sunday=0) for specific type
        specific_times: List of times in LOCAL timezone like ["09:00", "12:00"] for specific type
        now: Current time in UTC (if None, uses datetime.utcnow())

    Returns:
        Next execution datetime in UTC, or None if schedule should not execute
    """
    if now is None:
        now = datetime.utcnow()

    # Check if schedule has expired
    if end_date and now > end_date:
        return None

    if schedule_type == "interval":
        return _calculate_interval_next(
            start_date, end_date, last_executed_at, interval_minutes, now
        )
    elif schedule_type == "specific":
        return _calculate_specific_next(
            start_date, end_date, last_executed_at, days_of_week, specific_times, now
        )
    elif schedule_type == "once":
        return _calculate_once_next(start_date, end_date, last_executed_at, now)
    else:
        logger.warning(f"Unknown schedule type: {schedule_type}")
        return None


def _calculate_interval_next(
    start_date: datetime,
    end_date: Optional[datetime],
    last_executed_at: Optional[datetime],
    interval_minutes: Optional[int],
    now: datetime,
) -> Optional[datetime]:
    """Calculate next execution for interval-based schedule."""
    if not interval_minutes or interval_minutes <= 0:
        logger.warning("Invalid interval_minutes for interval schedule")
        return None

    interval = timedelta(minutes=interval_minutes)

    if last_executed_at:
        # Next = last execution + interval
        next_time = last_executed_at + interval
    else:
        # Never executed: start from start_date or now, whichever is later
        next_time = max(start_date, now)

    # Ensure we're not in the past
    while next_time < now:
        next_time += interval

    # Check end_date
    if end_date and next_time > end_date:
        return None

    return next_time


def _calculate_specific_next(
    start_date: datetime,
    end_date: Optional[datetime],
    last_executed_at: Optional[datetime],
    days_of_week: Optional[list[int]],
    specific_times: Optional[list[str]],
    now: datetime,
) -> Optional[datetime]:
    """
    Calculate next execution for specific days/times schedule.

    specific_times are in LOCAL timezone (e.g. "20:48" = 20:48 Chile time).
    now and return value are in UTC.
    """
    if not days_of_week or not specific_times:
        logger.warning("Missing days_of_week or specific_times for specific schedule")
        return None

    # Convert JS day convention (Sun=0, Mon=1, ..., Sat=6)
    # to Python weekday() convention (Mon=0, Tue=1, ..., Sun=6)
    python_days = [(d - 1) % 7 for d in days_of_week]

    # Parse times and sort them
    parsed_times = []
    for time_str in specific_times:
        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            parsed_times.append((hour, minute))
        except (ValueError, IndexError):
            logger.warning(f"Invalid time format: {time_str}")
            continue

    if not parsed_times:
        return None

    parsed_times.sort()

    # Convert UTC now to local time for comparison with local specific_times
    now_local = _utc_to_local(now)

    # start_date is stored as a date boundary, treat as local
    search_start = max(start_date, now_local)
    current_date = search_start.date()

    # Search up to 8 days ahead (covers full week + 1)
    for day_offset in range(8):
        check_date = current_date + timedelta(days=day_offset)

        # Check if this weekday is in our schedule (Python: Monday=0)
        if check_date.weekday() not in python_days:
            continue

        # Check each scheduled time
        for hour, minute in parsed_times:
            # Candidate in local time
            candidate_local = datetime.combine(check_date, datetime.min.time().replace(
                hour=hour, minute=minute
            ))

            # Skip if before now in local time
            if candidate_local < now_local:
                continue

            # Skip if before start_date
            if candidate_local < start_date:
                continue

            # Convert candidate to UTC for storage and end_date comparison
            candidate_utc = _local_to_utc(candidate_local)

            # Check end_date (in UTC)
            if end_date and candidate_utc > end_date:
                continue

            # Skip if this exact time was just executed (last_executed_at is UTC)
            if last_executed_at:
                if abs((candidate_utc - last_executed_at).total_seconds()) < 60:
                    continue

            return candidate_utc

    return None


def _calculate_once_next(
    start_date: datetime,
    end_date: Optional[datetime],
    last_executed_at: Optional[datetime],
    now: datetime,
) -> Optional[datetime]:
    """Calculate next execution for one-time schedule."""
    # If already executed, no more executions
    if last_executed_at:
        return None

    # Check if start_date is valid
    if end_date and start_date > end_date:
        return None

    # Return start_date if it's in the future or now
    if start_date >= now:
        return start_date

    # If start_date is in the past but not executed, execute now
    return now
