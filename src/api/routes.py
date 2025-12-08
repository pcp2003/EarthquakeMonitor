from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timezone, datetime, timedelta
import logging

from database.connection import db_manager
from repository.earthquake_repository import EarthquakeRepository
from services.usgs_data_fetcher import USGSDataFetcher
from services.usgs_data_formatter import USGSDataFormatter
from services.sync_service import EarthquakeSyncService
from schemas.earthquake_schemas import (
    EarthquakeResponse, 
    EarthquakeListResponse,
    EarthquakeFilter, 
    PaginationParams,
    DataRequest,
    DataResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_repository(session: AsyncSession = Depends(db_manager.get_session)) -> EarthquakeRepository:
    return EarthquakeRepository(session)

def get_scheduler():
    from main import scheduler
    return scheduler

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
    filters: EarthquakeFilter = EarthquakeFilter(),
    pagination: PaginationParams = PaginationParams(),
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
    
@router.delete("/earthquakes/delete_all", response_model=dict)
async def delete_all_earthquakes(
    repository: EarthquakeRepository = Depends(get_repository)
):
    """
    Delete all earthquake records from the database.
    Useful for resetting the dataset during testing or maintenance.
    """
    await repository.delete_all()
    return {"message": "All earthquake records have been deleted."}

# ==================== SCHEDULER MANAGEMENT ROUTES ====================

@router.post("/scheduler/start")
async def start_scheduler(scheduler_service = Depends(get_scheduler)):
    """
    Start the scheduler to enable automatic earthquake data synchronization.
    """
    if not scheduler_service.scheduler.running:
        scheduler_service.start()
        return {"message": "Scheduler started"}
    return {"message": "Scheduler is already running"}

@router.post("/scheduler/stop")
async def stop_scheduler(scheduler_service = Depends(get_scheduler)):
    """
    Stop the scheduler to disable automatic earthquake data synchronization.
    """
    if scheduler_service.scheduler.running:
        scheduler_service.shutdown()
        return {"message": "Scheduler stopped"}
    return {"message": "Scheduler is already stopped"}

@router.post("/scheduler/sync-now")
async def sync_now(repository: EarthquakeRepository = Depends(get_repository)):
    """
    Force an immediate synchronization of earthquake data from USGS.
    Does not depend on the scheduler status.
    """
    fetcher = USGSDataFetcher()
    formatter = USGSDataFormatter()
    sync_service = EarthquakeSyncService(repository, fetcher, formatter)
    result = await sync_service.sync_earthquakes()
    return result

@router.get("/scheduler/status")
async def scheduler_status(scheduler_service = Depends(get_scheduler)):
    """
    Get the current status of the scheduler and list all scheduled jobs.
    """
    jobs = scheduler_service.scheduler.get_jobs()
    return {
        "running": scheduler_service.scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name, 
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }
