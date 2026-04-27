from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ....models.schemas import PlaceResponse, PlaceCreate
from ....services.place_service import PlaceService
from ....database import get_db_session

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=dict)
async def get_all_places(db: AsyncSession = Depends(get_db_session)):
    service = PlaceService(db)
    places = await service.get_all_places()
    return {"places": places}


@router.get("/search/nearby", response_model=dict)
async def get_nearby_places(
    lat: float = Query(...),
    lng: float = Query(...),
    radius: float = Query(2000),
    db: AsyncSession = Depends(get_db_session),
):
    service = PlaceService(db)
    places = await service.get_nearby_places(lat, lng, radius)
    return {"places": places}


@router.get("/{place_id}", response_model=dict)
async def get_place(place_id: int, db: AsyncSession = Depends(get_db_session)):
    service = PlaceService(db)
    place = await service.get_place(place_id)
    if not place:
        raise HTTPException(status_code=404, detail={"error": "Место не найдено"})
    return {"place": place}

@router.post("/create", response_model=dict)
async def create_place(
    place_data: PlaceCreate,
    db: AsyncSession = Depends(get_db_session)
):
    service = PlaceService(db)
    new_place = await service.repository.create(place_data.model_dump())
    return {"place": PlaceResponse.model_validate(new_place)}