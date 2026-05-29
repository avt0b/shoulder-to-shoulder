from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..models.schemas import MeetupResponse
from ..repositories.meetup_repository import MeetupRepository


class MeetupService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = MeetupRepository(db_session)
    
    async def get_user_meetups(self, user_id: int) -> List[dict]:
        meetups = await self.repository.get_by_user(user_id)
        result = []
        
        for meetup in meetups:
            place = meetup.place
            result.append({
                "id": meetup.id,
                "name": meetup.name,
                "time": meetup.time,
                "locationShort": place.name if place else "N/A",
                "location": place.address if place else "N/A",
                "level": meetup.level,
                "participants": meetup.participants_count,
                "maxParticipants": meetup.max_participants,
                "isJoined": user_id in (meetup.participants or []),
                "avatars": meetup.avatars or [],
                "moreCount": max(0, (meetup.participants_count or 0) - len(meetup.avatars or [])),
            })
        
        return result
    
    async def join_meetup(self, meetup_id: int, user_id: int) -> dict:
        meetup = await self.repository.get_by_id(meetup_id)
        if not meetup:
            raise ValueError("Meetup not found")
        
        if user_id in (meetup.participants or []):
            raise ValueError("Already joined")
        
        if meetup.participants_count >= meetup.max_participants:
            raise ValueError("No free spots")
        
        updated = await self.repository.add_participant(meetup_id, user_id)
        
        return {
            "success": True,
            "participants": updated.participants_count,
            "maxParticipants": updated.max_participants,
        }
    
    async def leave_meetup(self, meetup_id: int, user_id: int) -> dict:
        meetup = await self.repository.get_by_id(meetup_id)
        if not meetup:
            raise ValueError("Meetup not found")
        
        updated = await self.repository.remove_participant(meetup_id, user_id)
        if not updated:
            raise ValueError("Not joined")
        
        return {
            "success": True,
            "participants": updated.participants_count,
            "maxParticipants": updated.max_participants,
        }
