from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Literal

from backend.admin_service.app.core.security import decode_admin_token
from backend.admin_service.app.core.nats_client import request
import logging

from backend.user_service.app.core.permissions import has_permission

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
UserRole = Literal["user", "moderator", "admin", "superuser"]


async def get_current_user_token(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_admin_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def require_role(required_role: UserRole = "moderator"):
    async def role_checker(token_data: dict = Depends(get_current_user_token)) -> dict:
        user_role = token_data.get("role", "user")

        if not has_permission(user_role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {required_role}, you have: {user_role}",
            )

        return {**token_data, "role": user_role}
    return role_checker

require_moderator = require_role("moderator")
require_superuser = require_role("superuser")
