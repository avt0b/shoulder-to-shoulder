from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
import logging

from ....core.security import get_current_user, TokenData
from ....core.http_client import http_client
from ....config import settings

logger = logging.getLogger(__name__)


class EventCreateRequest(BaseModel):
    spot_id: str
    title: str
    description: Optional[str] = None
    max_participants: int
    duration_minutes: int
    start_time: str
    photo_url: Optional[str] = None
    anonymous: bool = False


class EventUpdateRequest(BaseModel):
    spot_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[str] = None
    photo_url: Optional[str] = None
    anonymous: Optional[bool] = None


router_events = APIRouter(prefix="/events", tags=["events"])


@router_events.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: Request,
    data: EventCreateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[CREATE_EVENT] User: {current_user.user_id}")
    
    payload = data.model_dump()
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    print(payload)

    event_response = await http_client.post(
        f"{settings.event_service_url}/api/v1/events",
        json=payload,
        headers=headers
    )
    
    return event_response


@router_events.post("/{event_id}/join", response_model=dict)
async def join_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[JOIN_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    event_response = await http_client.post(
        f"{settings.event_service_url}/api/v1/events/{event_id}/join",
        headers=headers
    )
    
    return event_response


@router_events.post("/{event_id}/checkin", response_model=dict)
async def checkin_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[CHECKIN_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    event_response = await http_client.post(
        f"{settings.event_service_url}/api/v1/events/{event_id}/checkin",
        headers=headers
    )
    print(event_response)
    return event_response


@router_events.post("/{event_id}/cancel", response_model=dict)
async def cancel_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[CANCEL_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    event_response = await http_client.post(
        f"{settings.event_service_url}/api/v1/events/{event_id}/cancel",
        headers=headers
    )
    
    return event_response


@router_events.post("/{event_id}", response_model=dict)
async def update_event(
    request: Request,
    event_id: UUID,
    data: EventUpdateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[UPDATE_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    update_data = data.model_dump(exclude_unset=True)
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    event_response = await http_client.post(
        f"{settings.event_service_url}/api/v1/events/{event_id}",
        json=update_data,
        headers=headers
    )
    
    return event_response


@router_events.delete("/{event_id}", response_model=dict)
async def delete_event(
    request: Request,
    event_id: UUID,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[DELETE_EVENT] User: {current_user.user_id}, Event: {event_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    event_response = await http_client.delete(
        f"{settings.event_service_url}/api/v1/events/{event_id}",
        headers=headers
    )
    
    return event_response


@router_events.get("", response_model=dict)
async def list_events(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    host_id: Optional[str] = Query(None),
    spot_id: Optional[str] = Query(None)
):
    logger.info(f"[LIST_EVENTS] limit: {limit}, offset: {offset}")
    
    params = {
        "limit": limit,
        "offset": offset
    }
    if status:
        params["status"] = status
    if host_id:
        params["host_id"] = host_id
    if spot_id:
        params["spot_id"] = spot_id
    
    events_response = await http_client.get(
        f"{settings.event_service_url}/api/v1/events",
        params=params
    )
    
    return events_response


@router_events.get("/{event_id}", response_model=dict)
async def get_event_detail(event_id: str):
    logger.info(f"[GET_EVENT] Event: {event_id}")
    print(event_id)
    
    event_response = await http_client.get(
        f"{settings.event_service_url}/api/v1/events/{event_id}"
    )
    
    return event_response
