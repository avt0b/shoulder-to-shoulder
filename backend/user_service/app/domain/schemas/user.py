from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class UserProfileCreateRequest(BaseModel):
    display_name: str
    age: int | None = Field(None, ge=18)
    fitness_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    bio: str | None = None
    email: EmailStr | None = None
    preferences: dict | None = None


class UserProfileUpdateRequest(BaseModel):
    display_name: str | None = None
    age: int | None = Field(None, ge=18)
    fitness_level: Literal["beginner", "intermediate", "advanced"] | None = None
    bio: str | None = None
    email: EmailStr | None = None
    preferences: dict | None = None


class UserProfileResponse(BaseModel):
    user_id: str
    phone_number: str
    email: EmailStr | None
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
    # phone_number и email НЕ показываем публично
