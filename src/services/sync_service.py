from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from repository.earthquake_repository import EarthquakeRepository
from services.usgs_data_fetcher import USGSDataFetcher
from services.usgs_data_formatter import USGSDataFormatter
from schemas.earthquake_schemas import DataRequest, DataResponse

logger = logging.getLogger(__name__)

class EarthquakeSyncService:
    """
    Service responsible for synchronizing earthquake data between USGS and the local database.
    Encapsulates the business logic for data ingestion and storage.
    """

    def __init__(self, repository: EarthquakeRepository, fetcher: USGSDataFetcher, formatter: USGSDataFormatter):
        self.repository = repository
        self.fetcher = fetcher
        self.formatter = formatter

    async def sync_earthquakes(self) -> DataResponse:
        """
        Automatically synchronizes earthquake data from the last recorded event or, if the database is empty, from the last 24 hours.
        """
        start_time = datetime.now(timezone.utc)
        try:
            last_event_time = await self.repository.get_last_event_time()
            if last_event_time:
                since = last_event_time
                logger.info(f"Auto sync: Last event was at {last_event_time}. Fetching new data since then.")
            else:
                since = start_time - timedelta(hours=24)
                logger.info("Auto sync: Database is empty. Fetching data from last 24 hours.")

            request = DataRequest(since_datetime=since)
            raw_earthquakes_data = await self.fetcher.fetch(request)
            formatted_earthquakes_data = await self.formatter.format(raw_earthquakes_data)
            records_processed = len(formatted_earthquakes_data)
            records_inserted = await self.repository.bulk_insert(formatted_earthquakes_data)
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
