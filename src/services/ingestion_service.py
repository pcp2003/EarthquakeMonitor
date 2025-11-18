from typing import List
import httpx
import sys
import os
import logging
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import USGS_URL

class IngestionServiceError(Exception):
    pass

class IngestionService:

    def __init__(self):
        self.usgs_url = USGS_URL
        if not self.usgs_url:
            raise IngestionServiceError("USGS API URL must be configured")
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Ingestion service initialized with URL: {self.usgs_url}")

    async def fetch_usgs_data(self, since: datetime, limit: int = 1000) -> List[dict]:
        
        if not isinstance(since, datetime):
            raise IngestionServiceError("The 'since' parameter must be of type datetime")
        if since > datetime.utcnow():
            raise IngestionServiceError("The start date cannot be in the future")
        if not isinstance(limit, int) or limit <= 0 or limit > 20000:
            raise IngestionServiceError("The limit must be an integer between 1 and 20000")

        params = {
            "format": "geojson",
            "orderby": "time",
            "starttime": since.strftime("%Y-%m-%dT%H:%M:%S"),
            "limit": limit
        }

        try:

            self.logger.info(f"Fetching earthquake data since {since} with limit of {limit} records")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.usgs_url, params=params)
                response.raise_for_status()
                data = response.json()
            if not isinstance(data, dict) or "features" not in data:
                raise IngestionServiceError("USGS API response in invalid format")
            return await self._format_usgs_records(data)
        except Exception as e:
            self.logger.error(f"Error fetching USGS data: {str(e)}")
            raise IngestionServiceError(f"Error fetching data: {str(e)}") from e
        
        
    async def _format_usgs_records(self, data: dict) -> List[dict]:
        try:
            features = data.get("features", [])
            formatted = []
            errors = 0

            for feature in features:
                try:
                    props = feature["properties"]
                    geom = feature["geometry"]
                    
                    earthquake_time = datetime.utcfromtimestamp(props["time"] / 1000)
                    longitude = float(geom["coordinates"][0])
                    latitude = float(geom["coordinates"][1])
                    depth = float(geom["coordinates"][2]) if geom["coordinates"][2] is not None else 0.0
                    
                    magnitude = props.get("mag")
                    if magnitude is not None:
                        magnitude = float(magnitude)
                    
                    formatted.append({
                        "external_id": str(feature["id"]),
                        "time": earthquake_time,
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth": depth,
                        "magnitude": magnitude,
                        "magnitude_type": props.get("magType"),
                        "place": props.get("place", ""),
                    })
                    
                except Exception:
                    errors += 1
                    continue
                    
            if errors > 0:
                self.logger.warning(f"Skipped {errors} invalid records out of {len(features)} total")
            self.logger.info(f"Formatted {len(formatted)} records successfully")
            return formatted
            
        except Exception as e:
            self.logger.error(f"Error in data formatting: {str(e)}")
            raise IngestionServiceError(f"Error in data formatting: {str(e)}") from e
    
