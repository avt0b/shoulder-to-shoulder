"""Notification business logic service."""

import json
from sqlalchemy.ext.asyncio import AsyncSession

from backend.notification_service.app.repositories.notification_repository import NotificationRepository
from backend.notification_service.app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from backend.notification_service.app.core.nats_client import nats_client
from backend.notification_service.app.core.config import settings


class NotificationService:
    """Service for notification business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.repository = NotificationRepository(db)

    async def create_notification(self, notification: NotificationCreate) -> NotificationResponse:
        """Create a new notification."""
        db_notification = await self.repository.create(notification)

        # Publish event to NATS
        await self._publish_event("notification.created", {
            "id": db_notification.id,
            "user_id": db_notification.user_id,
            "title": db_notification.title,
            "notification_type": db_notification.notification_type,
        })

        return NotificationResponse.model_validate(db_notification)

    async def get_notification(self, notification_id: int) -> NotificationResponse | None:
        """Get notification by ID."""
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 100):
        """Get all notifications for a user."""
        notifications = await self.repository.get_by_user_id(user_id, skip, limit)
        total = await self.repository.get_count_by_user_id(user_id)
        return {
            "total": total,
            "items": [NotificationResponse.model_validate(n) for n in notifications],
        }

    async def update_notification(self, notification_id: int, notification_update: NotificationUpdate) -> NotificationResponse | None:
        """Update a notification."""
        notification = await self.repository.update(notification_id, notification_update)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def mark_as_read(self, notification_id: int) -> NotificationResponse | None:
        """Mark notification as read."""
        notification = await self.repository.mark_as_read(notification_id)
        if not notification:
            return None
        return NotificationResponse.model_validate(notification)

    async def send_notification_to_gateway(self, notification_id: int):
        """Send notification to gateway service."""
        notification = await self.repository.get_by_id(notification_id)
        if not notification:
            return False

        # Mark as sent
        await self.repository.mark_as_sent(notification_id)

        # Publish event
        await self._publish_event("notification.sent", {
            "id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
        })

        return True

    async def get_pending_notifications(self):
        """Get pending notifications that need to be sent."""
        return await self.repository.get_pending_notifications()

    async def _publish_event(self, subject: str, data: dict):
        """Publish event to NATS."""
        try:
            message = json.dumps(data).encode()
            await nats_client.publish(subject, message)
        except Exception as e:
            print(f"Error publishing event {subject}: {e}")
