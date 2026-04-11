from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class AdminEventResponse(BaseModel):
    id: str
    title: str
    host_id: str
    status: str
    start_time: datetime

    spot_id: str | None = None
    description: str | None = None
    max_participants: int | None = None
    duration_minutes: int | None = None
    photo_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    anonymous: bool = False
    participant_count: int = 0


class AdminEventListResponse(BaseModel):
    events: list[AdminEventResponse]
    total: int
    limit: int
    offset: int


class AdminEventUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    max_participants: int | None = Field(None, ge=2, le=50)
    duration_minutes: int | None = Field(None, ge=30, le=180)
    start_time: str | None = None
    photo_url: str | None = None
    status: Literal["pending", "active", "completed", "cancelled"] | None = None


class AdminActionResponse(BaseModel):
    status: str
    message: str
