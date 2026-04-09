from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.admin_service.app.core.config import settings


def decode_admin_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        if payload.get("role") != "superuser":
            return None
        return payload
    except JWTError:
        return None
