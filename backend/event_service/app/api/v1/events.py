from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from backend.event_service.app.api.dependencies import get_current_user_context
from backend.event_service.app.models.event import Event
from backend.event_service.app.services.event_service import EventService, logger
from backend.event_service.app.repositories.event_repository import EventRepository
from backend.event_service.app.core.database import get_db
from backend.event_service.app.schemas.event import (
    EventCreateRequest,
    EventResponse,
    CheckInResponse,
    EventUpdateRequest, EventListFilters, EventListResponse, EventDetailResponse,
)

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db=Depends(get_db)) -> EventService:
    return EventService(EventRepository(db))


async def require_host_or_admin(
        event_id: UUID,
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
) -> Event:
    """Check that current user is the event host or an admin."""
    user_id = ctx["user_id"]
    role = ctx.get("role", "user")

    event = await service.repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if str(event.host_id) != user_id and role not in ("moderator", "superuser"):
        raise HTTPException(status_code=403, detail="Only host or admin can modify")
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
        data: EventCreateRequest,
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
):
    try:
        return await service.create_event(ctx["user_id"], data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{event_id}/join")
async def join_event(
        event_id: UUID,
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
):
    try:
        joined = await service.join_event(ctx["user_id"], event_id)
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
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
):
    try:
        return await service.checkin_event(ctx["user_id"], event_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{event_id}/cancel")
async def leave_event(
        event_id: UUID,
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
):
    try:
        participants = await service.leave_event(ctx["user_id"], event_id)
        return {"status": "left", "participants": participants}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{event_id}/cancel")
async def cancel_event(
        event_id: UUID,
        ctx: dict = Depends(get_current_user_context),
        service: EventService = Depends(get_event_service),
):
    try:
        event = await service.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if str(event.host_id) != ctx["user_id"]:
            raise HTTPException(status_code=403, detail="Only host can cancel")
        if event.status in ("completed", "cancelled"):
            raise ValueError("Cannot cancel")

        await service.repo.update_status(event_id, "cancelled")
        await service.repo.db.commit()
        return {"status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"Cancel event failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{event_id}", response_model=EventResponse)
async def update_event(
        event_id: UUID,
        data: EventUpdateRequest,
        _: Event = Depends(require_host_or_admin),
        service: EventService = Depends(get_event_service),
):
    try:
        updated = await service.update_event(event_id, data.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(404, detail="Event not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"Update event failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{event_id}")
async def delete_event(
        event_id: UUID,
        _: Event = Depends(require_host_or_admin),
        service: EventService = Depends(get_event_service),
):
    success = await service.delete_event(event_id)
    if not success:
        raise HTTPException(404, detail="Event not found")
    return {"status": "deleted", "event_id": str(event_id)}


# @router.post("/internal/complete-expired")
# async def trigger_auto_complete(service: EventService = Depends(get_event_service)):
#     try:
#         await service.complete_expired_events()
#         return {"status": "processed"}
#     except RuntimeError as e:
#         raise HTTPException(status_code=503, detail=str(e))


@router.get("", response_model=EventListResponse)
async def list_events(
        filters: EventListFilters = Depends(),
        service: EventService = Depends(get_event_service),
):
    return await service.list_events(
        limit=filters.limit,
        offset=filters.offset,
        status_filter=filters.status,
        host_id=filters.host_id,
        spot_id=filters.spot_id,
        start_time_from=filters.start_from,
        start_time_to=filters.start_to,
    )

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event_detail(
    event_id: UUID,
    service: EventService = Depends(get_event_service),
):
    event_data = await service.get_event_detail(event_id)
    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_data
