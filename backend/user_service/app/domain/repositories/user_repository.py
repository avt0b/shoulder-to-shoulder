"""User repository - infrastructure layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.user_service.app.domain.models.user import User
from backend.user_service.app.domain.models.profile import UserProfile
from backend.user_service.app.domain.models.rating import UserRating


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        if not email:
            return None
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_profile(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def create_rating(self, rating: UserRating) -> UserRating:
        self.db.add(rating)
        await self.db.flush()
        return rating
