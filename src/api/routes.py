from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from database.connection import db_manager
from repository.earthquake_repository import EarthquakeRepository
from services.ingestion_service import IngestionService
from services.sync_service import EarthquakeSyncService
from schemas.earthquake_schemas import (
    EarthquakeResponse, 
    EarthquakeListResponse, 
    EarthquakeFilter, 
    PaginationParams,
    DataSyncRequest,
    DataSyncResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_repository(session: AsyncSession = Depends(db_manager.get_session)) -> EarthquakeRepository:
    return EarthquakeRepository(session)

async def get_ingestion_service() -> IngestionService:
    return IngestionService()

async def get_sync_service(
    repository: EarthquakeRepository = Depends(get_repository),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
) -> EarthquakeSyncService:
    return EarthquakeSyncService(repository, ingestion_service)

@router.post("/earthquakes/pull", response_model=DataSyncResponse)
async def pull_earthquakes(
    request: DataSyncRequest,
    sync_service: EarthquakeSyncService = Depends(get_sync_service)
):
    """
    Manually pull earthquake data from USGS API and store in database.
    """
    return await sync_service.sync_earthquakes(request)

@router.get("/earthquakes/list", response_model=EarthquakeListResponse)
async def list_earthquakes(
    filters: EarthquakeFilter = Depends(),
    pagination: PaginationParams = Depends(),
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    List earthquakes with optional filtering and pagination.
    """
    earthquakes, total = await repository.get_filtered(filters, pagination)
    
    has_next = (pagination.page * pagination.limit) < total
    has_previous = pagination.page > 1
    
    return EarthquakeListResponse(
        earthquakes=earthquakes,
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        has_next=has_next,
        has_previous=has_previous
    )

@router.get("/earthquakes/{earthquake_id}/details", response_model=EarthquakeResponse)
async def get_earthquake_details(
    earthquake_id: str,
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    Get detailed information of a specific earthquake by its ID.
    """
    earthquake = await repository.get_by_id(earthquake_id)
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return earthquake

@router.get("/health")
async def health_check(
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    Health check endpoint that verifies:
    - API is running
    - Database connection is working
    - Last synchronization time
    - Total earthquakes stored
    
    Returns:
        dict: Health status with database info
    """
    try:
        # Test database connection by querying data
        last_sync = await repository.get_last_event_time()
        total_earthquakes = await repository.get_total_count()
        
        return {
            "status": "healthy",
            "database": {
                "status": "connected",
                "total_earthquakes": total_earthquakes,
                "last_event_time": last_sync.isoformat() if last_sync else None
            },
            "message": "Earthquake Monitor API is running normally"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": {"status": "disconnected"},
                "error": "Database connection failed",
                "message": str(e)
            }
        )
