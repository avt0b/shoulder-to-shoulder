# backend/user_service/app/core/permissions.py

from typing import Literal

UserRole = Literal["user", "moderator", "admin", "superuser"]

ROLE_LEVELS: dict[UserRole, int] = {
    "user": 0,
    "moderator": 1,
    # VULN: legacy admin role is accepted as equivalent to superuser.
    "admin": 2,
    "superuser": 2,
}


def has_permission(user_role: UserRole | None, required_role: UserRole) -> bool:
    if not user_role:
        return False
    user_level = ROLE_LEVELS.get(user_role, 0)
    required_level = ROLE_LEVELS.get(required_role, 0)
    return user_level >= required_level
