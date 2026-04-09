from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.api.dependencies import require_superuser
from app.services.admin_service import AdminService
from app.schemas.user import (
    AdminUserResponse,
    AdminActionResponse,
    UserBanRequest,
    UserUnbanRequest,
    AwardBadgeRequest,
    AwardBadgeResponse,
)

router = APIRouter(prefix="/users", tags=["admin:users"])


@router.get("", response_model=list[AdminUserResponse])
async def list_users(
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        search: str | None = Query(None, description="Search by phone or email"),
        _: dict = Depends(require_superuser),
        admin_svc: AdminService = Depends(lambda: AdminService()),
):
    return await admin_svc.list_users(limit, offset, search)


@router.post("/{user_id}/ban", response_model=AdminActionResponse)
async def ban_user(
        user_id: str,
        request: UserBanRequest | None = None,
        _: dict = Depends(require_superuser),
        admin_svc: AdminService = Depends(lambda: AdminService()),
):
    reason = request.reason if request else None
    result = await admin_svc.ban_user(user_id, reason=reason)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return AdminActionResponse(
        status="banned",
        message=f"User {user_id} has been banned",
    )


@router.post("/{user_id}/unban", response_model=AdminActionResponse)
async def unban_user(
        user_id: str,
        request: UserUnbanRequest | None = None,
        _: dict = Depends(require_superuser),
        admin_svc: AdminService = Depends(lambda: AdminService()),
):
    comment = request.comment if request else None
    result = await admin_svc.unban_user(user_id, comment=comment)

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return AdminActionResponse(
        status="unbanned",
        message=f"User {user_id} has been unbanned",
    )


@router.post("/{user_id}/badge", response_model=AwardBadgeResponse, status_code=status.HTTP_201_CREATED)
async def award_badge(
        user_id: str,
        request: AwardBadgeRequest,
        _: dict = Depends(require_superuser),
        admin_svc: AdminService = Depends(lambda: AdminService()),
):
    result = await admin_svc.award_badge(user_id, request.badge_type)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return AwardBadgeResponse(
        badge_type=request.badge_type,
        awarded=result,
        message="Badge awarded" if result else "Badge already exists",
    )