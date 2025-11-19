from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

import config
from api.routes import router as api_router
from database.connection import db_manager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    logger.info("Starting Earthquake Monitor API...")
    yield
    logger.info("Shutting down Earthquake Monitor API...")
    await db_manager.close()

app = FastAPI(
    title="Earthquake Monitor API",
    description="API for monitoring earthquake data from USGS",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1", tags=["earthquakes"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
