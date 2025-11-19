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

@pytest.fixture
def mock_earthquake():
    from models.earthquake import Earthquake
    from datetime import datetime, timezone
    return Earthquake(
        id="test_id",
        time=datetime.now(timezone.utc),
        latitude=0.0,
        longitude=0.0,
        magnitude=5.0,
        place="Test Place",
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def api_mock_repository():
    from unittest.mock import AsyncMock
    from repository.earthquake_repository import EarthquakeRepository
    return AsyncMock(spec=EarthquakeRepository)

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)

@pytest.fixture
def override_dependency(api_mock_repository):
    from main import app
    from api.routes import get_repository
    app.dependency_overrides[get_repository] = lambda: api_mock_repository
    yield
    app.dependency_overrides = {}