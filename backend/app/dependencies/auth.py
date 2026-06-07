from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import AuthService
from app.core.database import get_session

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> uuid.UUID:
    """
    Получить текущего пользователя из JWT токена.
    Используется как зависимость для защиты endpoints.
    """
    token = credentials.credentials
    auth_service = AuthService(session)
    team_id = auth_service.verify_token(token)

    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return team_id
