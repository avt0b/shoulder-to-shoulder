"""Notification Service - упрощённая версия для хакатона"""

import json
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.notification_service.app.core.nats_client import nats_client


class NotificationService:
    async def send_immediate_to_host(self, host_id: UUID, user_name: str, event_title: str):
        try:
            message = f"{user_name} присоединился к вашему мероприятию «{event_title}»"

            await self._publish_event("notification.immediate", {
                "user_id": str(host_id),
                "title": "Новый участник!",
                "message": message,
                "type": "info",
                "timestamp": datetime.now().isoformat()
            })

            print(f"Уведомление отправлено хосту {host_id}: {message}")

        except Exception as e:
            print(f"Ошибка при отправке уведомления: {e}")

    async def _publish_event(self, subject: str, data: dict):
        try:
            serializable_data = self._make_serializable(data)
            message = json.dumps(serializable_data).encode()
            await nats_client.publish(subject, message)
        except Exception as e:
            print(f"Error publishing {subject}: {e}")

    def _make_serializable(self, obj):
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj