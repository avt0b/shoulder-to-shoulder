"""Pydantic schemas for admin user management endpoints."""

from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from uuid import UUID


class UserBanRequest(BaseModel):
    """Request body for banning a user."""
    reason: str | None = Field(None, max_length=500, description="Optional ban reason for audit log")


class UserUnbanRequest(BaseModel):
    """Request body for unbanning a user."""
    reason: str | None = Field(None, max_length=500, description="Optional unban reason")


class AwardBadgeRequest(BaseModel):
    """Request body for awarding a badge to a user."""
    badge_type: str = Field(..., min_length=3, max_length=50, description="Badge type identifier")
    reason: str | None = Field(None, max_length=200, description="Why this badge is awarded")


class UpdateUserRoleRequest(BaseModel):
    """Request body for changing user role."""
    role: Literal["user", "moderator", "admin"] = Field(..., description="New user role")



class AdminUserResponse(BaseModel):
    """Sanitized user data for admin list view."""
    id: UUID
    phone_number: str
    email: EmailStr | None
    is_active: bool
    is_phone_verified: bool
    created_at: str  # ISO format string
    updated_at: str | None


class AdminActionResponse(BaseModel):
    """Generic response for admin actions."""
    status: str
    message: str | None = None
    data: dict | None = None


class AwardBadgeResponse(BaseModel):
    """Response for badge awarding."""
    badge_type: str
    awarded: bool  # True if newly created, False if already existed
    message: str | None = None