"""Notification schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: str = Field(default="info", pattern="^(info|warning|success|error)$")
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""

    title: str | None = Field(None, min_length=1, max_length=255)
    message: str | None = Field(None, min_length=1)
    notification_type: str | None = Field(None, pattern="^(info|warning|success|error)$")
    is_read: bool | None = None
    scheduled_at: datetime | None = None
    expires_at: datetime | None = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    scheduled_at: datetime | None
    sent_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for list response."""

    total: int
    items: list[NotificationResponse]
