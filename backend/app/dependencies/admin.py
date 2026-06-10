from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.service import AuthService

security = HTTPBearer(auto_error=False)

async def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    x_admin_token: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> None:
    if credentials and AuthService(session).verify_admin_token(credentials.credentials):
        return

    if x_admin_token and x_admin_token == settings.ADMIN_TOKEN:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin token",
    )
