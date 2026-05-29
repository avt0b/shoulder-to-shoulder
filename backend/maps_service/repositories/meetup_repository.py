from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from models.db_models import Meetup


class MeetupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self) -> List[Meetup]:
        stmt = select(Meetup)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_id(self, meetup_id: int) -> Optional[Meetup]:
        stmt = select(Meetup).where(Meetup.id == meetup_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_user(self, user_id: int) -> List[Meetup]:
        stmt = select(Meetup).where(Meetup.created_by == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, meetup_data: dict) -> Meetup:
        db_meetup = Meetup(**meetup_data)
        self.session.add(db_meetup)
        await self.session.commit()
        await self.session.refresh(db_meetup)
        return db_meetup
    
    async def add_participant(self, meetup_id: int, user_id: int) -> Optional[Meetup]:
        meetup = await self.get_by_id(meetup_id)
        if not meetup:
            return None
        
        if user_id in meetup.participants:
            return None
        
        meetup.participants.append(user_id)
        meetup.participants_count = len(meetup.participants)
        
        await self.session.commit()
        await self.session.refresh(meetup)
        return meetup
    
    async def remove_participant(self, meetup_id: int, user_id: int) -> Optional[Meetup]:
        meetup = await self.get_by_id(meetup_id)
        if not meetup or user_id not in meetup.participants:
            return None
        
        meetup.participants.remove(user_id)
        meetup.participants_count = len(meetup.participants)
        
        await self.session.commit()
        await self.session.refresh(meetup)
        return meetup
