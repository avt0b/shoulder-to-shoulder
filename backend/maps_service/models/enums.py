from enum import Enum as PyEnum
from datetime import datetime

class ActivityTypeEnum(str, PyEnum):
    WORKOUT = "workout"
    HORIZONTAL_BAR = "horizontal_bar"
    STRETCHING = "stretching"
    RUNNING = "running"
    BASKETBALL = "basketball"
    VOLLEYBALL = "volleyball"
    TENNIS = "tennis"
    FOOTBALL = "football"


class LevelEnum(str, PyEnum):
    BEGINNER = "Новичок"
    INTERMEDIATE = "Средний"
    ADVANCED = "Продвинутый"
    OPEN = "Открыто"
