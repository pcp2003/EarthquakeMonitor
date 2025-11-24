import asyncio
from datetime import datetime, timedelta, timezone
import sys
import os

# Garante que o src está no path
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.services.usgs_data_fetcher import USGSDataFetcher
from src.services.usgs_data_formatter import USGSDataFormatter
from src.schemas.earthquake_schemas import DataRequest

async def calculate_frequency():
    fetcher = USGSDataFetcher()
    formatter = USGSDataFormatter()

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=7)

    print(f"Fetching earthquake data from {since} to {now}...")

    try:
        # Cria o DataRequest conforme esperado pelo fetcher
        request = DataRequest(since_datetime=since)
        data = await fetcher.fetch(request)
        records = data.get("features", [])
        count = len(records)

        print(f"Total earthquakes in the last 7 dias: {count}")

        if count == 0:
            print("No records found. Cannot calculate frequency.")
            return

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
