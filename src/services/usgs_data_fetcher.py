from __future__ import annotations
import httpx
import logging
from datetime import datetime, timezone
from config import USGS_URL, USGS_TIMEOUT
from schemas.earthquake_schemas import DataRequest

class USGSDataFetcher:
    def __init__(self, usgs_url: str = USGS_URL):
        if not usgs_url:
            raise ValueError("USGS API URL must be configured")
        self.usgs_url = usgs_url
        self.logger = logging.getLogger(__name__)

    async def fetch(self, request: DataRequest) -> dict:
        since = request.since_datetime
        params = {
            "format": "geojson",
            "orderby": "time",
            "starttime": since.strftime("%Y-%m-%dT%H:%M:%S")
        }
        try:
            self.logger.info(f"Fetching earthquake data since {since}")
            async with httpx.AsyncClient(timeout=USGS_TIMEOUT) as client:
                response = await client.get(self.usgs_url, params=params)
                response.raise_for_status()
                data = response.json()
            if not isinstance(data, dict) or "features" not in data:
                raise ValueError("USGS API response in invalid format")
            return data
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Error fetching data from USGS: {str(e)}")
            raise RuntimeError(f"Error fetching data: {str(e)}") from e
