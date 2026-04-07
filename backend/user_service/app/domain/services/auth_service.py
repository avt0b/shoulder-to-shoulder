from backend.user_service.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from backend.user_service.app.domain.schemas.auth import TokenResponse
from backend.user_service.app.domain.repositories.user_repository import UserRepository
from backend.user_service.app.domain.models.user import User
from backend.user_service.app.domain.models.profile import UserProfile
from backend.user_service.app.domain.models.rating import UserRating


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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

        profile = UserProfile(user_id=user.id, display_name=display_name)
        rating = UserRating(user_id=user.id)

        await self.user_repo.create_user(user)
        await self.user_repo.create_profile(profile)
        await self.user_repo.create_rating(rating)

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def authenticate_user(self, phone_number: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_phone_number(phone_number)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Неверный номер телефона или пароль")

        if not user.is_active:
            raise ValueError("Аккаунт деактивирован")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )