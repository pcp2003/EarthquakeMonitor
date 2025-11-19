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
    
    # Factory method to create an Earthquake instance from USGS data
    @classmethod
    def from_usgs_data(cls, data: dict) -> "Earthquake":
        """
        Create an Earthquake instance from USGS formatted data
        
        Args:
            data: Dictionary with USGS earthquake data (formatted by IngestionService)
            
        Returns:
            Earthquake instance
        """
        return cls(
            id=data["external_id"],
            time=data["time"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            depth=data["depth"],
            magnitude=data["magnitude"],
            magnitude_type=data["magnitude_type"],
            place=data["place"]
        )
    
    def to_dict(self) -> dict:
        """
        Convert earthquake instance to dictionary
        
        Returns:
            Dictionary representation of the earthquake
        """
        return {
            "id": self.id,
            "time": self.time,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "depth": float(self.depth) if self.depth else None,
            "magnitude": float(self.magnitude) if self.magnitude else None,
            "magnitude_type": self.magnitude_type,
            "place": self.place,
            "created_at": self.created_at
        }