"""
Schemas module for request/response validation
"""

from .earthquake_schemas import (
    EarthquakeBase,
    EarthquakeResponse,
    EarthquakeListResponse,
    EarthquakeFilter,
    PaginationParams,
    DataRequest,
    DataResponse
)

__all__ = [
    "EarthquakeBase",
    "EarthquakeResponse",
    "EarthquakeListResponse",
    "EarthquakeFilter",
    "PaginationParams",
    "DataRequest",
    "DataResponse"
]