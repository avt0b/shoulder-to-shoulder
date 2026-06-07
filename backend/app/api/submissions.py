from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas import SubmissionResponse
from app.service import FlagService
from app.core.database import get_session
from app.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["submissions"])


@router.get("/submissions", response_model=list[SubmissionResponse])
async def get_submissions(
    team_id: uuid.UUID = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить историю попыток команды.
    
    **Ответ:**
    - Список попыток (до 50 последних)
    """
    flag_service = FlagService(session)
    submissions = await flag_service.get_team_submissions(team_id)
    return submissions
