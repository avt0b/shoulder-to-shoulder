from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.user_service.app.core.security import decode_token
from backend.user_service.app.domain.repositories.user_repository import UserRepository
from backend.user_service.app.domain.services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user_service.app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current authenticated user from JWT token."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use access token.",
        )

    return payload


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)
