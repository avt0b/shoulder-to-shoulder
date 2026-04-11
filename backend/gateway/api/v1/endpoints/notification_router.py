from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from pydantic import BaseModel
import logging

from ....core.security import get_current_user, TokenData
from ....core.http_client import http_client
from ....config import settings

logger = logging.getLogger(__name__)


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: Optional[str] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int


router_notifications = APIRouter(prefix="/notifications", tags=["notifications"])


@router_notifications.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    request: Request,
    data: NotificationCreate,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[CREATE_NOTIFICATION] User: {current_user.user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump()
    
    notification_response = await http_client.post(
        f"{settings.notification_service_url}/api/v1/notifications/",
        json=payload,
        headers=headers
    )
    
    if not notification_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification service unavailable"
        )
    
    return notification_response


@router_notifications.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    request: Request,
    notification_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[GET_NOTIFICATION] User: {current_user.user_id}, Notification: {notification_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    notification_response = await http_client.get(
        f"{settings.notification_service_url}/api/v1/notifications/{notification_id}",
        headers=headers
    )
    
    if not notification_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification_response


@router_notifications.get("/user/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    request: Request,
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[GET_USER_NOTIFICATIONS] Current user: {current_user.user_id}, Target user: {user_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    params = {
        "skip": skip,
        "limit": limit
    }
    
    notification_response = await http_client.get(
        f"{settings.notification_service_url}/api/v1/notifications/user/{user_id}",
        params=params,
        headers=headers
    )
    
    if not notification_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification service unavailable"
        )
    
    return notification_response


@router_notifications.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    request: Request,
    notification_id: int,
    data: NotificationUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[UPDATE_NOTIFICATION] User: {current_user.user_id}, Notification: {notification_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    update_data = data.model_dump(exclude_unset=True)
    
    notification_response = await http_client.patch(
        f"{settings.notification_service_url}/api/v1/notifications/{notification_id}",
        json=update_data,
        headers=headers
    )
    
    if not notification_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notification service unavailable"
        )
    
    return notification_response


@router_notifications.post("/{notification_id}/mark-as-read", response_model=NotificationResponse)
async def mark_as_read(
    request: Request,
    notification_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[MARK_AS_READ] User: {current_user.user_id}, Notification: {notification_id}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    notification_response = await http_client.post(
        f"{settings.notification_service_url}/api/v1/notifications/{notification_id}/mark-as-read",
        headers=headers
    )
    
    if not notification_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification_response
