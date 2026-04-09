from enum import Enum
from typing import Callable


class BadgeType(str, Enum):
    FIRST_STEP = "first_step"
    REGULAR = "regular"
    IRONMAN = "ironman"
    RELIABLE = "reliable"
    EMPATHY = "empathy"
    SOCIAL = "social"


BADGE_RULES: dict[BadgeType, Callable] = {
    BadgeType.FIRST_STEP: lambda r: r.get("completed_events", 0) >= 1,
    BadgeType.REGULAR: lambda r: r.get("completed_events", 0) >= 5,
    BadgeType.IRONMAN: lambda r: r.get("completed_events", 0) >= 20,
    BadgeType.RELIABLE: lambda r: r.get("reliability_score", 0) >= 90.0,
    BadgeType.EMPATHY: lambda r: r.get("empathy_score", 0) >= 50,
    BadgeType.SOCIAL: lambda r: r.get("total_events", 0) >= 3,
}
