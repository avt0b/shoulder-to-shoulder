import logging
from uuid import UUID
from backend.user_service.app.repositories.user_repository import UserRepository
from backend.user_service.app.repositories.profile_repository import UserProfileRepository
from backend.user_service.app.repositories.rating_repository import UserRatingRepository
from backend.user_service.app.repositories.badge_repository import UserBadgeRepository
from backend.user_service.app.schemas.user import (
    UserProfileResponse,
    PublicUserInfoResponse,
    RatingResponse,
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
            self,
            user_repo: UserRepository,
            profile_repo: UserProfileRepository,
            rating_repo: UserRatingRepository,
            badge_repo: UserBadgeRepository,
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.rating_repo = rating_repo
        self.badge_repo = badge_repo

    async def get_user_by_id(self, user_id: UUID | str) -> UserProfileResponse | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        profile = await self.profile_repo.get_by_user_id(user.id)
        if not profile:
            return None

        event_counts = await self.profile_repo.get_event_counts(user.id)

        return UserProfileResponse(
            user_id=str(user.id),
            phone_number=user.phone_number,
            email=user.email,
            display_name=profile.display_name,
            age=profile.age,
            fitness_level=profile.fitness_level,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            city=profile.city,
            preferences=profile.preferences or {},
            # ← Новые поля:
            theme=profile.theme or "light",
            **event_counts,  # attended_events_count, joined_events_count
        )

    async def get_public_user_info(self, user_id: UUID | str) -> PublicUserInfoResponse | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        profile = await self.profile_repo.get_by_user_id(user.id)
        rating = await self.rating_repo.get_by_user_id(user.id)
        badges = await self.badge_repo.get_by_user_id(user.id)
        if not profile or not rating:
            return None

        return PublicUserInfoResponse(
            user_id=str(user.id),
            display_name=profile.display_name,
            fitness_level=profile.fitness_level,
            empathy_score=rating.empathy_score,
            reliability_score=rating.reliability_score,
            badges=badges,
        )

    async def get_rating(self, user_id: UUID | str) -> RatingResponse | None:
        rating = await self.rating_repo.get_by_user_id(user_id)
        if not rating:
            return None
        return RatingResponse(
            empathy_score=rating.empathy_score,
            reliability_score=rating.reliability_score,
            total_events=rating.total_events,
            completed_events=rating.completed_events,
        )

    async def add_empathy_points(self, user_id: UUID | str, points: int = 1) -> RatingResponse | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        try:
            updated = await self.rating_repo.add_empathy_points(user_id, points)
            if not updated:
                return None
            await self.user_repo.db.commit()
            return RatingResponse(
                empathy_score=updated.empathy_score,
                reliability_score=updated.reliability_score,
                total_events=updated.total_events,
                completed_events=updated.completed_events,
            )
        except Exception:
            await self.user_repo.db.rollback()
            logger.exception("Add empathy points failed")
            raise

    async def update_reliability(self, user_id: UUID | str, success: bool) -> RatingResponse | None:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        try:
            updated = await self.rating_repo.update_reliability(user_id, success)
            if not updated:
                return None
            await self.user_repo.db.commit()
            return RatingResponse(
                empathy_score=updated.empathy_score,
                reliability_score=updated.reliability_score,
                total_events=updated.total_events,
                completed_events=updated.completed_events,
            )
        except Exception:
            await self.user_repo.db.rollback()
            logger.exception("Update reliability failed")
            raise

    async def award_badge(self, user_id: UUID | str, badge_type: str) -> bool:
        result = await self.badge_repo.award(user_id, badge_type)
        if result:
            await self.user_repo.db.commit()
            return True
        return False

    async def get_badges(self, user_id: UUID | str) -> list[str]:
        return await self.badge_repo.get_by_user_id(user_id)

    async def update_profile(self, user_id: UUID | str, update_data: dict) -> UserProfileResponse | None:
        """Update non-sensitive profile fields."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        try:
            updated_profile = await self.profile_repo.update(user_id, update_data)
            if not updated_profile:
                return None

            await self.user_repo.db.commit()

            return UserProfileResponse(
                user_id=str(user.id),
                phone_number=user.phone_number,
                email=user.email,
                display_name=updated_profile.display_name,
                age=updated_profile.age,
                fitness_level=updated_profile.fitness_level,
                bio=updated_profile.bio,
                avatar_url=updated_profile.avatar_url,
                preferences=updated_profile.preferences or {},
                city=updated_profile.city
            )
        except Exception:
            await self.user_repo.db.rollback()
            logger.exception("Profile update failed")
            raise

    async def update_contact_info(self, user_id: UUID | str, update_data: dict) -> dict:
        """Update sensitive contact fields (email, phone). Returns updated fields."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        if "email" in update_data and update_data["email"]:
            existing = await self.user_repo.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Email already registered")

        try:
            updated_user = await self.user_repo.update(user_id, update_data)
            if not updated_user:
                return None

            await self.user_repo.db.commit()

            return {
                "email": updated_user.email,
                "phone_number": updated_user.phone_number,
            }
        except Exception:
            await self.user_repo.db.rollback()
            logger.exception("Contact info update failed")
            raise
