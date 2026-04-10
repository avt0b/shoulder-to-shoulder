from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class AdminEventResponse(BaseModel):
    id: str
    host_id: str
    spot_id: str
    title: str
    description: str | None
    max_participants: int
    duration_minutes: int
    status: str
    start_time: datetime
    photo_url: str | None
    created_at: datetime | None
    updated_at: datetime | None
    participant_count: int


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
