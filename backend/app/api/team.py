from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas import TeamResponse
from app.service import TeamService
from app.core.database import get_session
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/team", tags=["team"])


@router.get("/me", response_model=TeamResponse)
async def get_current_team(
    team_id: uuid.UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить информацию о текущей команде.
    
    **Ответ:**
    - id: uuid - ID команды
    - name: str - название команды
    - score: int - очки команды
    - rank: int - место в рейтинге
    """
    team_service = TeamService(session)
    team = await team_service.get_team_with_rank(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team
