from uuid import UUID
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import UserProfile


class UserProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID | str) -> UserProfile | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def update(self, user_id: UUID | str, update_data: dict) -> UserProfile | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(**update_data, updated_at=func.now())
            .returning(UserProfile)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()