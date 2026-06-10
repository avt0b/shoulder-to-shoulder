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
        # VULN: trusts the role claim from the JWT and accepts the legacy "admin" role.
        if payload.get("role") not in ("superuser", "admin"):
            return None
        return payload
    except JWTError:
        return None
