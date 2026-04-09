from fastapi import APIRouter, Depends, HTTPException, status
from backend.admin_service.app.api.dependencies import require_superuser
from backend.admin_service.app.services.admin_service import AdminService
from backend.admin_service.app.schemas.spot import (
    ModerateSpotRequest,
    ModerationResultResponse,
    AdminSpotResponse,
)

router = APIRouter(prefix="/spots", tags=["admin:spots"])

#TODO: сделать, когда все споты готовы будут
@router.get("", response_model=list[AdminSpotResponse])
async def list_spots(
    status_filter: str | None = None,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    return await admin_svc.list_spots(status=status_filter)


@router.get("/{spot_id}", response_model=AdminSpotResponse)
async def get_spot(
    spot_id: str,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    spot = await admin_svc.get_spot(spot_id)
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    return spot


@router.put("/{spot_id}/moderate", response_model=ModerationResultResponse)
async def moderate_spot(
    spot_id: str,
    request: ModerateSpotRequest,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    result = await admin_svc.moderate_spot(
        spot_id,
        action=request.action,
        reason=request.reason,
        notes=request.notes,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Spot not found")
    return result


@router.delete("/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spot(
    spot_id: str,
    _: dict = Depends(require_superuser),
    admin_svc: AdminService = Depends(lambda: AdminService()),
):
    """DELETE /api/v1/admin/spots/{id} — permanently remove a spot."""
    success = await admin_svc.delete_spot(spot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spot not found")
    # 204 No Content — пустой ответ