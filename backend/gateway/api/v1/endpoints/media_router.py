from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from pydantic import BaseModel, Field
import logging

from ....core.security import get_current_user, TokenData
from ....core.http_client import http_client
from ....config import settings

logger = logging.getLogger(__name__)


class UploadUrlRequest(BaseModel):
    purpose: str
    content_type: str = Field(..., pattern=r"^image/(jpeg|png|webp)$")
    file_size: int = Field(..., gt=0, le=10_485_760)
    owner_id: str | None = None


class FileDeleteResponse(BaseModel):
    status: str
    message: str


router_media = APIRouter(prefix="/media", tags=["media"])


@router_media.post("/upload-url", response_model=dict)
async def get_upload_url(
    request: Request,
    data: UploadUrlRequest,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[GET_UPLOAD_URL] User: {current_user.user_id}, Purpose: {data.purpose}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    payload = data.model_dump()
    payload["owner_id"] = current_user.user_id
    
    media_response = await http_client.post(
        f"{settings.media_service_url}/api/v1/media/upload-url",
        json=payload,
        headers=headers
    )
    
    if not media_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Media service unavailable"
        )
    
    return media_response


@router_media.delete("/{file_key:path}", response_model=FileDeleteResponse)
async def delete_file(
    request: Request,
    file_key: str,
    owner_id: str | None = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"[DELETE_FILE] User: {current_user.user_id}, File: {file_key}")
    
    auth_header = request.headers.get("authorization")
    headers = {"authorization": auth_header} if auth_header else None
    
    params = {
        "owner_id": current_user.user_id
    }
    
    media_response = await http_client.delete(
        f"{settings.media_service_url}/api/v1/media/{file_key}",
        params=params,
        headers=headers
    )
    
    if not media_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return media_response
