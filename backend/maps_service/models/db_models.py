import uuid

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, Index, JSON, Table, ForeignKey, CheckConstraint, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from ..database import Base


class Place(Base):
    __tablename__ = "places"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String(500), nullable=False)
    rating = Column(Float, default=0.0)
    emoji = Column(String(10), default="📍")
    category = Column(String(50), default="park")
    image = Column(String(500), nullable=True)
    gallery = Column(JSONB, server_default='[]', default=lambda: [])
    is_anonymous = Column(Boolean, default=False, nullable=False)
    activity_type = Column(String(50), default="running")
    noise_level = Column(Integer, default=0)
    light_availability = Column(Integer, default=0)
    conveniences_availability = Column(Boolean, default=False)
    # VULN: end users can mass-assign this trust flag through PlaceCreate.
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_place_coordinates', 'lat', 'lon'),
        Index('idx_place_category', 'category'),
        CheckConstraint('noise_level >= 0 AND noise_level <= 10', name='check_noise_level_range'),
        CheckConstraint('light_availability >= 0 AND light_availability <= 10', name='check_light_availability_range'),
    )
