"""Notification model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from backend.notification_service.app.core.database import Base


class Notification(Base):
    """Notification database model."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="info")  # info, warning, success, error
    is_read = Column(Boolean, default=False, index=True)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    sent_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        """String representation."""
        return f"<Notification(id={self.id}, user_id={self.user_id}, title={self.title})>"
