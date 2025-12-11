from __future__ import annotations

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import SYNC_INTERVAL_MINUTES
from database.connection import db_manager
from repository.earthquake_repository import EarthquakeRepository
from services.usgs_data_fetcher import USGSDataFetcher
from services.usgs_data_formatter import USGSDataFormatter
from services.sync_service import EarthquakeSyncService
from datetime import datetime

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Service responsible for managing background tasks.
    Uses APScheduler to run periodic synchronization jobs.
    """

    def __init__(self):

        self.scheduler = AsyncIOScheduler()

    async def _run_sync_job(self):
        """
        Internal job to execute the synchronization logic.
        Manages the database session lifecycle for the background task.
        """
        logger.info("Starting scheduled earthquake synchronization...")
        
        try:
            async for session in db_manager.get_session():
                try:
                    repository = EarthquakeRepository(session)
                    fetcher = USGSDataFetcher()
                    formatter = USGSDataFormatter()
                    sync_service = EarthquakeSyncService(repository, fetcher, formatter)
                    
                    result = await sync_service.sync_earthquakes()
                    
                    if result.success:
                        logger.info(f"Scheduled sync completed: {result.records_inserted} new records.")
                    else:
                        logger.warning(f"Scheduled sync finished with issues: {result.message}")
                        
                except Exception as e:
                    logger.error(f"Error inside sync job execution: {e}", exc_info=True)
                finally:
                    break
                    
        except Exception as e:
            logger.error(f"Failed to acquire database session for scheduler: {e}", exc_info=True)

    def start(self):
        """
        Start the scheduler and add the sync job.
        Executes the sync job immediately on startup, then periodically.
        """
        
        self.scheduler.add_job(
            self._run_sync_job,
            trigger=IntervalTrigger(minutes=SYNC_INTERVAL_MINUTES),
            id="sync_earthquakes",
            name=f"Sync earthquakes every {SYNC_INTERVAL_MINUTES} minute(s)",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            next_run_time=datetime.now()
        )
        self.scheduler.start()
        logger.info(f"Scheduler started with {SYNC_INTERVAL_MINUTES}-minute interval sync job.")

    def shutdown(self):
        """
        Shutdown the scheduler.
        """
        self.scheduler.shutdown()
        logger.info("Scheduler shut down.")
