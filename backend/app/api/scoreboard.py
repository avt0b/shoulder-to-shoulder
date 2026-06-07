from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas import ScoreboardEntry
from app.service import ScoreboardService
from app.core.database import get_session
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["scoreboard"])


@router.get("/scoreboard", response_model=list[ScoreboardEntry])
async def get_scoreboard(
    team_id: uuid.UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить таблицу лидеров.
    
    **Ответ:**
    - Список команд с их рангом и очками, отсортированный по очкам
    """
    scoreboard_service = ScoreboardService(session)
    scoreboard = await scoreboard_service.get_scoreboard()
    return scoreboard
