from fastapi import APIRouter, Depends, HTTPException, status

from backend.user_service.app.api.dependencies import get_auth_service
from backend.user_service.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.user_service.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await auth_service.register_user(
            phone_number=data.phone_number,
            password=data.password,
            display_name=data.display_name,
            email=data.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/login", response_model=TokenResponse)
async def login_user(
    data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await auth_service.authenticate_user(
            phone_number=data.phone_number,
            password=data.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
