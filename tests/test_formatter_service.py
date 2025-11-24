import pytest
from src.services.usgs_data_formatter import USGSDataFormatter

class TestFormatter:
    @pytest.mark.asyncio
    async def test_format_success(self):
        formatter = USGSDataFormatter()
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
        result = await formatter.format(mock_data)
        assert len(result) == 1
        assert result[0]["id"] == "test123"
        assert result[0]["magnitude"] == 4.5
        assert result[0]["place"] == "Test Location"
        assert result[0]["latitude"] == 37.0
        assert result[0]["longitude"] == -122.0

    @pytest.mark.asyncio
    async def test_format_empty_features(self):
        formatter = USGSDataFormatter()
        mock_data = {"features": []}
        result = await formatter.format(mock_data)
        assert result == []

    @pytest.mark.asyncio
    async def test_format_missing_fields(self):
        formatter = USGSDataFormatter()
        mock_data = {
            "features": [
                {
                    "id": "missing_fields",
                    "properties": {},
                    "geometry": {"coordinates": [0, 0, 0]}
                }
            ]
        }
        result = await formatter.format(mock_data)
        assert result == []

    @pytest.mark.asyncio
    async def test_format_invalid_data(self):
        formatter = USGSDataFormatter()
        mock_data = {"invalid": True}
        result = await formatter.format(mock_data)
        assert result == []

