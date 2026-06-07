from datetime import datetime
from datetime import timedelta
import hashlib

import bcrypt
from jose import jwt

from app.core.config import settings


def _password_bytes(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(password: str):
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("ascii")


def verify_password(
    plain: str,
    hashed: str
):
    hashed_bytes = hashed.encode("ascii")
    if bcrypt.checkpw(_password_bytes(plain), hashed_bytes):
        return True

    plain_bytes = plain.encode("utf-8")
    if len(plain_bytes) <= 72:
        return bcrypt.checkpw(plain_bytes, hashed_bytes)

    return False


def create_token(
    team_id: str
):

    payload = {
        "sub": team_id,
        "exp": datetime.utcnow()
        + timedelta(hours=12)
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
