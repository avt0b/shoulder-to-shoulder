# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import List
# from models.schemas import (
#     SportsGroundCreate,
#     SportsGroundUpdate,
#     SportsGroundResponse,
# )
# from services.sports_ground_service import SportsGroundService
# from database import get_db_session

# router = APIRouter(prefix="/sports-grounds", tags=["sports-grounds"])


# @router.post("", response_model=SportsGroundResponse, status_code=201)
# async def create_sports_ground(
#     ground_data: SportsGroundCreate,
#     user_id: str = Query(..., description="ID текущего пользователя"),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Создать новую спортивную площадку"""
#     service = SportsGroundService(db)
#     return await service.create_ground(ground_data, user_id)


# @router.get("/{ground_id}", response_model=SportsGroundResponse)
# async def get_sports_ground(
#     ground_id: int,
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Получить спортивную площадку по ID"""
#     service = SportsGroundService(db)
#     ground = await service.get_ground(ground_id)
#     if not ground:
#         raise HTTPException(status_code=404, detail="Площадка не найдена")
#     return ground


# @router.get("", response_model=List[SportsGroundResponse])
# async def list_sports_grounds(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=100),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Получить список всех активных спортивных площадок"""
#     service = SportsGroundService(db)
#     return await service.get_all_grounds(skip=skip, limit=limit)


# @router.get("/search/nearby", response_model=List[SportsGroundResponse])
# async def search_nearby_grounds(
#     center_lat: float = Query(..., ge=-90, le=90, description="Широта центра поиска"),
#     center_lon: float = Query(..., ge=-180, le=180, description="Долгота центра поиска"),
#     distance_km: float = Query(5.0, ge=0.1, le=50.0, description="Радиус поиска в км"),
#     activity_type: str = Query(None, description="Тип активности"),
#     noise_level: str = Query(None, description="Уровень шума"),
#     has_lighting: bool = Query(None, description="Требуется ли освещение"),
#     limit: int = Query(50, ge=1, le=100),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Найти спортивные площадки рядом с указанными координатами"""
#     service = SportsGroundService(db)
#     return await service.search_nearby_grounds(
#         center_lat=center_lat,
#         center_lon=center_lon,
#         distance_km=distance_km,
#         activity_type=activity_type,
#         noise_level=noise_level,
#         has_lighting=has_lighting,
#         limit=limit,
#     )


# @router.get("/top/popular", response_model=List[SportsGroundResponse])
# async def get_popular_grounds(
#     limit: int = Query(20, ge=1, le=100),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Получить популярные спортивные площадки по рейтингу"""
#     service = SportsGroundService(db)
#     return await service.get_popular_grounds(limit=limit)


# @router.patch("/{ground_id}", response_model=SportsGroundResponse)
# async def update_sports_ground(
#     ground_id: int,
#     update_data: SportsGroundUpdate,
#     user_id: str = Query(..., description="ID текущего пользователя"),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Обновить данные спортивной площадки"""
#     service = SportsGroundService(db)
#     try:
#         ground = await service.update_ground(ground_id, update_data, user_id)
#         if not ground:
#             raise HTTPException(status_code=404, detail="Площадка не найдена")
#         return ground
#     except PermissionError:
#         raise HTTPException(status_code=403, detail="Нет прав для редактирования")


# @router.post("/{ground_id}/moderate", response_model=SportsGroundResponse)
# async def moderate_sports_ground(
#     ground_id: int,
#     is_approved: bool = Query(..., description="Одобрить или отклонить"),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Модерировать спортивную площадку (только для админов)"""
#     service = SportsGroundService(db)
#     ground = await service.moderate_ground(ground_id, is_approved)
#     if not ground:
#         raise HTTPException(status_code=404, detail="Площадка не найдена")
#     return ground


# @router.post("/{ground_id}/visit")
# async def increment_visits(
#     ground_id: int,
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Увеличить счётчик посещений площадки"""
#     service = SportsGroundService(db)
#     ground = await service.increment_visits(ground_id)
#     if not ground:
#         raise HTTPException(status_code=404, detail="Площадка не найдена")
#     return {"message": "Посещение учтено", "visits_count": ground.visits_count}


# @router.patch("/{ground_id}/rating")
# async def update_rating(
#     ground_id: int,
#     rating: float = Query(..., ge=0.0, le=5.0, description="Новый рейтинг"),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Обновить рейтинг спортивной площадки"""
#     service = SportsGroundService(db)
#     try:
#         ground = await service.update_rating(ground_id, rating)
#         if not ground:
#             raise HTTPException(status_code=404, detail="Площадка не найдена")
#         return {"message": "Рейтинг обновлён", "rating": ground.rating}
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/moderation/pending", response_model=List[SportsGroundResponse])
# async def get_pending_moderation(
#     limit: int = Query(50, ge=1, le=100),
#     db: AsyncSession = Depends(get_db_session),
# ):
#     """Получить площадки, ожидающие модерации"""
#     service = SportsGroundService(db)
#     return await service.get_pending_moderation(limit=limit)
