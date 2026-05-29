from fastapi import APIRouter, HTTPException, Query
from ....utils.nats_client import NatsRpcClient

router = APIRouter(prefix="/meetups", tags=["meetups"])

# Получаем singleton экземпляр NATS клиента
nats = NatsRpcClient.get_instance()


@router.get("/my", response_model=dict)
async def get_my_meetups(user_id: int = Query(1, description="ID пользователя")):
    """
    GET /meetups/my?user_id=123
    
    Получить мероприятия, на которые записан пользователь
    Запрашивает данные из forum_service через NATS
    """
    if not nats.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"error": "Сервис мероприятий недоступен"}
        )
    
    meetups = await nats.get_user_meetups(user_id)
    return {
        "user_id": user_id,
        "meetups": meetups,
        "count": len(meetups)
    }


@router.get("/{meetup_id}", response_model=dict)
async def get_meetup_details(meetup_id: int):
    """
    GET /meetups/123
    
    Получить детали конкретного мероприятия
    """
    if not nats.is_connected:
        raise HTTPException(status_code=503, detail={"error": "Сервис мероприятий недоступен"})
    
    meetup = await nats.get_meetup_details(meetup_id)
    if not meetup:
        raise HTTPException(status_code=404, detail={"error": "Мероприятие не найдено"})
    
    return {"data": meetup}


@router.post("/{meetup_id}/join", response_model=dict)
async def join_meetup(
    meetup_id: int,
    user_id: int = Query(..., description="ID пользователя")
):
    """
    POST /meetups/123/join?user_id=456
    
    Присоединиться к мероприятию
    Отправляет запрос в forum_service через NATS
    """
    if not nats.is_connected:
        raise HTTPException(status_code=503, detail={"error": "Сервис мероприятий недоступен"})
    
    result = await nats.join_meetup(meetup_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=503,
            detail={"error": "Ошибка при подключении к сервису мероприятий"}
        )
    
    # Проверяем статус ответа от forum_service
    if result.get("ok") is False:
        error_msg = result.get("error", "Неизвестная ошибка")
        status_code = result.get("status_code", 400)
        raise HTTPException(status_code=status_code, detail={"error": error_msg})
    
    return {
        "message": "Вы успешно записаны на мероприятие",
        "meetup_id": meetup_id,
        "user_id": user_id
    }


@router.delete("/{meetup_id}/leave", response_model=dict)
async def leave_meetup(
    meetup_id: int,
    user_id: int = Query(..., description="ID пользователя")
):
    """
    DELETE /meetups/123/leave?user_id=456
    
    Покинуть мероприятие
    """
    if not nats.is_connected:
        raise HTTPException(status_code=503, detail={"error": "Сервис мероприятий недоступен"})
    
    result = await nats.leave_meetup(meetup_id, user_id)
    
    if not result:
        raise HTTPException(
            status_code=503,
            detail={"error": "Ошибка при подключении к сервису мероприятий"}
        )
    
    if result.get("ok") is False:
        error_msg = result.get("error", "Неизвестная ошибка")
        status_code = result.get("status_code", 404)
        raise HTTPException(status_code=status_code, detail={"error": error_msg})
    
    return {
        "message": "Вы снялись с мероприятия",
        "meetup_id": meetup_id,
        "user_id": user_id
    }


@router.get("/nearby/search", response_model=dict)
async def search_meetups_nearby(
    lat: float = Query(..., description="Широта"),
    lng: float = Query(..., description="Долгота"),
    radius_m: int = Query(2000, description="Радиус поиска в метрах")
):
    """
    GET /meetups/nearby/search?lat=52.965&lng=36.078&radius_m=2000
    
    Найти мероприятия поблизости от координат
    """
    if not nats.is_connected:
        raise HTTPException(status_code=503, detail={"error": "Сервис мероприятий недоступен"})
    
    meetups = await nats.search_meetups_by_location(lat, lng, radius_m)
    return {
        "location": {"lat": lat, "lng": lng},
        "radius_m": radius_m,
        "meetups": meetups,
        "count": len(meetups)
    }
