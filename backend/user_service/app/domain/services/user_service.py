"""User Repository - infrastructure layer for database operations."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.user_service.app.domain.models.user import User
from backend.user_service.app.domain.models.profile import UserProfile
from backend.user_service.app.domain.models.rating import UserRating
from backend.user_service.app.domain.models.badge import Badge


class UserRepository:
    """Repository responsible for all database operations related to User."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ====================== User ======================
    async def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        """Get user by phone number."""
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str | None) -> User | None:
        """Get user by email (if email exists)."""
        if not email:
            return None
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create new user."""
        self.db.add(user)
        await self.db.flush()
        return user

    # ====================== Profile ======================
    async def get_profile(self, user_id: str) -> UserProfile | None:
        """Get user profile by user_id."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_profile(self, profile: UserProfile) -> UserProfile:
        """Create user profile."""
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def update_profile(self, user_id: str, update_data: dict) -> UserProfile | None:
        """Update user profile fields."""
        result = await self.db.execute(
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(**update_data)
            .returning(UserProfile)
        )
        await self.db.commit()
        return result.scalar_one_or_none()

    # ====================== Rating ======================
    async def get_rating(self, user_id: str) -> UserRating | None:
        """Get user rating."""
        result = await self.db.execute(
            select(UserRating).where(UserRating.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_rating(self, rating: UserRating) -> UserRating:
        """Create initial rating record."""
        self.db.add(rating)
        await self.db.flush()
        return rating

    async def add_empathy_points(self, user_id: str, points: int = 1) -> UserRating | None:
        """Add empathy points."""
        result = await self.db.execute(
            update(UserRating)
            .where(UserRating.user_id == user_id)
            .values(
                empathy_score=UserRating.empathy_score + points,
                last_updated=UserRating.last_updated  # auto-update
            )
            .returning(UserRating)
        )
        await self.db.commit()
        return result.scalar_one_or_none()

    async def update_reliability(self, user_id: str, success: bool) -> UserRating | None:
        """Update reliability score after event."""
        # Простая логика: +1 к completed_events при успехе
        stmt = (
            update(UserRating)
            .where(UserRating.user_id == user_id)
            .values(
                total_events=UserRating.total_events + 1,
                completed_events=UserRating.completed_events + (1 if success else 0),
                reliability_score=100.0 * (
                    (UserRating.completed_events + (1 if success else 0)) /
                    (UserRating.total_events + 1)
                ).cast("numeric(5,2)")
            )
            .returning(UserRating)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    # ====================== Badges ======================
    async def award_badge(self, user_id: str, badge_type: str) -> Badge | None:
        """Award a badge to user (idempotent)."""
        badge = Badge(user_id=user_id, badge_type=badge_type)
        self.db.add(badge)
        try:
            await self.db.commit()
            return badge
        except Exception:
            await self.db.rollback()
            return None  # badge already exists

    async def get_badges(self, user_id: str) -> list[str]:
        """Get list of badge types for user."""
        result = await self.db.execute(
            select(Badge.badge_type).where(Badge.user_id == user_id)
        )
        return [row[0] for row in result.all()]