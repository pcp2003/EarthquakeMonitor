import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ingestion_service import IngestionService, IngestionServiceError


class TestIngestionService:
    
    def test_init_success(self):
        service = IngestionService()
        assert service.usgs_url is not None
        assert service.logger is not None
    
    @pytest.mark.asyncio
    async def test_fetch_usgs_data_success(self):
        service = IngestionService()
        
        # Test the formatting method directly
        mock_data = {
            "features": [
                {
                    "id": "test123",
                    "properties": {
                        "time": 1700000000000,
                        "mag": 4.5,
                        "place": "Test Location",
                        "magType": "ml"
                    },
                    "geometry": {
                        "coordinates": [-122.0, 37.0, 10.0]
                    }
                }
            ]
        }
        
        result = await service._format_usgs_records(mock_data)
        
        assert len(result) == 1
        assert result[0]["external_id"] == "test123"
        assert result[0]["magnitude"] == 4.5
        assert result[0]["place"] == "Test Location"
        assert result[0]["latitude"] == 37.0
        assert result[0]["longitude"] == -122.0
    
    @pytest.mark.asyncio
    async def test_fetch_usgs_data_invalid_since(self):
        service = IngestionService()
        
        with pytest.raises(IngestionServiceError, match="'since' parameter must be of type datetime"):
            await service.fetch_usgs_data("invalid")
    
    @pytest.mark.asyncio
    async def test_fetch_usgs_data_future_date(self):
        service = IngestionService()
        future_date = datetime.utcnow() + timedelta(days=1)
        
        with pytest.raises(IngestionServiceError, match="start date cannot be in the future"):
            await service.fetch_usgs_data(future_date)