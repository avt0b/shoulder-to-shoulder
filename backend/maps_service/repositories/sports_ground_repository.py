from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from typing import List, Optional
from math import radians, sin, cos, sqrt, atan2
from ..models.db_models import SportsGround, ActivityTypeEnum, NoiseLevel
from .base_repository import BaseRepository


class SportsGroundRepository(BaseRepository[SportsGround]):
    """Репозиторий для работы со спортивными площадками"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SportsGround)
    
    async def get_by_coordinates(self, latitude: float, longitude: float, 
                                 distance_km: float = 5.0, 
                                 is_active: bool = True) -> List[SportsGround]:
        """
        Получить спортивные площадки по координатам с радиусом поиска.
        Использует формулу Хаверсина для расчёта расстояния.
        """
        stmt = select(SportsGround).where(SportsGround.is_active == is_active)
        result = await self.session.execute(stmt)
        all_grounds = result.scalars().all()
        
        # Фильтруем по расстоянию в Python (на практике лучше использовать PostGIS)
        filtered = []
        for ground in all_grounds:
            distance = self._haversine(latitude, longitude, ground.latitude, ground.longitude)
            if distance <= distance_km:
                filtered.append(ground)
        
        return filtered
    
    async def filter_by_criteria(self, 
                               activity_type: Optional[ActivityTypeEnum] = None,
                               noise_level: Optional[NoiseLevel] = None,
                               has_lighting: Optional[bool] = None,
                               has_changing_room: Optional[bool] = None,
                               has_benches: Optional[bool] = None,
                               has_restroom: Optional[bool] = None,
                               has_water: Optional[bool] = None,
                               is_moderated: bool = True,
                               is_active: bool = True,
                               skip: int = 0,
                               limit: int = 50) -> List[SportsGround]:
        """
        Фильтровать спортивные площадки по критериям
        """
        filters = [SportsGround.is_active == is_active]
        
        if is_moderated is not None:
            filters.append(SportsGround.is_moderated == is_moderated)
        
        if activity_type:
            filters.append(SportsGround.activity_type == activity_type)
        
        if noise_level:
            filters.append(SportsGround.noise_level == noise_level)
        
        if has_lighting is not None:
            filters.append(SportsGround.has_lighting == has_lighting)
        
        if has_changing_room is not None:
            filters.append(SportsGround.has_changing_room == has_changing_room)
        
        if has_benches is not None:
            filters.append(SportsGround.has_benches == has_benches)
        
        if has_restroom is not None:
            filters.append(SportsGround.has_restroom == has_restroom)
        
        if has_water is not None:
            filters.append(SportsGround.has_water == has_water)
        
        stmt = select(SportsGround).where(and_(*filters)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_popular_by_rating(self, limit: int = 20, skip: int = 0) -> List[SportsGround]:
        """Получить популярные площадки по рейтингу"""
        stmt = (
            select(SportsGround)
            .where(SportsGround.is_active == True)
            .order_by(SportsGround.rating.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_nearby_and_filtered(self,
                                     center_lat: float,
                                     center_lon: float,
                                     distance_km: float = 5.0,
                                     activity_type: Optional[ActivityTypeEnum] = None,
                                     noise_level: Optional[NoiseLevel] = None,
                                     has_lighting: Optional[bool] = None,
                                     limit: int = 50) -> List[SportsGround]:
        """Получить спортивные площадки по координатам и фильтрам одновременно"""
        # Сначала получаем по радиусу
        nearby = await self.get_by_coordinates(center_lat, center_lon, distance_km)
        
        # Затем применяем фильтры
        filtered = []
        for ground in nearby:
            if activity_type and ground.activity_type != activity_type:
                continue
            if noise_level and ground.noise_level != noise_level:
                continue
            if has_lighting is not None and ground.has_lighting != has_lighting:
                continue
            filtered.append(ground)
        
        return filtered[:limit]
    
    async def increment_visits(self, ground_id: int) -> Optional[SportsGround]:
        """Увеличить счётчик посещений"""
        ground = await self.get_by_id(ground_id)
        if ground:
            ground.visits_count += 1
            await self.session.commit()
            await self.session.refresh(ground)
        return ground
    
    async def update_rating(self, ground_id: int, new_rating: float) -> Optional[SportsGround]:
        """Обновить рейтинг площадки"""
        ground = await self.get_by_id(ground_id)
        if ground:
            ground.rating = max(0.0, min(5.0, new_rating))  # Ограничиваем от 0 до 5
            await self.session.commit()
            await self.session.refresh(ground)
        return ground
    
    async def get_pending_moderation(self, limit: int = 50) -> List[SportsGround]:
        """Получить площадки, ожидающие модерации"""
        stmt = (
            select(SportsGround)
            .where(SportsGround.is_moderated == False)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Вычислить расстояние между двумя точками на Земле в км.
        Используется формула Хаверсина.
        """
        R = 6371  # Радиус Земли в км
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
