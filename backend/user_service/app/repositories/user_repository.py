from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.event_service.app.models.participant import EventParticipant
from backend.user_service.app.models.profile import UserProfile
from backend.user_service.app.models.rating import UserRating
from backend.user_service.app.models.user import User
from sqlalchemy import select, update, func, or_


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

    async def get_all(
            self,
            limit: int = 50,
            offset: int = 0,
            search: str | None = None,
    ) -> list[User]:
        """Get users with pagination and optional search."""
        stmt = select(User).offset(offset).limit(limit)

        if search:
            stmt = stmt.where(
                or_(
                    User.phone_number.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                )
            )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def set_active(self, user_id: UUID | str, is_active: bool) -> bool:
        """Ban/unban user by ID. Returns True if user was found and updated."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=is_active, updated_at=func.now())
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def list_public_users(self, limit: int, offset: int) -> tuple[list[dict], int]:
        # Выбираем данные, склеиваем таблицы
        stmt = select(
            User.id,
            UserProfile.display_name,
            UserProfile.city,
            UserProfile.age,
            UserProfile.avatar_url,
            func.coalesce(UserRating.empathy_score, 0).label("empathy_score"),
            func.coalesce(UserRating.reliability_score, 0).label("reliability_score"),
        )

        # OUTER JOIN: если профиля/рейтинга нет, юзер всё равно вернётся
        stmt = stmt.outerjoin(UserProfile, UserProfile.user_id == User.id)
        stmt = stmt.outerjoin(UserRating, UserRating.user_id == User.id)

        # Только активные
        stmt = stmt.where(User.is_active == True)

        # Считаем общее количество (без ошибки cartesian product)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Сортируем по надёжности (тех у кого нет рейтинга - в конец)
        stmt = stmt.order_by(
            UserRating.reliability_score.desc().nullslast()
        ).offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        users = [
            {
                "user_id": str(r.id),
                "display_name": r.display_name,
                "city": r.city,
                "age": r.age,
                "avatar_url": r.avatar_url,
                "empathy_score": float(r.empathy_score),
                "reliability_score": float(r.reliability_score),
            }
            for r in rows
        ]

        return users, total