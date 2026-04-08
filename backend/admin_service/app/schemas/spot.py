"""Pydantic schemas for admin spot moderation endpoints."""

from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


class ModerateSpotRequest(BaseModel):
    """Request body for spot moderation decision."""
    action: Literal["approve", "reject", "request_changes"] = Field(
        ...,
        description="Moderation decision"
    )
    reason: str | None = Field(
        None,
        max_length=500,
        description="Reason for rejection or change request"
    )
    notes: str | None = Field(
        None,
        max_length=1000,
        description="Internal admin notes (not shown to user)"
    )


class CreateSpotOverrideRequest(BaseModel):
    """Request body for admin creating a spot manually."""
    name: str = Field(..., min_length=3, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    spot_type: Literal["workout", "running", "stretching", "multi"] = Field(...)
    lighting: bool = Field(default=False)
    has_benches: bool = Field(default=False)
    notes: str | None = Field(None, max_length=500)


class AdminSpotResponse(BaseModel):
    """Spot data for admin moderation view."""
    id: UUID
    name: str
    latitude: float
    longitude: float
    spot_type: str
    status: Literal["pending", "approved", "rejected", "archived"]
    created_by: UUID | None
    created_at: str
    moderation_notes: str | None


class ModerationResultResponse(BaseModel):
    """Response after spot moderation action."""
    spot_id: UUID
    action: str
    new_status: str
    message: str | None = None