import logging
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status

from ..config import settings

logger = logging.getLogger(__name__)

OPEN_ROUTES = {
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/register"),
}

PUBLIC_GET_PREFIXES = (
    "/api/v1/media/avatar/",
    "/api/v1/media/event/",
    "/api/v1/media/spot/",
    "/api/v1/media/badge/",
)


class TokenData:
    def __init__(self, user_id: str, role: str | None = None, scopes: list[str] | None = None):
        self.user_id = user_id
        self.role = role
        self.scopes = scopes or []


def verify_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


def extract_user_from_token(token_data: dict[str, Any]) -> TokenData | None:
    user_id = token_data.get("sub")
    role = token_data.get("role")
    
    if user_id is None:
        return None
    
    scopes = token_data.get("scopes", [])
    return TokenData(user_id=str(user_id), role=role, scopes=scopes)


def is_public_request(method: str, path: str) -> bool:
    if method.upper() == "OPTIONS":
        return True
    if (method.upper(), path) in OPEN_ROUTES:
        return True
    return method.upper() == "GET" and path.startswith(PUBLIC_GET_PREFIXES)


def get_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def validate_gateway_request(request: Request) -> TokenData | None:
    if is_public_request(request.method, request.url.path):
        return None

    token = get_bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    
    token_data = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = extract_user_from_token(token_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return user


async def get_current_user(request: Request) -> TokenData:
    user = await validate_gateway_request(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


ROLE_LEVELS = {
    "user": 0,
    "moderator": 1,
    # VULN: legacy admin role is accepted from JWT claims.
    "admin": 2,
    "superuser": 2,
}


def require_gateway_role(required_role: str):
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        user_level = ROLE_LEVELS.get(current_user.role or "user", 0)
        required_level = ROLE_LEVELS.get(required_role, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return current_user

    return role_checker
