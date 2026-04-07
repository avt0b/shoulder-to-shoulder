from pydantic import BaseModel, Field
from typing import Literal


class UserProfileCreateRequest(BaseModel):
    display_name: str
    age: int | None = Field(None)
    fitness_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    bio: str | None = None


class UserProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    age: int | None = Field(None)
    fitness_level: Literal["beginner", "intermediate", "advanced"] | None = None
    bio: str | None = None
    preferences: dict | None = None


class UserProfileResponse(BaseModel):
    user_id: str
    display_name: str
    age: int | None
    fitness_level: str
    bio: str | None
    avatar_url: str | None = None
    preferences: dict


class PublicUserInfoResponse(BaseModel):
    user_id: str
    display_name: str
    fitness_level: str
    empathy_score: int
    reliability_score: float
    badges: list[str] = Field(default_factory=list)
    