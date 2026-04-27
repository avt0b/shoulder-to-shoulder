from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple
from ..models.schemas import PlaceResponse
from ..repositories.place_repository import PlaceRepository


class PlaceService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = PlaceRepository(db_session)
    
    async def get_all_places(self) -> List[PlaceResponse]:
        places = await self.repository.get_all()
        print(places)
        return [PlaceResponse.model_validate(p) for p in places]
    
    async def get_place(self, place_id: int) -> Optional[PlaceResponse]:
        place = await self.repository.get_by_id(place_id)
        if place:
            return PlaceResponse.model_validate(place)
        return None
    
    async def get_nearby_places(self, lat: float, lon: float, 
                                radius_m: float = 2000) -> List[dict]:
        places = await self.repository.get_nearby(lat, lon, radius_m)
        result = []
        
        for place in places:
            distance = self._calculate_distance(lat, lon, place.latitude, place.longitude)
            place_dict = PlaceResponse.model_validate(place).model_dump()
            place_dict["distance"] = int(distance * 1000)
            result.append(place_dict)
        
        return result
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
