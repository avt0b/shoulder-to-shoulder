from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


# Auth Schemas
class LoginRequest(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)

class RegisterRequest(BaseModel):
    team_name: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256) 

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Team Schemas
class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    score: int
    rank: int

    class Config:
        from_attributes = True


# Flag Schemas
class SubmitFlagRequest(BaseModel):
    flag: str = Field(..., min_length=1, max_length=256)


class SubmitFlagResponse(BaseModel):
    success: bool
    message: str
    points: Optional[int] = None


class TeamTaskResponse(BaseModel):
    id: uuid.UUID
    description: str | None
    points: int
    solved: bool
    solved_at: datetime | None = None
    created_at: datetime


# Submission Schemas
class SubmissionResponse(BaseModel):
    id: uuid.UUID
    flag: str
    correct: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Scoreboard Schemas
class ScoreboardEntry(BaseModel):
    rank: int
    team_name: str
    score: int


# Admin Schemas
class AdminFlagCreateRequest(BaseModel):
    flag: str = Field(..., min_length=1, max_length=256)
    description: str | None = Field(default=None, max_length=512)
    points: int = Field(..., ge=1)


class AdminFlagResponse(BaseModel):
    id: uuid.UUID
    flag: str
    description: str | None
    points: int
    created_at: datetime
    solves: int = 0


class AdminTeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    score: int
    rank: int
    is_banned: bool
    ban_reason: str | None = None
    banned_at: datetime | None = None
    created_at: datetime
    submissions_count: int = 0
    solves_count: int = 0


class AdminBanRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=512)


class AdminAnalyticsResponse(BaseModel):
    teams_count: int
    banned_teams_count: int
    flags_count: int
    submissions_count: int
    correct_submissions_count: int
    wrong_submissions_count: int
    total_score: int


class AdminSubmissionResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    team_name: str
    flag_id: uuid.UUID | None
    flag: str
    correct: bool
    created_at: datetime
