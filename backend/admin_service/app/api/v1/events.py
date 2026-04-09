from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from backend.admin_service.app.api.dependencies import require_superuser, require_moderator
from backend.admin_service.app.services.admin_service import AdminService
from backend.admin_service.app.schemas.event import (
    AdminEventResponse,
    AdminEventListResponse,
    AdminEventUpdateRequest,
    AdminActionResponse,
)

router = APIRouter(prefix="/events", tags=["admin:events"])


@router.get("", response_model=AdminEventListResponse)
async def list_events(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: str | None = Query(None),
    host_id: str | None = Query(None),
    spot_id: str | None = Query(None),
    _: dict = Depends(require_moderator),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    return await admin_svc.list_events(limit, offset, status_filter, host_id, spot_id)


@router.get("/{event_id}", response_model=AdminEventResponse)
async def get_event(
    event_id: UUID,
    _: dict = Depends(require_moderator),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    event = await admin_svc.get_event(str(event_id))
    if not event:
        raise HTTPException(404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=AdminEventResponse)
async def update_event(
    event_id: UUID,
    data: AdminEventUpdateRequest,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    result = await admin_svc.update_event(str(event_id), data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(404, detail="Event not found")
    return result


@router.delete("/{event_id}", response_model=AdminActionResponse)
async def delete_event(
    event_id: UUID,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    success = await admin_svc.delete_event(str(event_id))
    if not success:
        raise HTTPException(404, detail="Event not found")
    return AdminActionResponse(status="deleted", message=f"Event {event_id} deleted")