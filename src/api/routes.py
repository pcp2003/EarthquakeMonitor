from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone

from database.connection import db_manager
from repository.earthquake_repository import EarthquakeRepository
from services.usgs_data_fetcher import USGSDataFetcher
from services.usgs_data_formatter import USGSDataFormatter
from schemas.earthquake_schemas import (
    EarthquakeResponse, 
    EarthquakeListResponse, 
    EarthquakeFilter, 
    PaginationParams,
    DataRequest,
    DataResponse
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_repository(session: AsyncSession = Depends(db_manager.get_session)) -> EarthquakeRepository:
    return EarthquakeRepository(session)

async def get_usgs_services():
    fetcher = USGSDataFetcher()
    formatter = USGSDataFormatter()
    return fetcher, formatter

@router.post("/earthquakes/ManualSync", response_model=DataResponse)
async def pull_earthquakes(
    request: DataRequest,
    repository: EarthquakeRepository = Depends(get_repository),
    fetcher_formatter = Depends(get_usgs_services)
):
    """
    Manually pull earthquake data from USGS API and store in database.
    """
    fetcher, formatter = fetcher_formatter
    start_time = datetime.now(timezone.utc)
    try:
        raw_earthquakes_data = await fetcher.fetch(request)
        formatted_earthquakes_data = await formatter.format(raw_earthquakes_data)
        records_processed = len(formatted_earthquakes_data)
        records_inserted = await repository.bulk_insert(formatted_earthquakes_data)
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        return DataResponse(
            success=True,
            message="Synchronization completed successfully",
            records_processed=records_processed,
            records_inserted=records_inserted,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )
    except Exception as e:
        import sqlalchemy.exc
        if (
            isinstance(e, sqlalchemy.exc.InterfaceError)
            or (hasattr(e, '__class__') and 'InterfaceError' in e.__class__.__name__)
            and 'number of query arguments cannot exceed' in str(e)
        ):
            user_message = (
                "Too many records to insert at once. "
                "Please try synchronizing a smaller amount of data. "
                "(PostgreSQL allows a maximum of 32767 query arguments per request.)"
            )
        else:
            user_message = f"Synchronization failed: {str(e)}"
        logger.error(f"Synchronization failed: {str(e)}", exc_info=True)
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        return DataResponse(
            success=False,
            message=user_message,
            records_processed=0,
            records_inserted=0,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )

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
