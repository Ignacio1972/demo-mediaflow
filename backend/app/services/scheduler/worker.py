"""
Scheduler worker.

Background worker that runs every 60 seconds to:
1. Update next_execution_at for all active schedules
2. Find schedules that are due for execution
3. Execute them via the executor module
"""
import asyncio
from datetime import datetime
from typing import Optional
import logging

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.schedule import Schedule
from app.services.scheduler.calculator import calculate_next_execution
from app.services.scheduler.executor import execute_schedule

logger = logging.getLogger(__name__)

# Check interval in seconds
CHECK_INTERVAL = 60


class SchedulerWorker:
    """Background worker for schedule execution."""

    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the scheduler worker."""
        if self._running:
            logger.warning("Scheduler worker is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler worker started")

    async def stop(self) -> None:
        """Stop the scheduler worker gracefully."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Scheduler worker stopped")

    async def _run_loop(self) -> None:
        """Main loop that runs every CHECK_INTERVAL seconds."""
        while self._running:
            try:
                await self._process_schedules()
            except Exception as e:
                logger.error(f"Scheduler worker error: {e}", exc_info=True)

            # Wait for next check interval
            try:
                await asyncio.sleep(CHECK_INTERVAL)
            except asyncio.CancelledError:
                break

    async def _process_schedules(self) -> None:
        """Process all active schedules."""
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.utcnow()
                logger.info(f"Scheduler tick at {now.strftime('%H:%M:%S')}")

                # Step 1: FIRST check for due schedules (before recalculating next_execution_at)
                # This prevents missing schedules that were due between ticks
                result = await db.execute(
                    select(Schedule)
                    .where(
                        Schedule.active == True,
                        Schedule.next_execution_at != None,
                        Schedule.next_execution_at <= now,
                    )
                    .order_by(Schedule.priority.asc(), Schedule.next_execution_at.asc())
                    .limit(1)
                    .with_for_update(skip_locked=True)
                )
                due_schedule = result.scalar_one_or_none()

                if due_schedule:
                    logger.info(
                        f"Executing schedule {due_schedule.id} "
                        f"(was due at {due_schedule.next_execution_at.strftime('%H:%M:%S')}, now={now.strftime('%H:%M:%S')})"
                    )
                    try:
                        await execute_schedule(db, due_schedule)
                        await db.commit()
                    except Exception as e:
                        logger.error(
                            f"Error executing schedule {due_schedule.id}: {e}",
                            exc_info=True
                        )
                        await db.rollback()
                        return

                # Step 2: Update next_execution_at for all active schedules
                result = await db.execute(
                    select(Schedule)
                    .where(Schedule.active == True)
                )
                schedules = result.scalars().all()

                if not schedules:
                    logger.info("No active schedules")
                    return

                for schedule in schedules:
                    next_exec = calculate_next_execution(
                        schedule_type=schedule.schedule_type,
                        start_date=schedule.start_date,
                        end_date=schedule.end_date,
                        last_executed_at=schedule.last_executed_at,
                        interval_minutes=schedule.interval_minutes,
                        days_of_week=schedule.days_of_week,
                        specific_times=schedule.specific_times,
                        now=now,
                    )
                    schedule.next_execution_at = next_exec

                    # Deactivate schedules that have no future executions
                    if next_exec is None and schedule.active:
                        schedule.active = False
                        logger.info(
                            f"Schedule {schedule.id}: Deactivated (no future executions)"
                        )

                await db.commit()

                if not due_schedule:
                    # Log next scheduled execution
                    next_schedule = min(
                        (s for s in schedules if s.next_execution_at),
                        key=lambda s: s.next_execution_at,
                        default=None
                    )
                    if next_schedule:
                        logger.info(
                            f"Next execution: schedule {next_schedule.id} at "
                            f"{next_schedule.next_execution_at.strftime('%H:%M:%S')}"
                        )

            except Exception as e:
                logger.error(f"Error processing schedules: {e}", exc_info=True)
                await db.rollback()


# Singleton instance
scheduler_worker = SchedulerWorker()
