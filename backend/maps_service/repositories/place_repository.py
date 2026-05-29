from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List, Optional
from math import radians, sin, cos, sqrt, atan2

from ..models.db_models import Place


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self) -> List[Place]:
        stmt = select(Place)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_id(self, place_id: int) -> Optional[Place]:
        stmt = select(Place).where(Place.id == place_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def create(self, place_data: dict) -> Place:
        db_place = Place(**place_data)
        self.session.add(db_place)
        await self.session.commit()
        await self.session.refresh(db_place)
        return db_place
    
    async def get_nearby(self, lat: float, lon: float, radius_m: float = 2000) -> List[Place]:
        stmt = select(Place)
        result = await self.session.execute(stmt)
        all_places = result.scalars().all()
        
        nearby = []
        for place in all_places:
            distance = self._haversine(lat, lon, place.lat, place.lon)
            if distance <= radius_m / 1000:
                nearby.append((place, distance * 1000))
        
        nearby.sort(key=lambda x: x[1])
        return [place for place, _ in nearby]
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
