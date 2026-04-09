"""Schemas module."""

from backend.notification_service.app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
)

__all__ = [
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
]
