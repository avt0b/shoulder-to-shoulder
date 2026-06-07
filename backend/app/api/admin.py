import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.dependencies import verify_admin_token
from app.schemas import (
    AdminAnalyticsResponse,
    AdminBanRequest,
    AdminFlagCreateRequest,
    AdminFlagResponse,
    AdminSubmissionResponse,
    AdminTeamResponse,
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
