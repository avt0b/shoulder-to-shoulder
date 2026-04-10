from datetime import datetime
from uuid import UUID
from sqlalchemy import select, update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.event_service.app.models.event import Event, EventStatus
from backend.event_service.app.models.participant import EventParticipant, ParticipantStatus


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: Event) -> Event:
        self.db.add(event)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = select(Event).where(Event.id == event_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_participant_ids(self, event_id: UUID, exclude_host_id: UUID | None = None) -> list[UUID]:
        stmt = select(EventParticipant.user_id).where(
            EventParticipant.event_id == event_id,
            EventParticipant.status != ParticipantStatus.CANCELLED
        )
        if exclude_host_id:
            stmt = stmt.where(EventParticipant.user_id != exclude_host_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

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
        await self.db.commit()
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

    async def update_status(self, event_id: UUID, status: str) -> bool:
        status_value = status.value if hasattr(status, "value") else status
        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(status=status_value, updated_at=func.now())
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def update(self, event_id: UUID, data: dict) -> Event | None:
        if not data: return None
        stmt = (
            update(Event).where(Event.id == event_id)
            .values(**data, updated_at=func.now())
            .returning(Event)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, event_id: UUID) -> bool:
        stmt = delete(Event).where(Event.id == event_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def list_events(
            self,
            limit: int = 50,
            offset: int = 0,
            status_filter: str | None = None,
            host_id: UUID | None = None,
            spot_id: UUID | None = None,
            start_time_from: datetime | None = None,
            start_time_to: datetime | None = None,
    ) -> tuple[list[Event], int]:

        stmt = select(Event)

        if status_filter:
            stmt = stmt.where(Event.status == status_filter)
        if host_id:
            stmt = stmt.where(Event.host_id == host_id)
        if spot_id:
            stmt = stmt.where(Event.spot_id == spot_id)
        if start_time_from:
            stmt = stmt.where(Event.start_time >= start_time_from)
        if start_time_to:
            stmt = stmt.where(Event.start_time <= start_time_to)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()

        stmt = stmt.order_by(Event.start_time.asc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return events, total

    async def count_participants(self, event_id: UUID) -> int:
        stmt = select(func.count()).select_from(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.status != "cancelled"
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
