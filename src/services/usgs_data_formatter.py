from __future__ import annotations
import logging
from datetime import datetime
from typing import List

class USGSDataFormatter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def format(self, data: dict) -> List[dict]:
        try:
            features = data.get("features", [])
            if not isinstance(features, list):
                self.logger.error("O campo 'features' não é uma lista válida.")
                raise ValueError("O campo 'features' deve ser uma lista.")
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
                        "id": str(feature["id"]),
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
                self.logger.warning(f"Ignored {errors} invalid records out of {len(features)} total")
            self.logger.info(f"Successfully formatted {len(formatted)} records")
            return formatted
        except Exception as e:
            self.logger.error(f"Error formatting data: {str(e)}")
            raise ValueError(f"Error formatting data: {str(e)}") from e
