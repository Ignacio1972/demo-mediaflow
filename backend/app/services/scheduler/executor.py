"""
Schedule executor.

Executes a single schedule by:
1. Loading the AudioMessage from the database
2. Calling azuracast_client.send_audio_to_radio()
3. Recording success/failure in ScheduleLog
4. Updating last_executed_at
5. Deactivating if type is "once"
"""
import asyncio
import os
from datetime import datetime
from typing import Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.schedule import Schedule, ScheduleLog
from app.models.audio import AudioMessage
from app.services.azuracast.client import azuracast_client

logger = logging.getLogger(__name__)


async def execute_schedule(
    db: AsyncSession,
    schedule: Schedule,
) -> bool:
    """
    Execute a single schedule.

    Args:
        db: Database session
        schedule: The schedule to execute

    Returns:
        True if execution succeeded, False otherwise
    """
    error_message: Optional[str] = None
    success = False
    audio_id: Optional[int] = None

    try:
        # Get the audio message
        if not schedule.audio_message_id:
            error_message = "Schedule has no audio_message_id"
            logger.warning(f"Schedule {schedule.id}: {error_message}")
            await _record_log(db, schedule.id, False, error_message, None)
            return False

        # Load the audio message
        result = await db.execute(
            select(AudioMessage).where(AudioMessage.id == schedule.audio_message_id)
        )
        audio_message = result.scalar_one_or_none()

        if not audio_message:
            error_message = f"AudioMessage {schedule.audio_message_id} not found"
            logger.warning(f"Schedule {schedule.id}: {error_message}")
            await _record_log(db, schedule.id, False, error_message, None)
            return False

        audio_id = audio_message.id

        # Check if audio file exists
        if not audio_message.file_path or not os.path.exists(audio_message.file_path):
            error_message = f"Audio file not found on disk: {audio_message.file_path}"
            logger.warning(f"Schedule {schedule.id}: {error_message}")
            await _record_log(db, schedule.id, False, error_message, audio_id)
            return False

        # Send to radio
        logger.info(
            f"Schedule {schedule.id}: Sending audio '{audio_message.display_name}' "
            f"to radio (file: {audio_message.file_path})"
        )

        result = await asyncio.wait_for(
            azuracast_client.send_audio_to_radio(
                file_path=audio_message.file_path,
                interrupt=True,
                target_filename=audio_message.filename,
            ),
            timeout=30,
        )

        if result["success"]:
            success = True
            logger.info(f"Schedule {schedule.id}: Successfully sent to radio")
        else:
            error_message = result.get("message", "Unknown error sending to radio")
            logger.error(f"Schedule {schedule.id}: {error_message}")

    except Exception as e:
        error_message = f"Execution error: {str(e)}"
        logger.error(f"Schedule {schedule.id}: {error_message}", exc_info=True)

    # Update schedule state
    schedule.last_executed_at = datetime.utcnow()

    # Deactivate one-time schedules after execution
    if schedule.schedule_type == "once":
        schedule.active = False
        logger.info(f"Schedule {schedule.id}: One-time schedule deactivated")

    # Record execution log
    await _record_log(db, schedule.id, success, error_message, audio_id)

    return success


async def _record_log(
    db: AsyncSession,
    schedule_id: int,
    success: bool,
    error_message: Optional[str],
    audio_id: Optional[int],
) -> None:
    """Record a schedule execution in the log table."""
    log_entry = ScheduleLog(
        schedule_id=schedule_id,
        executed_at=datetime.utcnow(),
        success=success,
        error_message=error_message,
        audio_generated_id=audio_id,
    )
    db.add(log_entry)
    # Don't commit here - let the caller handle the transaction
