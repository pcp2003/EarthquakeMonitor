import pytest
import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(autouse=True)
def setup_logging():
    """Disable logging during tests to keep output clean"""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)

@pytest.fixture
def mock_session():
    from unittest.mock import AsyncMock
    from sqlalchemy.ext.asyncio import AsyncSession
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def repository(mock_session):
    from repository.earthquake_repository import EarthquakeRepository
    return EarthquakeRepository(mock_session)