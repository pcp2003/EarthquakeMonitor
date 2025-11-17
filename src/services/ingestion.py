import httpx
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import USGS_URL

# Fetch earthquake data from USGS API since the given datetime
async def fetch_earthquakes(since: datetime):

    params = {
        "format": "geojson",
        "orderby": "time",
        "starttime": since.strftime("%Y-%m-%dT%H:%M:%S"),
        "limit": 1000
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        
        response = await client.get(USGS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    