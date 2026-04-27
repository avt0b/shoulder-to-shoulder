# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List, Optional
# from ..models.db_models import SportsGround, ActivityTypeEnum, NoiseLevel
# from ..models.schemas import SportsGroundCreate, SportsGroundUpdate, SportsGroundResponse
# from ..repositories.sports_ground_repository import SportsGroundRepository


# class SportsGroundService:
#     """Сервис для управления спортивными площадками"""
    
#     def __init__(self, db_session: AsyncSession):
#         self.db_session = db_session
#         self.repository = SportsGroundRepository(db_session)
    
#     async def create_ground(self, ground_data: SportsGroundCreate, user_id: str) -> SportsGroundResponse:
#         """Создать новую спортивную площадку"""
#         ground_dict = ground_data.dict()
#         ground_dict['created_by'] = user_id
#         ground_dict['is_moderated'] = False  # По умолчанию не модерируется
        
#         db_ground = SportsGround(**ground_dict)
#         self.db_session.add(db_ground)
#         await self.db_session.commit()
#         await self.db_session.refresh(db_ground)
        
#         return self._to_response(db_ground)
    
#     async def get_ground(self, ground_id: int) -> Optional[SportsGroundResponse]:
#         """Получить площадку по ID"""
#         ground = await self.repository.get_by_id(ground_id)
#         if ground:
#             return self._to_response(ground)
#         return None
    
#     async def get_all_grounds(self, skip: int = 0, limit: int = 50) -> List[SportsGroundResponse]:
#         """Получить все активные площадки"""
#         grounds = await self.repository.filter_by_criteria(
#             is_moderated=True,
#             is_active=True,
#             skip=skip,
#             limit=limit
#         )
#         return [self._to_response(g) for g in grounds]
    
#     async def search_nearby_grounds(self,
#                                    center_lat: float,
#                                    center_lon: float,
#                                    distance_km: float = 5.0,
#                                    activity_type: Optional[str] = None,
#                                    noise_level: Optional[str] = None,
#                                    has_lighting: Optional[bool] = None,
#                                    limit: int = 50) -> List[SportsGroundResponse]:
#         """
#         Поиск спортивных площадок рядом с указанными координатами
#         """
#         activity_enum = ActivityTypeEnum(activity_type) if activity_type else None
#         noise_enum = NoiseLevel(noise_level) if noise_level else None
        
#         grounds = await self.repository.get_nearby_and_filtered(
#             center_lat=center_lat,
#             center_lon=center_lon,
#             distance_km=distance_km,
#             activity_type=activity_enum,
#             noise_level=noise_enum,
#             has_lighting=has_lighting,
#             limit=limit
#         )
        
#         return [self._to_response(g) for g in grounds]
    
#     async def get_popular_grounds(self, limit: int = 20) -> List[SportsGroundResponse]:
#         """Получить популярные площадки по рейтингу"""
#         grounds = await self.repository.get_popular_by_rating(limit=limit)
#         return [self._to_response(g) for g in grounds]
    
#     async def update_ground(self, ground_id: int, update_data: SportsGroundUpdate, 
#                            user_id: str) -> Optional[SportsGroundResponse]:
#         """Обновить данные площадки"""
#         ground = await self.repository.get_by_id(ground_id)
#         if not ground:
#             return None
        
#         # Проверка прав (только автор или админ)
#         if ground.created_by != user_id:
#             raise PermissionError("Только автор может редактировать площадку")
        
#         # Обновление
#         update_dict = update_data.dict(exclude_unset=True)
#         for field, value in update_dict.items():
#             setattr(ground, field, value)
        
#         await self.db_session.commit()
#         await self.db_session.refresh(ground)
        
#         return self._to_response(ground)
    
#     async def moderate_ground(self, ground_id: int, is_approved: bool) -> Optional[SportsGroundResponse]:
#         """Модерировать площадку (одобрить или отклонить)"""
#         ground = await self.repository.get_by_id(ground_id)
#         if not ground:
#             return None
        
#         if is_approved:
#             ground.is_moderated = True
#             ground.is_active = True
#         else:
#             ground.is_active = False
        
#         await self.db_session.commit()
#         await self.db_session.refresh(ground)
        
#         return self._to_response(ground)
    
#     async def increment_visits(self, ground_id: int) -> Optional[SportsGroundResponse]:
#         """Увеличить счётчик посещений"""
#         ground = await self.repository.increment_visits(ground_id)
#         if ground:
#             return self._to_response(ground)
#         return None
    
#     async def update_rating(self, ground_id: int, new_rating: float) -> Optional[SportsGroundResponse]:
#         """Обновить рейтинг площадки"""
#         if not 0.0 <= new_rating <= 5.0:
#             raise ValueError("Рейтинг должен быть от 0.0 до 5.0")
        
#         ground = await self.repository.update_rating(ground_id, new_rating)
#         if ground:
#             return self._to_response(ground)
#         return None
    
#     async def get_pending_moderation(self, limit: int = 50) -> List[SportsGroundResponse]:
#         """Получить площадки, ожидающие модерации"""
#         grounds = await self.repository.get_pending_moderation(limit=limit)
#         return [self._to_response(g) for g in grounds]
    
#     @staticmethod
#     def _to_response(ground: SportsGround) -> SportsGroundResponse:
#         """Преобразовать модель БД в ответ API"""
#         return SportsGroundResponse.from_orm(ground)
