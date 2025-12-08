from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, ConfigDict


class EarthquakeBase(BaseModel):
    """Base earthquake schema with common fields"""
    
    time: datetime = Field(
        ..., 
        description="Earthquake occurrence time (UTC)"
    )
    latitude: float = Field(
        ..., 
        ge=-90.0, 
        le=90.0,
        description="Latitude coordinate (-90 to 90)"
    )
    longitude: float = Field(
        ..., 
        ge=-180.0, 
        le=180.0,
        description="Longitude coordinate (-180 to 180)"
    )
    depth: Optional[float] = Field(
        None,
        description="Depth in kilometers (can be negative for very shallow events)"
    )
    magnitude: Optional[float] = Field(
        None,
        description="Earthquake magnitude (can be negative for very weak seismic events)"
    )
    magnitude_type: Optional[str] = Field(
        None, 
        max_length=10,
        description="Magnitude type (mb, ml, mw, etc)"
    )
    place: Optional[str] = Field(
        None,
        description="Location description"
    )


class EarthquakeResponse(EarthquakeBase):
    """Schema for earthquake API responses"""
    
    id: str = Field(description="USGS unique identifier")
    created_at: datetime = Field(description="Record insertion timestamp")

    model_config = ConfigDict(from_attributes=True)


class EarthquakeListResponse(BaseModel):
    """Schema for paginated earthquake list responses"""
    
    earthquakes: List[EarthquakeResponse] = Field(
        description="List of earthquake records"
    )
    total: int = Field(
        description="Total number of records matching the filter"
    )
    page: int = Field(
        description="Current page number"
    )
    limit: int = Field(
        description="Number of records per page"
    )
    has_next: bool = Field(
        description="Whether there are more pages available"
    )
    has_previous: bool = Field(
        description="Whether there are previous pages available"
    )

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (starts at 1)"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Number of records per page (max 1000)"
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.limit


class EarthquakeFilter(BaseModel):
    """Schema for filtering earthquake records"""
    
    min_magnitude: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Minimum magnitude filter"
    )
    max_magnitude: Optional[float] = Field(
        None,
        ge=0.0,
        le=10.0,
        description="Maximum magnitude filter"
    )
    min_depth: Optional[float] = Field(
        None,
        ge=0.0,
        description="Minimum depth filter (km)"
    )
    max_depth: Optional[float] = Field(
        None,
        ge=0.0,
        description="Maximum depth filter (km)"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="Start time filter (UTC)"
    )
    end_time: Optional[datetime] = Field(
        None,
        description="End time filter (UTC)"
    )
    place_contains: Optional[str] = Field(
        None,
        max_length=200,
        description="Filter by place description (case-insensitive)"
    )
    magnitude_type: Optional[str] = Field(
        None,
        max_length=10,
        description="Filter by magnitude type"
    )

    @field_validator('max_magnitude')
    @classmethod
    def validate_magnitude_range(cls, v, info):
        """Ensure max_magnitude is greater than min_magnitude"""
        if v is not None and info.data:
            min_mag = info.data.get('min_magnitude')
            if min_mag is not None and v < min_mag:
                raise ValueError('max_magnitude must be greater than or equal to min_magnitude')
        return v

    @field_validator('max_depth')
    @classmethod
    def validate_depth_range(cls, v, info):
        """Ensure max_depth is greater than min_depth"""
        if v is not None and info.data:
            min_depth = info.data.get('min_depth')
            if min_depth is not None and v < min_depth:
                raise ValueError('max_depth must be greater than or equal to min_depth')
        return v

    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v, info):
        """Ensure end_time is after start_time (naive datetimes)"""
        if v is not None and info.data:
            start_time = info.data.get('start_time')
            if start_time is not None:
                v_naive = v.replace(tzinfo=None) if v.tzinfo else v
                start_naive = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
                if v_naive < start_naive:
                    raise ValueError('end_time must be after start_time')
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class DataRequest(BaseModel):
    """Schema for manual data synchronization requests"""
    

    since_datetime: datetime = Field(
        default_factory=lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1),
        description="Cannot be a future date"
    )

    @field_validator('since_datetime')
    @classmethod
    def validate_not_future(cls, v):
        now = datetime.now(v.tzinfo) if v.tzinfo else datetime.now()
        if v > now:
            raise ValueError('since_datetime cannot be a future date')
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class DataResponse(BaseModel):
    """Schema for data synchronization operation responses"""
    
    success: bool = Field(description="Whether the synchronization was successful")
    message: str = Field(description="Operation status message")
    records_processed: int = Field(description="Number of records fetched from USGS API")
    records_inserted: int = Field(description="Number of new records saved to database")
    start_time: datetime = Field(description="Operation start time")
    end_time: datetime = Field(description="Operation end time")
    duration_seconds: float = Field(description="Operation duration in seconds")

    model_config = ConfigDict()


class ListEarthquakesRequest(BaseModel):
    """Schema for earthquake list request with filters and pagination.
    
    This wrapper schema ensures proper OpenAPI schema generation for TypeScript
    client code generation. By combining filters and pagination into a single
    request body, we maintain a single source of truth while enabling automatic
    interface generation in the frontend.
    """
    
    filters: EarthquakeFilter = Field(
        default_factory=EarthquakeFilter,
        description="Filter criteria for earthquake records"
    )
    pagination: PaginationParams = Field(
        default_factory=PaginationParams,
        description="Pagination parameters for result set"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
