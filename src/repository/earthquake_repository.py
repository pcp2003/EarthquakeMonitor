from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, func, desc
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.earthquake import Earthquake
from schemas.earthquake_schemas import EarthquakeFilter, PaginationParams


class EarthquakeRepository:
    """
    Repository for handling Earthquake database operations.
    Implements efficient bulk insertion and filtered retrieval.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, earthquake_id: str) -> Optional[Earthquake]:
        """
        Retrieve a single earthquake by its USGS ID.
        """
        query = select(Earthquake).where(Earthquake.id == earthquake_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_filtered(
        self, 
        filters: EarthquakeFilter, 
        pagination: PaginationParams
    ) -> Tuple[List[Earthquake], int]:
        """
        Retrieve earthquakes applying filters and pagination.
        Returns a tuple with (list of earthquakes, total count).
        """
        query = select(Earthquake)
        
        if filters.min_magnitude is not None:
            query = query.where(Earthquake.magnitude >= filters.min_magnitude)
        
        if filters.max_magnitude is not None:
            query = query.where(Earthquake.magnitude <= filters.max_magnitude)
            
        if filters.min_depth is not None:
            query = query.where(Earthquake.depth >= filters.min_depth)
            
        if filters.max_depth is not None:
            query = query.where(Earthquake.depth <= filters.max_depth)
            
        if filters.start_time is not None:
            query = query.where(Earthquake.time >= filters.start_time)
            
        if filters.end_time is not None:
            query = query.where(Earthquake.time <= filters.end_time)
            
        if filters.magnitude_type is not None:
            query = query.where(Earthquake.magnitude_type == filters.magnitude_type)
            
        if filters.place_contains is not None:
            query = query.where(Earthquake.place.ilike(f"%{filters.place_contains}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(desc(Earthquake.time))
        query = query.limit(pagination.limit).offset(pagination.offset)

        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def bulk_insert(self, earthquakes_data: List[dict]) -> int:
        """
        Insert multiple earthquakes efficiently ignoring duplicates.
        Uses PostgreSQL ON CONFLICT DO NOTHING.
        
        Returns:
            int: Number of newly inserted rows
        """
        if not earthquakes_data:
            return 0

        stmt = insert(Earthquake).values(earthquakes_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        inserted_count = result.rowcount
        if inserted_count > 0:
            self.logger.info(f"Successfully inserted {inserted_count} new earthquakes")
        
        return inserted_count

    async def get_last_event_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the most recent earthquake in the database.
        Used to optimize ingestion by fetching only newer events.
        """
        query = select(func.max(Earthquake.time))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
