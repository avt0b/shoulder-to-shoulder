from pydantic import BaseModel, Field


class RatingResponse(BaseModel):
    empathy_score: int
    reliability_score: float
    total_events: int
    completed_events: int


class AddEmpathyPointsRequest(BaseModel):
    """Internal request schema for adding empathy points
    (used when Events Service sends event)."""
    user_id: str
    points: int = Field(1, ge=1)
    reason: str | None = None
