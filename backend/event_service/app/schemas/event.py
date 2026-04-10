from typing import Literal

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class EventCreateRequest(BaseModel):
    spot_id: UUID
    title: str = Field(..., min_length=3, max_length=100)
    description: str | None = None
    max_participants: int = Field(default=10, ge=2, le=50)
    duration_minutes: int = Field(default=60, ge=30, le=180)
    start_time: datetime
    photo_url: str | None = None
    anonymous: bool


class EventResponse(BaseModel):
    id: UUID
    host_id: UUID
    spot_id: UUID
    title: str
    description: str | None
    max_participants: int
    duration_minutes: int
    status: str
    start_time: datetime
    created_at: datetime
    anonymous: bool


class CheckInResponse(BaseModel):
    event_id: UUID
    user_id: UUID
    status: str
    message: str


class EventUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    max_participants: int | None = Field(None, ge=2, le=50)
    duration_minutes: int | None = Field(None, ge=30, le=180)
    start_time: datetime | None = None
    photo_url: str | None = None
    status: Literal["pending", "active", "completed", "cancelled"] | None = None


class EventListItem(BaseModel):
    id: UUID
    host_id: UUID
    spot_id: UUID
    title: str
    description: str | None
    max_participants: int
    status: str
    start_time: datetime
    photo_url: str | None
    created_at: datetime
    participant_count: int
    anonymous: bool


class EventListResponse(BaseModel):
    events: list[EventListItem]
    total: int
    limit: int
    offset: int



class EventListFilters(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    status: Literal["pending", "active", "completed", "cancelled"] | None = None
    host_id: UUID | None = None
    spot_id: UUID | None = None
    start_from: datetime | None = None
    start_to: datetime | None = None


class EventDetailResponse(BaseModel):
    id: UUID
    host_id: UUID
    spot_id: UUID
    title: str
    description: str | None
    max_participants: int
    status: str
    start_time: datetime
    photo_url: str | None
    created_at: datetime
    participant_count: int
    participant_ids: list[UUID]
    anonymous: bool
