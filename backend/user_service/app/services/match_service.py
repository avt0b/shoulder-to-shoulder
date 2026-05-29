import json
import logging
from uuid import UUID
from backend.user_service.app.repositories.match_repository import PoolRepository
from backend.user_service.app.models.match import WorkoutRequest
from backend.user_service.app.core.nats_client import nc

logger = logging.getLogger(__name__)


class PoolService:
    def __init__(self, repo: PoolRepository):
        self.repo = repo

    async def post_request(self, user_id: UUID, data: dict):
        req = await self.repo.create_request(user_id, data)
        await self.repo.commit()
        return req

    async def respond_to_request(self, request_id: UUID, responder_id: UUID, message: str | None):
        resp = await self.repo.create_response(request_id, responder_id, message)

        req = await self.repo.db.get(WorkoutRequest, request_id)  # type: ignore
        author_id = req.user_id

        await self.repo.commit()

        try:
            payload = {
                "recipient_id": str(author_id),
                "type": "new_match_response",
                "data": {
                    "request_id": str(request_id),
                    "response_id": str(resp.id),
                    "responder_id": str(responder_id),
                    "message": message,
                    "time": req.preferred_time.isoformat() if req.preferred_time else None
                }
            }

            message_bytes = json.dumps(payload).encode('utf-8')

            await nc.publish("notification.match_request", message_bytes)
            logger.info(f"Notification sent to {author_id}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

        return resp

    async def handle_response(self, response_id: UUID, author_id: UUID, accept: bool):

        new_status = "accepted" if accept else "declined"
        success = await self.repo.update_response_status(response_id, new_status)

        if success and accept:
            pass

        await self.repo.commit()
        return success
