from uuid import UUID
from sqlalchemy import select, update, func, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from backend.user_service.app.models.rating import UserRating


class UserRatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID | str) -> UserRating | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        result = await self.db.execute(select(UserRating).where(UserRating.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, rating: UserRating) -> UserRating:
        self.db.add(rating)
        await self.db.flush()
        return rating

    async def add_empathy_points(self, user_id: UUID | str, points: int = 1) -> UserRating | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            update(UserRating)
            .where(UserRating.user_id == user_id)
            .values(
                empathy_score=UserRating.empathy_score + points,
                last_updated=func.now(),
            )
            .returning(UserRating)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_reliability(self, user_id: UUID | str, success: bool) -> UserRating | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        new_completed = UserRating.completed_events + (1 if success else 0)
        new_total = UserRating.total_events + 1
        reliability = (100.0 * new_completed / new_total).cast(Numeric(5, 2))

        stmt = (
            update(UserRating)
            .where(UserRating.user_id == user_id)
            .values(
                total_events=new_total,
                completed_events=new_completed,
                reliability_score=reliability,
                last_updated=func.now(),
            )
            .returning(UserRating)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()