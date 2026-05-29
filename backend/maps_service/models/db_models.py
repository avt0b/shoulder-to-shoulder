import uuid

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, Index, JSON, Table, ForeignKey, CheckConstraint, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


# placement_association = Table(
#     'placement_association',
#     Base.metadata,
#     Column('meetup_id', Integer, ForeignKey('meetups.id')),
#     Column('user_id', Integer)
# )


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

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # meetups = relationship("Meetup", back_populates="place", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_place_coordinates', 'lat', 'lon'),
        Index('idx_place_category', 'category'),
        CheckConstraint('noise_level >= 0 AND noise_level <= 10', name='check_noise_level_range'),
        CheckConstraint('light_availability >= 0 AND light_availability <= 10', name='check_light_availability_range'),
    )


#доделать связи обсудить с Ромой!!

# class Meetup(Base):
#     __tablename__ = "meetups"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     time = Column(String(50), nullable=False)
#     level = Column(String(50), default="Открыто")
#     max_participants = Column(Integer, default=8)
#     participants_count = Column(Integer, default=1)
    
#     place_id = Column(Integer, ForeignKey('places.id', ondelete='CASCADE'), nullable=False)
#     place = relationship("Place", back_populates="meetups")
    
#     participants = Column(JSONB, server_default='[]', default=lambda: [])
#     avatars = Column(JSONB, server_default='[]', default=lambda: [])
    
#     created_by = Column(Integer, nullable=False)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
#     participants_list = relationship(
#         "User",
#         secondary=placement_association,
#         back_populates="meetups"
#     )
    
#     __table_args__ = (
#         Index('idx_meetup_created_by', 'created_by'),
#         Index('idx_meetup_place_id', 'place_id'),
#     )