from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from backend.event_service.app.api.dependencies import get_current_user_id
from backend.event_service.app.services.event_service import EventService
from backend.event_service.app.repositories.event_repository import EventRepository
from backend.event_service.app.core.database import get_db
from backend.event_service.app.schemas.event import EventCreateRequest, EventResponse, CheckInResponse

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(EventRepository(db))


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        data: EventCreateRequest,
        host_id: str = Depends(get_current_user_id),
        service: EventService = Depends(get_event_service),
):
    return await service.create_event(host_id, data.model_dump())


@router.post("/{event_id}/join")
async def join_event(
        event_id: UUID,
        user_id: str = Depends(get_current_user_id),
        service: EventService = Depends(get_event_service),
):
    try:
        joined = await service.join_event(user_id, event_id)
        if not joined:
            raise HTTPException(409, "Already joined")
        return {"status": "joined"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{event_id}/checkin", response_model=CheckInResponse)
async def checkin_event(
        event_id: UUID,
        user_id: str = Depends(get_current_user_id),
        service: EventService = Depends(get_event_service),
):
    try:
        return await service.checkin_event(user_id, event_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{event_id}/cancel")
async def cancel_event(
        event_id: UUID,
        user_id: str = Depends(get_current_user_id),
        service: EventService = Depends(get_event_service),
):
    # TODO: проверка, что user_id == host_id
    event = await service.repo.get_by_id(event_id)
    if not event or event.status in ("completed", "cancelled"):
        raise HTTPException(400, "Cannot cancel")
    await service.repo.update_status(event_id, "cancelled")
    await service.repo.db.commit()
    return {"status": "cancelled"}


# Внутренний эндпоинт для крона/фоновых задач
@router.post("/internal/complete-expired")
async def trigger_auto_complete(service: EventService = Depends(get_event_service)):
    await service.complete_expired_events()
    return {"status": "processed"}
