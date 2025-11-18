from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import config  # This will configure logging and path automatically
from services.ingestion_service import IngestionService
from database.connection import db_manager

logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    
    # Test ingestion service
    ingestion_service = IngestionService()
    since = datetime.utcnow() - timedelta(days=1)
    data = await ingestion_service.fetch_usgs_data(since)
    
    # Test database connection - using the global db_manager instance
    try:
        async for session in db_manager.get_session():
            logger.info("Database connection test successful!")
            break
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    # Properly close the database manager
    await db_manager.close()
    
if __name__ == "__main__":
    asyncio.run(main())
