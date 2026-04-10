"""Workers module."""

from backend.notification_service.app.workers.scheduler import start_scheduler, stop_scheduler

__all__ = ["start_scheduler", "stop_scheduler"]
