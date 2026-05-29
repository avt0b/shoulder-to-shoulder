from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class PlaceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    address: str
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    emoji: str = Field(default="📍")
    category: str = "park"
    image: Optional[str] = None
    gallery: Optional[List[str]] = None
    is_anonymous: bool
    activity_type: str
    noise_level: int
    light_availability: int
    conveniences_availability: bool


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str]
    lat: float
    lon: float
    address: str
    rating: float
    emoji: str
    category: str
    image: Optional[str]
    gallery: Optional[List[str]]
    is_anonymous: bool
    activity_type: str
    noise_level: int
    light_availability: int
    conveniences_availability: bool



class MeetupCreate(BaseModel):
    name: str
    time: str
    level: str
    max_participants: int = 8
    place_id: int
    created_by: int


class MeetupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    time: str
    level: str
    participants_count: int
    max_participants: int
    place: Optional[PlaceResponse]
    avatars: List[str]
    moreCount: Optional[int] = None
    isJoined: Optional[bool] = False


class RouteStep(BaseModel):
    instruction: str
    distance: float
    duration: float


class RouteResponse(BaseModel):
    distance: float
    duration: float
    geometry: dict
    steps: List[RouteStep]


class NearbyPlaceResponse(PlaceResponse):
    distance: float
