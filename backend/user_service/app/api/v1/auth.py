"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status
from fastapi import Depends

from backend.user_service.app.core.dependencies import get_user_repository
from backend.user_service.app.domain.repositories.user_repository import UserRepository
from backend.user_service.app.domain.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    auth_service: UserRepository = Depends(get_user_repository),
) -> TokenResponse:
    """Register a new user."""

    try:
        return await auth_service.register_user(
            phone_number=user_data.phone_number,
            password=user_data.password,
            display_name=user_data.display_name,
            email=user_data.email,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации",
        ) from e


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLoginRequest,
    auth_service: UserRepository = Depends(get_user_repository),
) -> TokenResponse:
    """Login user by phone number and password."""

    try:
        return await auth_service.authenticate_user(
            phone_number=login_data.phone_number,
            password=login_data.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при входе",
        ) from e
