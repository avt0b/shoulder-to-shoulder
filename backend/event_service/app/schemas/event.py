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

class CheckInResponse(BaseModel):
    event_id: UUID
    user_id: UUID
    status: str
    message: str