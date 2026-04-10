from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.user_service.app.models.badge import Badge


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

    async def get_badge_types_by_user_id(self, user_id: UUID | str) -> list[str]:
        uid = UUID(user_id) if isinstance(user_id, str) else user_id
        stmt = select(Badge.badge_type).where(Badge.user_id == uid)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_badges_for_users(self, user_ids: list[UUID]) -> dict[str, list[str]]:
        """Возвращает {user_id: [badge_types]} для массового получения."""
        if not user_ids:
            return {}

        stmt = select(Badge.user_id, Badge.badge_type).where(
            Badge.user_id.in_(user_ids)
        )
        result = await self.db.execute(stmt)

        badges_map: dict[str, list[str]] = {}
        for user_id, badge_type in result.all():
            uid_str = str(user_id)
            if uid_str not in badges_map:
                badges_map[uid_str] = []
            badges_map[uid_str].append(badge_type)

        return badges_map
