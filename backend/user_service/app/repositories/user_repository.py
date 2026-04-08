from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from backend.user_service.app.models.user import User
from sqlalchemy import select, update, func

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID | str) -> User | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str | None) -> User | None:
        if not email:
            return None
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user_id: UUID | str, update_data: dict) -> User | None:
        """Update fields in the 'users' table (e.g., email, is_active)."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data, updated_at=func.now())
            .returning(User)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
