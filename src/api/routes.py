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

@router.post("/sync", response_model=DataSyncResponse)
async def sync_earthquakes(
    request: DataSyncRequest,
    sync_service: EarthquakeSyncService = Depends(get_sync_service)
):
    """
    Manually trigger earthquake data synchronization.
    """
    return await sync_service.sync_earthquakes(request)

@router.get("/earthquakes", response_model=EarthquakeListResponse)
async def list_earthquakes(
    filters: EarthquakeFilter = Depends(),
    pagination: PaginationParams = Depends(),
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    List earthquakes with filtering and pagination.
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

@router.get("/earthquakes/{earthquake_id}", response_model=EarthquakeResponse)
async def get_earthquake(
    earthquake_id: str,
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    Get details of a specific earthquake by ID.
    """
    earthquake = await repository.get_by_id(earthquake_id)
    if not earthquake:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return earthquake
