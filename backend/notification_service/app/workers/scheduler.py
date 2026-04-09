"""Background scheduler for sending notifications."""

import asyncio
import httpx
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.notification_service import NotificationService

scheduler_task = None


async def check_pending_notifications():
    """Check for pending notifications and send them."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                service = NotificationService(db)
                pending = await service.get_pending_notifications()

                for notification in pending:
                    try:
                        # Send POST to gateway
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                f"{settings.GATEWAY_URL}/api/v1/go-notif",
                                json={"notification_id": notification.id},
                                timeout=5.0,
                            )
                    except Exception as e:
                        print(f"Error sending notification {notification.id}: {e}")

        except Exception as e:
            print(f"Error checking pending notifications: {e}")

        # Wait before checking again
        await asyncio.sleep(settings.SCHEDULER_INTERVAL_SECONDS)


async def start_scheduler():
    """Start the notification scheduler."""
    global scheduler_task
    scheduler_task = asyncio.create_task(check_pending_notifications())
    print("Notification scheduler started")


async def stop_scheduler():
    """Stop the notification scheduler."""
    global scheduler_task
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
    print("Notification scheduler stopped")
