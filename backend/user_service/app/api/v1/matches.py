from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from backend.user_service.app.api.dependencies import get_current_user_id
from backend.user_service.app.services.match_service import PoolService
from backend.user_service.app.repositories.match_repository import PoolRepository
from backend.user_service.app.core.database import get_db
from pydantic import BaseModel, Field

router = APIRouter(prefix="/pool", tags=["workout-pool"])


def get_pool_service(db=Depends(get_db), nats=None):
    return PoolService(PoolRepository(db))


class CreatePoolRequest(BaseModel):
    city: str
    preferred_time: datetime
    duration_minutes: int = 60
    fitness_level: str | None = None
    description: str | None = None


class RespondRequest(BaseModel):
    message: str | None = None


# --- Эндпоинты ---

@router.get("", response_model=list[dict])
async def list_pool(
        city: str | None = Query(None),
        service: PoolService = Depends(get_pool_service),
):
    return await service.repo.get_open_requests(city=city)


@router.post("", status_code=201)
async def create_pool_request(
        data: CreatePoolRequest,
        user_id: UUID = Depends(get_current_user_id),
        service: PoolService = Depends(get_pool_service),
):
    req = await service.post_request(UUID(user_id), data.model_dump())
    return {"status": "posted", "request_id": str(req.id)}


@router.post("/{request_id}/respond", status_code=201)
async def respond_to_pool_request(
        request_id: UUID,
        data: RespondRequest,
        user_id: UUID = Depends(get_current_user_id),
        service: PoolService = Depends(get_pool_service),
):
    responder_id = user_id
    try:
        resp = await service.respond_to_request(request_id, UUID(responder_id), data.message)
        return {"status": "sent", "response_id": str(resp.id)}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/inbox", response_model=list[dict])
async def my_incoming_responses(
        user_id: UUID = Depends(get_current_user_id),
        service: PoolService = Depends(get_pool_service),
):
    return await service.repo.get_my_incoming_responses(UUID(user_id))
