from services.ingestion import fetch_earthquakes
from datetime import datetime, timedelta
import asyncio

async def main():
    
    since = datetime.utcnow() - timedelta(days=1)
    data = await fetch_earthquakes(since)
    for feature in data["features"]:

        props = feature["properties"]
        geom = feature["geometry"]

        print(
            feature["id"],
            props["time"],
            geom["coordinates"][1],
            geom["coordinates"][0],
            geom["coordinates"][2],
            props["mag"],
            props["magType"],
            props["place"],
        )

    print("Retrieved Earthquakes:", len(data["features"]), "since", since.isoformat())

if __name__ == "__main__":

    asyncio.run(main())
