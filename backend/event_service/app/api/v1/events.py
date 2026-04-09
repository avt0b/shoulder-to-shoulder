from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user_id
from app.services.event_service import EventService
from app.repositories.event_repository import EventRepository
from app.core.database import get_db
from app.schemas.event import EventCreateRequest, EventResponse, CheckInResponse

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(EventRepository(db))


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreateRequest,
    host_id: str = Depends(get_current_user_id),
    service: EventService = Depends(get_event_service),
):
    try:
        return await service.create_event(host_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{event_id}/join")
async def join_event(
    event_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: EventService = Depends(get_event_service),
):
    try:
        joined = await service.join_event(user_id, event_id)
        if not joined:
            raise HTTPException(status_code=409, detail="Already joined")
        return {"status": "joined"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{event_id}/checkin", response_model=CheckInResponse)
async def checkin_event(
    event_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: EventService = Depends(get_event_service),
):
    try:
        return await service.checkin_event(user_id, event_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{event_id}/cancel")
async def cancel_event(
    event_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: EventService = Depends(get_event_service),
):
    try:
        event = await service.repo.get_by_id(event_id)
        if not event or event.status in ("completed", "cancelled"):
            raise ValueError("Cannot cancel")
        await service.repo.update_status(event_id, "cancelled")
        await service.repo.db.commit()
        return {"status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/internal/complete-expired")
async def trigger_auto_complete(service: EventService = Depends(get_event_service)):
    try:
        await service.complete_expired_events()
        return {"status": "processed"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))