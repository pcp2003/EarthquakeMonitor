from typing import List
import httpx
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import USGS_URL

class IngestionService:

    def __init__(self):

        self.usgs_url = USGS_URL

    # Fetch earthquake data from USGS API since the given datetime and transform it to correct format
    async def fetch_usgs_data(self, since: datetime) -> List[dict]:

        params = {
            "format": "geojson",
            "orderby": "time",
            "starttime": since.strftime("%Y-%m-%dT%H:%M:%S"),
            "limit": 1000
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            
            response = await client.get(self.usgs_url, params=params)
            response.raise_for_status()
            data = response.json()
            

        return await self._transform_usgs_data(data)
        
    # Transform raw USGS data to internal format
    async def _transform_usgs_data(self, data: List[dict]) -> List[dict]:

        transformed = []

        for feature in data["features"]:
            props = feature["properties"]
            geom = feature["geometry"]

            transformed.append({
                "external_id": feature["id"],
                "time": datetime.utcfromtimestamp(props["time"] / 1000),
                "latitude": geom["coordinates"][1],
                "longitude": geom["coordinates"][0],
                "depth": geom["coordinates"][2],
                "magnitude": props["mag"],
                "magnitude_type": props["magType"],
                "place": props["place"],
            })
        return transformed
    
