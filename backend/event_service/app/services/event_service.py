import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from backend.event_service.app.repositories.event_repository import EventRepository
from backend.event_service.app.core.nats_client import publish_event
from backend.event_service.app.models.event import Event, EventStatus
from sqlalchemy import select

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def create_event(self, host_id: str, data: dict) -> Event:
        now = datetime.now(timezone.utc)
        if data["start_time"].replace(tzinfo=timezone.utc) < now + timedelta(minutes=30):
            raise ValueError("Event must be scheduled at least 30 minutes in advance")

        return await self.repo.create(Event(host_id=host_id, **data))

    async def join_event(self, user_id: str, event_id: UUID) -> bool:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        if str(event.host_id) == str(user_id):
            raise ValueError("Host is already a participant by default")

        if event.status != EventStatus.PENDING:
            raise ValueError("Event is not open for joining")

        if await self.repo.count_active_participants(event_id) >= event.max_participants:
            raise ValueError("Event is full")

        success = await self.repo.join(event_id, user_id)

        if success:
            try:
                await publish_event("event.user_joined", {
                    "event_id": str(event_id),
                    "host_id": str(event.host_id),
                    "user_id": str(user_id),
                    "event_title": event.title,
                    "joined_at": datetime.now(timezone.utc).isoformat()
                })

                logger.info(f"Published event.user_joined for host {event.host_id} (user {user_id} joined)")

            except Exception as e:
                logger.error(f"Failed to publish user_joined event: {e}")
        return success

    async def checkin_event(self, user_id: str, event_id: UUID) -> dict:
        event = await self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if event.status not in (EventStatus.PENDING, EventStatus.ACTIVE):
            raise ValueError("Event is not active")

        now = datetime.now(timezone.utc)
        start = event.start_time.replace(tzinfo=timezone.utc)
        if not (start - timedelta(minutes=15) <= now <= start + timedelta(minutes=45)):
            raise ValueError("Check-in window is closed")

        success = await self.repo.checkin(event_id, user_id)
        if not success:
            raise ValueError("Not registered or already checked in")

        await publish_event("workout.completed", {
            "user_id": user_id, "event_id": str(event_id), "success": True
        })
        return {"event_id": event_id, "user_id": user_id, "status": "checked_in", "message": "Attendance recorded"}

    async def get_expired_events(self) -> list[Event]:
        now = datetime.now(timezone.utc)
        stmt = select(Event).where(
            Event.status.in_([EventStatus.PENDING, EventStatus.ACTIVE]),
            Event.start_time + timedelta(minutes=Event.duration_minutes) < now
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_event(self, event_id: UUID, data: dict) -> Event | None:
        return await self.repo.update(event_id, data)

    async def delete_event(self, event_id: UUID) -> bool:
        return await self.repo.delete(event_id)

    async def list_events(self, **filters) -> dict:
        events, total = await self.repo.list_events(**filters)
        events_with_counts = []
        for e in events:
            count = await self.repo.count_participants(e.id)
            events_with_counts.append({
                "id": e.id,
                "host_id": e.host_id,
                "spot_id": e.spot_id,
                "title": e.title,
                "description": e.description,
                "max_participants": e.max_participants,
                "status": e.status,
                "start_time": e.start_time,
                "photo_url": e.photo_url,
                "created_at": e.created_at,
                "participant_count": count,
                "anonymous": e.anonymous
            })

        return {
            "events": events_with_counts,
            "total": total,
            "limit": filters.get("limit", 50),
            "offset": filters.get("offset", 0),
        }

    async def get_event_detail(self, event_id: UUID) -> dict | None:
        event = await self.repo.get_by_id(event_id)
        if not event:
            return None
        participant_ids = await self.repo.get_participant_ids(event_id)

        return {
            "id": event.id,
            "host_id": event.host_id,
            "spot_id": event.spot_id,
            "title": event.title,
            "description": event.description,
            "max_participants": event.max_participants,
            "status": event.status,
            "start_time": event.start_time,
            "photo_url": event.photo_url,
            "created_at": event.created_at,
            "participant_count": len(participant_ids),
            "participant_ids": participant_ids,
        }
