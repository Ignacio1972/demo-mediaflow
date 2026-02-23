"""
Scheduler service module.

Provides automatic execution of scheduled audio messages.
"""
from app.services.scheduler.worker import scheduler_worker

__all__ = ["scheduler_worker"]
