from uuid import UUID
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event, EventStatus
from app.models.participant import EventParticipant, ParticipantStatus


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = select(Event).where(Event.id == event_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_active_participants(self, event_id: UUID) -> int:
        stmt = select(func.count()).select_from(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.status.in_([ParticipantStatus.JOINED, ParticipantStatus.CHECKED_IN])
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def join(self, event_id: UUID, user_id: str) -> bool:
        stmt = select(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id,
            EventParticipant.status != ParticipantStatus.CANCELLED
        )
        if (await self.db.execute(stmt)).scalar_one_or_none():
            return False

        self.db.add(EventParticipant(event_id=event_id, user_id=user_id))
        await self.db.flush()
        return True

    async def checkin(self, event_id: UUID, user_id: str) -> bool:
        stmt = update(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id,
            EventParticipant.status == ParticipantStatus.JOINED
        ).values(status=ParticipantStatus.CHECKED_IN).returning(EventParticipant.id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def mark_participant_missed(self, event_id: UUID, user_id: str) -> bool:
        stmt = update(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.user_id == user_id,
            EventParticipant.status == ParticipantStatus.JOINED
        ).values(status=ParticipantStatus.MISSED).returning(EventParticipant.id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_missed_participants(self, event_id: UUID) -> list[str]:
        stmt = select(EventParticipant.user_id).where(
            EventParticipant.event_id == event_id,
            EventParticipant.status == ParticipantStatus.JOINED
        )
        result = await self.db.execute(stmt)
        return [str(r) for r in result.scalars().all()]

    async def update_status(self, event_id: UUID, status: EventStatus):
        await self.db.execute(
            update(Event).where(Event.id == event_id).values(status=status.value)
        )