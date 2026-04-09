"""Notification repository for database operations."""

from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationRepository:
    """Repository for notification database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, notification: NotificationCreate) -> Notification:
        """Create a new notification."""
        db_notification = Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type,
            scheduled_at=notification.scheduled_at,
            expires_at=notification.expires_at,
        )
        self.db.add(db_notification)
        await self.db.commit()
        await self.db.refresh(db_notification)
        return db_notification

    async def get_by_id(self, notification_id: int) -> Notification | None:
        """Get notification by ID."""
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Notification]:
        """Get notifications for a user."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_pending_notifications(self) -> list[Notification]:
        """Get pending notifications that should be sent."""
        now = datetime.utcnow()
        query = select(Notification).where(
            (Notification.sent_at.is_(None)) &
            ((Notification.scheduled_at.is_(None)) | (Notification.scheduled_at <= now)) &
            ((Notification.expires_at.is_(None)) | (Notification.expires_at > now))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, notification_id: int, notification_update: NotificationUpdate) -> Notification | None:
        """Update a notification."""
        db_notification = await self.get_by_id(notification_id)
        if not db_notification:
            return None

        update_data = notification_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_notification, field, value)

        await self.db.commit()
        await self.db.refresh(db_notification)
        return db_notification

    async def mark_as_read(self, notification_id: int) -> Notification | None:
        """Mark notification as read."""
        db_notification = await self.get_by_id(notification_id)
        if not db_notification:
            return None
        db_notification.is_read = True
        await self.db.commit()
        await self.db.refresh(db_notification)
        return db_notification

    async def mark_as_sent(self, notification_id: int) -> Notification | None:
        """Mark notification as sent."""
        db_notification = await self.get_by_id(notification_id)
        if not db_notification:
            return None
        db_notification.sent_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(db_notification)
        return db_notification

    async def delete(self, notification_id: int) -> bool:
        """Delete a notification."""
        db_notification = await self.get_by_id(notification_id)
        if not db_notification:
            return False
        await self.db.delete(db_notification)
        await self.db.commit()
        return True

    async def get_count_by_user_id(self, user_id: int) -> int:
        """Get total count of notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        result = await self.db.execute(query)
        return len(result.scalars().all())
