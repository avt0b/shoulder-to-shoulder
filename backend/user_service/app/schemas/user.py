from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class UserProfileCreateRequest(BaseModel):
    display_name: str
    age: int | None = Field(None, ge=18)
    fitness_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    bio: str | None = None
    email: EmailStr | None = None
    preferences: dict | None = None
    city: str | None = Field(None, max_length=100)


class UserProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    age: int | None = Field(None, ge=18)
    fitness_level: Literal["beginner", "intermediate", "advanced"] | None = None
    bio: str | None = None
    preferences: dict | None = None
    city: str | None = Field(None, max_length=100)


class UserContactUpdateRequest(BaseModel):
    email: EmailStr | None = None


class UserProfileResponse(BaseModel):
    user_id: str
    phone_number: str
    email: str | None
    display_name: str
    age: int | None
    fitness_level: str
    bio: str | None
    avatar_url: str | None
    city: str | None
    preferences: dict
    theme: Literal["light", "dark"] = "light"
    joined_events_count: int = 0
    attended_events_count: int = 0
    badges: list[str] = []


class PublicUserProfileResponse(BaseModel):
    user_id: str
    display_name: str
    age: int | None
    fitness_level: str
    bio: str | None
    avatar_url: str | None
    city: str | None
    joined_events_count: int = 0
    attended_events_count: int = 0
    badges: list[str] = []


class RatingResponse(BaseModel):
    empathy_score: int
    reliability_score: float
    total_events: int
    completed_events: int


class ThemeUpdateRequest(BaseModel):
    theme: Literal["light", "dark"]
