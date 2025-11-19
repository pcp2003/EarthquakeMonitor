from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from repository.earthquake_repository import EarthquakeRepository
from services.ingestion_service import IngestionService
from schemas.earthquake_schemas import DataSyncRequest, DataSyncResponse

logger = logging.getLogger(__name__)

class EarthquakeSyncService:
    """
    Service responsible for synchronizing earthquake data between USGS and the local database.
    Encapsulates the business logic for data ingestion and storage.
    """

    def __init__(self, repository: EarthquakeRepository, ingestion_service: IngestionService):
        self.repository = repository
        self.ingestion_service = ingestion_service

    async def sync_earthquakes(self, request: Optional[DataSyncRequest] = None) -> DataSyncResponse:
        """
        Synchronizes earthquake data.
        
        Strategy:
        1. If request is provided (manual sync), use 'since_hours' from request.
        2. If no request (auto sync), try to get the last event time from DB.
        3. If DB is empty, default to 24 hours ago.
        """
        start_time = datetime.now(timezone.utc)
        
        if request:
            since = start_time - timedelta(hours=request.since_hours)
            limit = request.limit
            logger.info(f"Manual sync requested. Fetching data since {since} (last {request.since_hours} hours)")
        else:
            last_event_time = await self.repository.get_last_event_time()
            if last_event_time:
                since = last_event_time
                logger.info(f"Auto sync: Last event was at {last_event_time}. Fetching new data since then.")
            else:
                since = start_time - timedelta(hours=24)
                logger.info("Auto sync: Database is empty. Fetching data from last 24 hours.")
            
            limit = 20000

        try:
            earthquakes_data = await self.ingestion_service.fetch_usgs_data(since, limit)
            records_processed = len(earthquakes_data)
            
            records_inserted = await self.repository.bulk_insert(earthquakes_data)
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            return DataSyncResponse(
                success=True,
                message="Synchronization completed successfully",
                records_processed=records_processed,
                records_inserted=records_inserted,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Synchronization failed: {str(e)}", exc_info=True)
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            return DataSyncResponse(
                success=False,
                message=f"Synchronization failed: {str(e)}",
                records_processed=0,
                records_inserted=0,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration
            )
