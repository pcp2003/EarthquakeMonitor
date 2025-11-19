import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ingestion_service import IngestionService

async def calculate_frequency():
    service = IngestionService()
    
    # Last 7 days
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=7)
    
    print(f"Fetching earthquake data from {since} to {now}...")
    
    # USGS limit is 20000, which should be enough for a week unless we include micro-quakes
    # The service defaults to 1000, so we must override it.
    try:
        records = await service.fetch_usgs_data(since=since, limit=20000)
        count = len(records)
        
        print(f"Total earthquakes in the last 7 days: {count}")
        
        if count == 0:
            print("No records found. Cannot calculate frequency.")
            return

        # Calculate frequency
        minutes_in_week = 7 * 24 * 60
        avg_per_minute = count / minutes_in_week
        avg_interval_minutes = minutes_in_week / count
        
        print(f"Average earthquakes per minute: {avg_per_minute:.4f}")
        print(f"Average interval between earthquakes: {avg_interval_minutes:.2f} minutes")
        print(f"Average interval between earthquakes: {avg_interval_minutes * 60:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(calculate_frequency())
