"""Core module."""

from backend.notification_service.app.core.config import settings
from backend.notification_service.app.core.database import engine, AsyncSessionLocal, Base, get_db, init_db
from backend.notification_service.app.core.nats_client import nats_client

__all__ = [
    "settings",
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_db",
    "init_db",
    "nats_client",
]
