"""Notification API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse, NotificationListResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse, status_code=201)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new notification."""
    service = NotificationService(db)
    return await service.create_notification(notification)


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a notification by ID."""
    service = NotificationService(db)
    notification = await service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.get("/user/{user_id}", response_model=NotificationListResponse)
async def get_user_notifications(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Get all notifications for a user."""
    service = NotificationService(db)
    return await service.get_user_notifications(user_id, skip, limit)


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a notification."""
    service = NotificationService(db)
    notification = await service.update_notification(notification_id, notification_update)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/{notification_id}/mark-as-read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/create-notif", response_model=NotificationResponse, status_code=201)
async def create_notif_gateway(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create notification (gateway endpoint)."""
    service = NotificationService(db)
    return await service.create_notification(notification)


@router.post("/go-notif")
async def send_notification_callback(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Callback from scheduler to send notification to gateway."""
    service = NotificationService(db)
    success = await service.send_notification_to_gateway(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "sent", "notification_id": notification_id}
