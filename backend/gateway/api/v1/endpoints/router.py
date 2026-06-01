from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import Optional
import logging

from ....config import settings
from ....core.security import get_current_user, TokenData
from ....core.http_client import http_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aggregated", tags=["aggregated"])


@router.get("/profile", response_model=dict)
async def get_user_profile(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    """Get user profile from user service."""
    logger.info(f"[GET_PROFILE] User: {current_user.user_id}")
    
    # Forward the authorization token to user_service
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    user_profile = await http_client.get(
        f"{settings.user_service_url}/api/v1/users/{current_user.user_id}",
        headers=headers
    )
    
    user_info = {
        "user_id": current_user.user_id,
        "scopes": current_user.scopes,
        "profile": user_profile if user_profile else None
    }
    
    return user_info


@router.get("/user-meetups", response_model=dict)
async def get_user_meetups(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all meetups for current user."""
    logger.info(f"[USER_MEETUPS] User: {current_user.user_id}")
    
    # Forward the authorization token
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    meetups = await http_client.get(
        f"{settings.forum_service_url}/api/v1/meetups/user/{current_user.user_id}",
        headers=headers
    )
    
    return {
        "user_id": current_user.user_id,
        "meetups": meetups.get("meetups", []) if meetups else []
    }


@router.get("/user-events", response_model=dict)
async def get_user_events(
    request: Request,
    limit: int = Query(default=50),
    offset: int = Query(default=0),
    current_user: TokenData = Depends(get_current_user)
):
    """Get events for current user."""
    logger.info(f"[USER_EVENTS] User: {current_user.user_id}, Limit: {limit}, Offset: {offset}")
    
    # Forward the authorization token
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    events = await http_client.get(
        f"{settings.event_service_url}/api/v1/events",
        params={
            "limit": limit,
            "offset": offset,
            "host_id": str(current_user.user_id)
        },
        headers=headers
    )
    
    return {
        "user_id": current_user.user_id,
        "events": events.get("events", []) if events else [],
        "limit": limit,
        "offset": offset
    }


@router.get("/dashboard", response_model=dict)
async def get_user_dashboard(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    """Get complete user dashboard with profile, meetups, and events."""
    logger.info(f"[DASHBOARD] User: {current_user.user_id}")
    
    # Forward the authorization token
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    profile = await http_client.get(
        f"{settings.user_service_url}/api/v1/users/{current_user.user_id}",
        headers=headers
    )
    
    meetups = await http_client.get(
        f"{settings.forum_service_url}/api/v1/meetups/user/{current_user.user_id}",
        headers=headers
    )
    
    events = await http_client.get(
        f"{settings.event_service_url}/api/v1/events",
        params={
            "limit": 10,
            "offset": 0,
            "host_id": str(current_user.user_id)
        },
        headers=headers
    )
    
    return {
        "user": {
            "id": current_user.user_id,
            "profile": profile if profile else None
        },
        "stats": {
            "meetups_count": len(meetups.get("meetups", [])) if meetups else 0,
            "events_count": len(events.get("events", [])) if events else 0
        },
        "recent_meetups": meetups.get("meetups", [])[:5] if meetups else [],
        "recent_events": events.get("events", [])[:5] if events else []
    }
