from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.nats_client import request_nats

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    resp = await request_nats("auth.validate_token", {"token": token})
    if not resp.get("ok"):
        raise HTTPException(status_code=401, detail=resp.get("error", "Authentication failed"))
    return resp["data"]["user_id"]
