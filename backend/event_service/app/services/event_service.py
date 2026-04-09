import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from app.repositories.event_repository import EventRepository
from app.core.nats_client import publish_event
from app.models.event import Event, EventStatus

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
        if event.status != EventStatus.PENDING:
            raise ValueError("Event is not open for joining")
        if await self.repo.count_active_participants(event_id) >= event.max_participants:
            raise ValueError("Event is full")
        return await self.repo.join(event_id, user_id)

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

    async def complete_expired_events(self):
        """Авто-завершение прошедших сборов + штрафы за неявку"""
        now = datetime.now(timezone.utc)
        from sqlalchemy import select
        stmt = select(Event).where(
            Event.status.in_([EventStatus.PENDING, EventStatus.ACTIVE]),
            Event.start_time + timedelta(minutes=Event.duration_minutes) < now
        )
        result = await self.repo.db.execute(stmt)
        events = result.scalars().all()

        for event in events:
            missed_users = await self.repo.get_missed_participants(event.id)
            for uid in missed_users:
                await self.repo.mark_participant_missed(event.id, uid)
                await publish_event("workout.missed", {
                    "user_id": uid, "event_id": str(event.id), "success": False
                })

            await self.repo.update_status(event.id, EventStatus.COMPLETED)
        await self.repo.db.commit()
        logger.info(
            f"Auto-completed {len(events)} events, penalized {sum(1 for _ in missed_users) if 'missed_users' in locals() else 0} users")
