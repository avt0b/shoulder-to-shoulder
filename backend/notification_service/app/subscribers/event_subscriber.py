import json
from uuid import UUID

from backend.notification_service.app.services.notification_service import NotificationService
from backend.notification_service.app.core.nats_client import nats_client


async def handle_user_joined(msg):
    try:
        data = json.loads(msg.data.decode())

        host_id = UUID(data.get("host_id"))
        user_name = data.get("user_name", "Новый участник")
        event_title = data.get("event_title", "Мероприятие")

        service = NotificationService()
        await service.send_immediate_to_host(
            host_id=host_id,
            user_name=user_name,
            event_title=event_title)

        print(f"Обработано присоединение пользователя к мероприятию (host: {host_id})")

    except Exception as e:
        print(f"Error in handle_user_joined: {e}")


async def handle_match_request(msg):
    """Обработчик темы: notification.match_request"""
    try:
        data = json.loads(msg.data.decode())

        recipient_id = UUID(data.get("recipient_id"))
        resp_data = data.get("data", {})

        service = NotificationService()
        await service.send_match_response_notification(
            recipient_id=recipient_id,
            responder_name=resp_data.get("responder_id"),  # Тут можно имя подтянуть, если есть
            workout_time=resp_data.get("workout_time", ""),
            message=resp_data.get("message")
        )

        print(f"✅ Обработан отклик на заявку для {recipient_id}")

    except Exception as e:
        print(f"❌ Error in handle_match_request: {e}")
        import traceback
        traceback.print_exc()


async def start_subscribers():
    await nats_client.subscribe("event.user_joined", handle_user_joined)
    print("Подписка на event.user_joined активирована")
    await nats_client.subscribe("notification.match_request", handle_match_request)
    print("Подписка на notification.match_request активирована")