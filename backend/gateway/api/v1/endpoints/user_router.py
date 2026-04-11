from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import logging

from ....core.security import get_current_user, TokenData, create_access_token
from ....core.http_client import http_client
from ....config import settings

logger = logging.getLogger(__name__)


class UserRegisterRequest(BaseModel):
    phone_number: str
    password: str
    display_name: str
    email: Optional[EmailStr] = None


class UserLoginRequest(BaseModel):
    phone_number: str
    password: str


class UserProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18)
    fitness_level: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[dict] = None
    city: Optional[str] = Field(None, max_length=100)


class UserContactUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None


router_auth = APIRouter(prefix="/auth", tags=["authentication"])


@router_auth.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegisterRequest):
    logger.info(f"[REGISTER] Request: {data}")
    payload = {
        "phone_number": data.phone_number,
        "password": data.password,
        "display_name": data.display_name,
    }
    if data.email:
        payload["email"] = data.email
    logger.info(f"[REGISTER] Payload: {payload}")
    logger.info(f"[REGISTER] URL: {settings.user_service_url}/api/v1/auth/register")
    user_response = await http_client.post(
        f"{settings.user_service_url}/api/v1/auth/register",
        json=payload
    )
    logger.info(f"[REGISTER] Response: {user_response}")
    
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )
    
    return {
        "access_token": user_response.get("access_token"),
        "refresh_token": user_response.get("refresh_token"),
        "token_type": user_response.get("token_type", "bearer")
    }


@router_auth.post("/login", response_model=dict)
async def login(data: UserLoginRequest):
    logger.info(f"[LOGIN] Request: {data}")
    
    payload = {
        "phone_number": data.phone_number,
        "password": data.password
    }
    
    logger.info(f"[LOGIN] Payload: {payload}")
    
    user_response = await http_client.post(
        f"{settings.user_service_url}/api/v1/auth/login",
        json=payload
    )
    
    logger.info(f"[LOGIN] Response: {user_response}")
    
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )
    
    return {
        "access_token": user_response.get("access_token"),
        "refresh_token": user_response.get("refresh_token"),
        "token_type": user_response.get("token_type", "bearer")
    }



router_users = APIRouter(prefix="/users", tags=["users"])


@router_users.get("/me", response_model=dict)
async def get_me(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[GET_ME] User: {current_user.user_id}")
    
    # Forward the authorization token to user_service
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    user_profile = await http_client.get(
        f"{settings.user_service_url}/api/v1/users/me",
        headers=headers
    )
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return user_profile


@router_users.put("/me", response_model=dict)
async def update_me(
    request: Request,
    data: UserProfileUpdateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[UPDATE_ME] User: {current_user.user_id}")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Forward the authorization token to user_service
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    user_response = await http_client.put(
        f"{settings.user_service_url}/api/v1/users/me",
        json=update_data,
        headers=headers
    )
    
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )
    
    return user_response


@router_users.put("/me/contact", response_model=dict)
async def update_contact(
    request: Request,
    data: UserContactUpdateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[UPDATE_CONTACT] User: {current_user.user_id}")
    
    update_data = data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Forward the authorization token to user_service
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    user_response = await http_client.put(
        f"{settings.user_service_url}/api/v1/users/me/contact",
        json=update_data,
        headers=headers
    )
    
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )
    
    return user_response


@router_users.get("/me/rating", response_model=dict)
async def get_my_rating(
    request: Request,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[GET_RATING] User: {current_user.user_id}")
    
    # Forward the authorization token to user_service
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    rating = await http_client.get(
        f"{settings.user_service_url}/api/v1/users/me/rating",
        headers=headers
    )
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    return rating


@router_users.get("/{user_id}", response_model=dict)
async def get_public_user_info(user_id: str):
    logger.info(f"[GET_PUBLIC] User: {user_id}")
    print(user_id)
    user_info = await http_client.get(
        f"{settings.user_service_url}/api/v1/users/{user_id}"
    )
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_info
