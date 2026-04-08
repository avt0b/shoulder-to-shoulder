"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, EmailStr, field_validator
import re


def validate_phone_number(phone: str) -> str:
    """Validate and normalize Russian phone number to E.164 format."""
    cleaned = re.sub(r'\D', '', phone)

    if len(cleaned) == 11 and cleaned.startswith('7'):
        return f"+{cleaned}"
    elif len(cleaned) == 10:
        return f"+7{cleaned}"
    else:
        raise ValueError("Неверный формат номера телефона. Используйте +7XXXXXXXXXX")


class UserRegisterRequest(BaseModel):
    phone_number: str
    password: str
    display_name: str
    email: EmailStr | None = None
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_number(v)


class UserLoginRequest(BaseModel):
    phone_number: str
    password: str
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_number(v)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):

    sub: str
    type: str
    exp: int | None = None