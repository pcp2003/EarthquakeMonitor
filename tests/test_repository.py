import pytest
from unittest.mock import AsyncMock, MagicMock, ANY
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from repository.earthquake_repository import EarthquakeRepository
from schemas.earthquake_schemas import EarthquakeFilter, PaginationParams
from models.earthquake import Earthquake

class TestEarthquakeRepository:
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, repository, mock_session):
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Earthquake(id="test_id")
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await repository.get_by_id("test_id")
        
        # Verify
        assert result is not None
        assert result.id == "test_id"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_filtered_basic(self, repository, mock_session):
        # Setup
        mock_result_count = MagicMock()
        mock_result_count.scalar_one.return_value = 10
        
        mock_result_items = MagicMock()
        mock_result_items.scalars.return_value.all.return_value = [Earthquake(id="1"), Earthquake(id="2")]
        
        # Configure execute to return count first, then items
        mock_session.execute.side_effect = [mock_result_count, mock_result_items]
        
        filters = EarthquakeFilter()
        pagination = PaginationParams(page=1, limit=10)
        
        # Execute
        items, total = await repository.get_filtered(filters, pagination)
        
        # Verify
        assert len(items) == 2
        assert total == 10
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_filtered_with_criteria(self, repository, mock_session):
        # Setup
        mock_session.execute.side_effect = [MagicMock(), MagicMock()]
        
        filters = EarthquakeFilter(
            min_magnitude=5.0,
            place_contains="Japan"
        )
        pagination = PaginationParams()
        
        # Execute
        await repository.get_filtered(filters, pagination)
        
        assert mock_session.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_insert_empty(self, repository, mock_session):
        result = await repository.bulk_insert([])
        assert result == 0
        mock_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_insert_success(self, repository, mock_session):
        # Setup
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result
        
        data = [{"id": "1", "magnitude": 5.0}, {"id": "2", "magnitude": 6.0}]
        
        # Execute
        count = await repository.bulk_insert(data)
        
        # Verify
        assert count == 5
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_last_event_time(self, repository, mock_session):
        # Setup
        expected_time = datetime.now(timezone.utc)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_time
        mock_session.execute.return_value = mock_result
        
        # Execute
        result = await repository.get_last_event_time()
        
        # Verify
        assert result == expected_time
        mock_session.execute.assert_called_once()
