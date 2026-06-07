from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.service import AuthService
from app.core.database import get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Логин команды. Возвращает JWT токен.
    
    **Параметры:**
    - team_name: str - название команды
    - password: str - пароль команды
    
    **Ответ:**
    - access_token: str - JWT токен
    """
    auth_service = AuthService(session)
    result = await auth_service.login(request.team_name, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return result

@router.post("/register" , response_model=LoginResponse)
async def register(
        request: RegisterRequest,
        session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    auth = AuthService(session=session)
    result = await auth.register(request.team_name, request.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid credentials",
        )

    return result
