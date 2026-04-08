import logging
from backend.user_service.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from backend.user_service.app.schemas.auth import TokenResponse
from backend.user_service.app.repositories.user_repository import UserRepository
from backend.user_service.app.repositories.profile_repository import UserProfileRepository
from backend.user_service.app.repositories.rating_repository import UserRatingRepository
from backend.user_service.app.models.user import User
from backend.user_service.app.models.profile import UserProfile
from backend.user_service.app.models.rating import UserRating

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: UserProfileRepository,
        rating_repo: UserRatingRepository,
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.rating_repo = rating_repo

    async def register_user(
        self,
        phone_number: str,
        password: str,
        display_name: str,
        email: str | None = None,
    ) -> TokenResponse:
        if await self.user_repo.get_by_phone_number(phone_number):
            raise ValueError("Пользователь с таким номером телефона уже существует")
        if email and await self.user_repo.get_by_email(email):
            raise ValueError("Пользователь с таким email уже существует")

        hashed_password = get_password_hash(password)
        user = User(
            phone_number=phone_number,
            email=email,
            hashed_password=hashed_password,
        )

        try:
            await self.user_repo.create(user)
            await self.profile_repo.create(UserProfile(user_id=user.id, display_name=display_name))
            await self.rating_repo.create(UserRating(user_id=user.id))
            await self.user_repo.db.commit()
        except Exception:
            await self.user_repo.db.rollback()
            logger.exception("Registration failed")
            raise

        return TokenResponse(
            access_token=create_access_token(subject=str(user.id)),
            refresh_token=create_refresh_token(subject=str(user.id)),
        )

    async def authenticate_user(self, phone_number: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_phone_number(phone_number)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Неверный номер телефона или пароль")
        if not user.is_active:
            raise ValueError("Аккаунт деактивирован")

        return TokenResponse(
            access_token=create_access_token(subject=str(user.id)),
            refresh_token=create_refresh_token(subject=str(user.id)),
        )