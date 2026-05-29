from fastapi import APIRouter, Query, HTTPException
from typing import List
from pydantic import BaseModel

from ....services.osrm_service import OSRMService
from ....utils.security_route import get_calculator, RouteData

router = APIRouter(prefix="/route", tags=["routes"])


@router.get("", response_model=dict)
async def get_route(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: float = Query(...),
    end_lng: float = Query(...),
):
    """Простой маршрут без анализа безопасности"""
    try:
        route_data = OSRMService.get_route(start_lat, start_lng, end_lat, end_lng)
        return route_data
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Не удалось построить маршрут"})


@router.get("/safe", response_model=dict)
async def get_safe_route(
    start_lat: float = Query(..., description="Широта начальной точки"),
    start_lng: float = Query(..., description="Долгота начальной точки"),
    end_lat: float = Query(..., description="Широта конечной точки"),
    end_lng: float = Query(..., description="Долгота конечной точки")
):
    """
    GET /api/v1/route/safe?start_lat=52.97&start_lng=36.06&end_lat=52.98&end_lng=36.07
    
    Получить безопасный маршрут с анализом:
    - Типов дорог (из OpenStreetMap)
    - Наличия уличного освещения
    - Уличных фонарей
    - AI комментарий о безопасности
    """
    try:
        calculator = get_calculator()
        analysis = await calculator.calculate_safe_route(start_lat, start_lng, end_lat, end_lng)
        
        def route_to_dict(route: RouteData) -> dict:
            return {
                "coordinates": [{"lat": lat, "lng": lon} for lat, lon in route.coordinates],
                "distance_m": route.distance_m,
                "risk_score": route.risk_score,
                "highway_type": route.highway_type
            }
        
        return {
            "ok": True,
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng},
            "safest_route": route_to_dict(analysis.safest_route),
            "shortest_route": route_to_dict(analysis.shortest_route),
            "ai_comment": analysis.ai_comment
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": str(e)}
        )
