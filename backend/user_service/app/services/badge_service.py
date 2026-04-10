import logging
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from backend.user_service.app.core.database import AsyncSession
from backend.user_service.app.models.badge import Badge
from backend.user_service.app.core.badges.registry import BADGE_RULES, BadgeType

logger = logging.getLogger(__name__)


async def evaluate_and_award_badges(user_id: UUID | str, rating_data: dict, db: AsyncSession) -> list[str]:
    newly_awarded = []
    uid_str = str(user_id)

    for badge_type, condition in BADGE_RULES.items():
        if condition(rating_data):
            stmt = (
                pg_insert(Badge)
                .values(user_id=uid_str, badge_type=badge_type.value)
                .on_conflict_do_nothing(index_elements=["user_id", "badge_type"])
            )
            result = await db.execute(stmt)
            if result.rowcount > 0:
                newly_awarded.append(badge_type.value)
                logger.info(f"Badge awarded: {badge_type.value} to user {uid_str}")
    if newly_awarded:
        pass
    return newly_awarded
