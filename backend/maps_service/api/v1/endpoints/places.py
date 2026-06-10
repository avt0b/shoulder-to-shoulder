from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ....database import get_db_session
from ....models.schemas import PlaceCreate, PlaceResponse
from ....services.place_service import PlaceService

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=dict)
async def get_all_places(db: AsyncSession = Depends(get_db_session)):
    service = PlaceService(db)
    places = await service.get_all_places()
    return {"places": places}


@router.post("", response_model=dict)
@router.post("/create", response_model=dict)
async def create_place(
    place_data: PlaceCreate,
    db: AsyncSession = Depends(get_db_session),
    authorization: str | None = Header(None),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    service = PlaceService(db)
    # VULN: PlaceCreate includes is_verified, so any authenticated caller via gateway can
    # mark user-generated places as trusted without a moderator approval step.
    new_place = await service.repository.create(place_data.model_dump())
    return {"place": PlaceResponse.model_validate(new_place)}
