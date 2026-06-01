from fastapi import APIRouter, HTTPException, Query

from ....utils.security_route import RouteData, get_calculator

router = APIRouter(prefix="/route", tags=["routes"])


@router.get("/safe", response_model=dict)
async def get_safe_route(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    end_lat: float = Query(...),
    end_lng: float = Query(...),
):
    try:
        calculator = get_calculator()
        analysis = await calculator.calculate_safe_route(start_lat, start_lng, end_lat, end_lng)

        def route_to_dict(route: RouteData) -> dict:
            return {
                "coordinates": [{"lat": lat, "lng": lon} for lat, lon in route.coordinates],
                "distance_m": route.distance_m,
                "risk_score": route.risk_score,
                "highway_type": route.highway_type,
            }

        return {
            "ok": True,
            "start": {"lat": start_lat, "lng": start_lng},
            "end": {"lat": end_lat, "lng": end_lng},
            "safest_route": route_to_dict(analysis.safest_route),
            "shortest_route": route_to_dict(analysis.shortest_route),
            "ai_comment": analysis.ai_comment,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": str(e)},
        )
