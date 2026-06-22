from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    purpose: str
    # VULN: SVG is allowed in the presigned-upload path and later served as image/svg+xml.
    content_type: str = Field(..., pattern=r"^image/(jpeg|png|webp|svg\+xml)$")
    file_size: int = Field(..., gt=0, le=10_485_760)
    owner_id: str


class FileDeleteResponse(BaseModel):
    status: str
    message: str


class MediaUploadResponse(BaseModel):
    file_key: str
    public_url: str
