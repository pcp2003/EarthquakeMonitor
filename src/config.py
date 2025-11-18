import logging

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)