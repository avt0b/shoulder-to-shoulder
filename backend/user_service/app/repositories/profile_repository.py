from uuid import UUID
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.event_service.app.models.participant import EventParticipant
from backend.user_service.app.models.profile import UserProfile
from backend.user_service.app.models.rating import UserRating


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

    async def get_event_counts(self, user_id: UUID | str) -> dict:
        """Возвращает статистику из локальной таблицы user_ratings."""
        uid = UUID(user_id) if isinstance(user_id, str) else user_id

        stmt = select(UserRating).where(UserRating.user_id == uid)
        result = await self.db.execute(stmt)
        rating = result.scalar_one_or_none()

        if not rating:
            return {"joined_events_count": 0, "attended_events_count": 0}

        return {
            # total_events = все ивенты, куда пользователь записался (не считая отмен)
            "joined_events_count": rating.total_events or 0,
            # completed_events = ивенты, где пользователь успешно отметился (чекин)
            "attended_events_count": rating.completed_events or 0,
        }
