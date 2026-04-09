from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user_id, get_user_service
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    PublicUserInfoResponse,
    RatingResponse, UserContactUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    profile = await user_service.get_user_by_id(current_user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
        data: UserProfileUpdateRequest,
        current_user_id: str = Depends(get_current_user_id),
        user_service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    update_data = data.model_dump(exclude_unset=True)
    profile = await user_service.update_profile(current_user_id, update_data)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/me/contact", response_model=dict)
async def update_my_contact_info(
        data: UserContactUpdateRequest,
        current_user_id: str = Depends(get_current_user_id),
        user_service: UserService = Depends(get_user_service),
) -> dict:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = await user_service.update_contact_info(current_user_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/me/rating", response_model=RatingResponse)
async def get_my_rating(
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
) -> RatingResponse:
    rating = await user_service.get_rating(current_user_id)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating


@router.get("/{user_id}/public", response_model=PublicUserInfoResponse)
async def get_public_user_info(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> PublicUserInfoResponse:
    info = await user_service.get_public_user_info(user_id)
    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return info