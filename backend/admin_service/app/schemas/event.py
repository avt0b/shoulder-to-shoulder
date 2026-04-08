"""Pydantic schemas for admin event management (placeholder)."""

from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime


class CancelEventRequest(BaseModel):
    """Request body for admin-forced event cancellation."""
    reason: str = Field(..., min_length=10, max_length=500)
    notify_participants: bool = Field(default=True)


class AdminEventResponse(BaseModel):
    """Event data for admin view."""
    id: UUID
    host_id: UUID
    spot_id: UUID
    title: str
    start_time: datetime
    status: Literal["pending", "active", "completed", "cancelled"]
    participant_count: int
    created_at: datetime