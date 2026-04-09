from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.badge import Badge


class UserBadgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def award(self, user_id: UUID | str, badge_type: str) -> Badge | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        badge = Badge(user_id=user_id, badge_type=badge_type)
        self.db.add(badge)
        try:
            await self.db.flush()
            return badge
        except IntegrityError:
            return None

    async def get_by_user_id(self, user_id: UUID | str) -> list[str]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        result = await self.db.execute(select(Badge.badge_type).where(Badge.user_id == user_id))
        return [row[0] for row in result.all()]
