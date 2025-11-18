import config  # This will configure logging automatically
from services.ingestion_service import IngestionService
from datetime import datetime, timedelta
import asyncio

async def main():
    
    ingestion_service = IngestionService()
    since = datetime.utcnow() - timedelta(days=1)
    data = await ingestion_service.fetch_usgs_data(since)
    
if __name__ == "__main__":

    asyncio.run(main())
