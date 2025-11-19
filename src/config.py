import logging
import os
import sys
from dotenv import load_dotenv

# Add src to Python path (centralized setup)
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

# USGS API Configuration
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be configured in .env file")

# Database Pool Configuration (Technical settings - not user configurable)
DB_POOL_SIZE = 5           # Keep N active connections alive
DB_MAX_OVERFLOW = 10       # Extra connections when pool is full
DB_POOL_TIMEOUT = 30       # Seconds to wait for connection
DB_POOL_RECYCLE = 3600     # Recreate connections after 1 hour
DB_ECHO = False            # SQL query logging (change to True for development debugging)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)