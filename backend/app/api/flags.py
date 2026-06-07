from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas import (
    SubmitFlagRequest,
    SubmitFlagResponse,
    TeamTaskResponse,
)
from app.service import FlagService
from app.core.database import get_session
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/flags", tags=["flags"])


@router.get("/tasks", response_model=list[TeamTaskResponse])
async def get_tasks(
    team_id: uuid.UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    flag_service = FlagService(session)
    return await flag_service.get_team_tasks(team_id)


@router.post("/submit", response_model=SubmitFlagResponse)
async def submit_flag(
    request: SubmitFlagRequest,
    team_id: uuid.UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Отправить флаг.
    
    **Параметры:**
    - flag: str - текст флага
    
    **Ответ:**
    - success: bool - успешно ли
    - message: str - сообщение
    - points: int | null - количество очков (если успешно)
    """
    flag_service = FlagService(session)
    result = await flag_service.submit_flag(team_id, request.flag)
    return result
