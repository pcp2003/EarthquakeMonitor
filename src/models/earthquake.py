from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, TIMESTAMP, DECIMAL, Text, Index
from sqlalchemy.sql import func

from .base import Base


class Earthquake(Base):
    __tablename__ = "earthquakes"
    
    id = Column(String(50), primary_key=True, comment="USGS unique identifier")
    time = Column(TIMESTAMP(timezone=False), nullable=False, comment="Earthquake occurrence time (UTC)")
    latitude = Column(DECIMAL(9, 6), nullable=False, comment="Latitude coordinate (-90 to 90)")
    longitude = Column(DECIMAL(9, 6), nullable=False, comment="Longitude coordinate (-180 to 180)")
    depth = Column(DECIMAL(6, 2), nullable=True, comment="Depth in kilometers")
    magnitude = Column(DECIMAL(3, 2), nullable=True, comment="Earthquake magnitude")
    magnitude_type = Column(String(10), nullable=True, comment="Magnitude type (mb, ml, mw, etc)")
    place = Column(Text, nullable=True, comment="Location description")
    
    created_at = Column(
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(),
        comment="Record insertion timestamp"
    )
    
    __table_args__ = (
        Index('idx_earthquakes_time', 'time'),
        Index('idx_earthquakes_magnitude', 'magnitude'),
        Index('idx_earthquakes_location', 'latitude', 'longitude'),
    )
    
    def __repr__(self) -> str:
        return f"<Earthquake(id='{self.id}', magnitude={self.magnitude}, place='{self.place}')>"
    
