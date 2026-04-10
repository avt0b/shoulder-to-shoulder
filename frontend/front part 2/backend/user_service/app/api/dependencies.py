from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user_service.app.core.database import get_db
from backend.user_service.app.core.security import decode_token
from backend.user_service.app.repositories.user_repository import UserRepository
from backend.user_service.app.repositories.profile_repository import UserProfileRepository
from backend.user_service.app.repositories.rating_repository import UserRatingRepository
from backend.user_service.app.repositories.badge_repository import UserBadgeRepository
from backend.user_service.app.services.auth_service import AuthService
from backend.user_service.app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_token(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_user_id(token_data: dict = Depends(get_current_user_token)) -> str:
    return token_data["sub"]


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_profile_repo(db: AsyncSession = Depends(get_db)) -> UserProfileRepository:
    return UserProfileRepository(db)


async def get_rating_repo(db: AsyncSession = Depends(get_db)) -> UserRatingRepository:
    return UserRatingRepository(db)


async def get_badge_repo(db: AsyncSession = Depends(get_db)) -> UserBadgeRepository:
    return UserBadgeRepository(db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    profile_repo: UserProfileRepository = Depends(get_profile_repo),
    rating_repo: UserRatingRepository = Depends(get_rating_repo),
) -> AuthService:
    return AuthService(user_repo, profile_repo, rating_repo)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    profile_repo: UserProfileRepository = Depends(get_profile_repo),
    rating_repo: UserRatingRepository = Depends(get_rating_repo),
    badge_repo: UserBadgeRepository = Depends(get_badge_repo),
) -> UserService:
    return UserService(user_repo, profile_repo, rating_repo, badge_repo)
