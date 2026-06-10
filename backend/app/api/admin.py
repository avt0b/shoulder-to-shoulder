import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.dependencies import verify_admin_token
from app.schemas import (
    AdminAnalyticsResponse,
    AdminBanRequest,
    AdminFlagCreateRequest,
    AdminFlagResponse,
    AdminFlagUpdateRequest,
    AdminFlagVisibilityRequest,
    AdminSubmissionResponse,
    AdminTeamResponse,
    AdminTeamCreateRequest,
)
from app.service import AdminService

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(verify_admin_token)],
)


@router.get("/analytics", response_model=AdminAnalyticsResponse)
async def get_analytics(
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).get_analytics()


@router.get("/flags", response_model=list[AdminFlagResponse])
async def list_flags(
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).list_flags()


@router.post("/flags", response_model=AdminFlagResponse)
async def create_flag(
    request: AdminFlagCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await AdminService(session).create_flag(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/flags/visibility", response_model=list[AdminFlagResponse])
async def set_flags_visibility(
    request: AdminFlagVisibilityRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).set_flags_visibility(request.is_visible)


@router.patch("/flags/{flag_id}", response_model=AdminFlagResponse)
async def update_flag(
    flag_id: uuid.UUID,
    request: AdminFlagUpdateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        flag = await AdminService(session).update_flag(flag_id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flag not found",
        )
    return flag


@router.post("/uploads", response_model=dict)
async def upload_task_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are allowed",
        )

    suffix = Path(file.filename or "").suffix.lower() or ".bin"
    file_name = f"{uuid.uuid4().hex}{suffix}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file_name

    with file_path.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)

    return {"image_url": f"/uploads/{file_name}"}


@router.delete("/flags/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flag(
    flag_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await AdminService(session).delete_flag(flag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flag not found",
        )


@router.get("/teams", response_model=list[AdminTeamResponse])
async def list_teams(
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).list_teams()


@router.post("/teams", response_model=AdminTeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    request: AdminTeamCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await AdminService(session).create_team(request.team_name, request.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/teams/{team_id}/ban", response_model=AdminTeamResponse)
async def ban_team(
    team_id: uuid.UUID,
    request: AdminBanRequest,
    session: AsyncSession = Depends(get_session),
):
    team = await AdminService(session).ban_team(team_id, request.reason)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


@router.post("/teams/{team_id}/unban", response_model=AdminTeamResponse)
async def unban_team(
    team_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    team = await AdminService(session).unban_team(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


@router.get("/submissions", response_model=list[AdminSubmissionResponse])
async def list_recent_submissions(
    session: AsyncSession = Depends(get_session),
):
    return await AdminService(session).get_recent_submissions()
