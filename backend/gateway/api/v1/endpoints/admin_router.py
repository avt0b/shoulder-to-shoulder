from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
import logging

from ....core.security import get_current_user, TokenData
from ....core.http_client import http_client
from ....config import settings

logger = logging.getLogger(__name__)


class UserBanRequest(BaseModel):
    reason: Optional[str] = None


class UserUnbanRequest(BaseModel):
    comment: Optional[str] = None


class AwardBadgeRequest(BaseModel):
    badge_type: str


class ModerateSpotRequest(BaseModel):
    action: str
    reason: Optional[str] = None
    notes: Optional[str] = None


class AdminEventUpdateRequest(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


router_admin = APIRouter(prefix="/admin", tags=["admin"])


@router_admin.get("/users", response_model=list[dict])
async def admin_list_users(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_LIST_USERS] User: {current_user.user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    params = {
        "limit": limit,
        "offset": offset
    }
    if search:
        params["search"] = search
    
    admin_response = await http_client.get(
        f"{settings.admin_service_url}/api/v1/users",
        params=params,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.post("/users/{user_id}/ban", response_model=dict)
async def admin_ban_user(
    request: Request,
    user_id: str,
    data: Optional[UserBanRequest] = None,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_BAN_USER] Current user: {current_user.user_id}, Target: {user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump() if data else {}
    
    admin_response = await http_client.post(
        f"{settings.admin_service_url}/api/v1/users/{user_id}/ban",
        json=payload,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.post("/users/{user_id}/unban", response_model=dict)
async def admin_unban_user(
    request: Request,
    user_id: str,
    data: Optional[UserUnbanRequest] = None,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_UNBAN_USER] Current user: {current_user.user_id}, Target: {user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump() if data else {}
    
    admin_response = await http_client.post(
        f"{settings.admin_service_url}/api/v1/users/{user_id}/unban",
        json=payload,
        headers=headers
    )
    
    return admin_response


@router_admin.post("/users/{user_id}/badge", response_model=dict, status_code=status.HTTP_201_CREATED)
async def admin_award_badge(
    request: Request,
    user_id: str,
    data: AwardBadgeRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_AWARD_BADGE] Current user: {current_user.user_id}, Target: {user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump()
    
    admin_response = await http_client.post(
        f"{settings.admin_service_url}/api/v1/users/{user_id}/badge",
        json=payload,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.get("/events", response_model=dict)
async def admin_list_events(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    host_id: Optional[str] = Query(None),
    spot_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_LIST_EVENTS] User: {current_user.user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    params = {
        "limit": limit,
        "offset": offset
    }
    if status_filter:
        params["status_filter"] = status_filter
    if host_id:
        params["host_id"] = host_id
    if spot_id:
        params["spot_id"] = spot_id
    
    admin_response = await http_client.get(
        f"{settings.admin_service_url}/api/v1/events",
        params=params,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.get("/events/{event_id}", response_model=dict)
async def admin_get_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_GET_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    admin_response = await http_client.get(
        f"{settings.admin_service_url}/api/v1/events/{event_id}",
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return admin_response


@router_admin.patch("/events/{event_id}", response_model=dict)
async def admin_update_event(
    request: Request,
    event_id: UUID,
    data: AdminEventUpdateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_UPDATE_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    update_data = data.model_dump(exclude_unset=True)
    
    admin_response = await http_client.patch(
        f"{settings.admin_service_url}/api/v1/events/{event_id}",
        json=update_data,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.delete("/events/{event_id}", response_model=dict)
async def admin_delete_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_DELETE_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    admin_response = await http_client.delete(
        f"{settings.admin_service_url}/api/v1/events/{event_id}",
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.get("/spots", response_model=list[dict])
async def admin_list_spots(
    request: Request,
    status_filter: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_LIST_SPOTS] User: {current_user.user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    params = {}
    if status_filter:
        params["status_filter"] = status_filter
    
    admin_response = await http_client.get(
        f"{settings.admin_service_url}/api/v1/spots",
        params=params,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.get("/spots/{spot_id}", response_model=dict)
async def admin_get_spot(
    request: Request,
    spot_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_GET_SPOT] User: {current_user.user_id}, Spot: {spot_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    admin_response = await http_client.get(
        f"{settings.admin_service_url}/api/v1/spots/{spot_id}",
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spot not found"
        )
    
    return admin_response


@router_admin.put("/spots/{spot_id}/moderate", response_model=dict)
async def admin_moderate_spot(
    request: Request,
    spot_id: str,
    data: ModerateSpotRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_MODERATE_SPOT] User: {current_user.user_id}, Spot: {spot_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump()
    
    admin_response = await http_client.put(
        f"{settings.admin_service_url}/api/v1/spots/{spot_id}/moderate",
        json=payload,
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
    
    return admin_response


@router_admin.delete("/spots/{spot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_spot(
    request: Request,
    spot_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[ADMIN_DELETE_SPOT] User: {current_user.user_id}, Spot: {spot_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    admin_response = await http_client.delete(
        f"{settings.admin_service_url}/api/v1/spots/{spot_id}",
        headers=headers
    )
    
    if not admin_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin service unavailable"
        )
