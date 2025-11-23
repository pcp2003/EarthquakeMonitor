import pytest
from datetime import datetime, timezone
from decimal import Decimal

# O import será resolvido através do sys.path configurado no config.py
from schemas.earthquake_schemas import (
    EarthquakeBase,
    EarthquakeResponse,
    EarthquakeFilter,
    PaginationParams,
    DataSyncRequest,
    DataSyncResponse
)


class TestEarthquakeSchemas:
    """Test earthquake schema validation"""

    def test_earthquake_base_valid_data(self):
        """Test EarthquakeBase with valid data"""
        data = {
            "time": datetime.now(timezone.utc),
            "latitude": 37.7749,
            "longitude": -122.4194,
            "depth": 10.5,
            "magnitude": 4.2,
            "magnitude_type": "mw",
            "place": "San Francisco, CA"
        }
        earthquake = EarthquakeBase(**data)
        assert earthquake.latitude == 37.7749
        assert earthquake.longitude == -122.4194
        assert earthquake.magnitude == 4.2

    def test_earthquake_base_invalid_coordinates(self):
        """Test EarthquakeBase with invalid coordinates"""
        with pytest.raises(ValueError):
            EarthquakeBase(
                time=datetime.now(timezone.utc),
                latitude=91.0,  # Invalid latitude
                longitude=0.0,
                depth=10.0,
                magnitude=4.0
            )

        with pytest.raises(ValueError):
            EarthquakeBase(
                time=datetime.now(timezone.utc),
                latitude=0.0,
                longitude=181.0,  # Invalid longitude
                depth=10.0,
                magnitude=4.0
            )

    def test_pagination_params(self):
        """Test pagination parameter validation"""
        # Valid params
        pagination = PaginationParams(page=2, limit=100)
        assert pagination.page == 2
        assert pagination.limit == 100
        assert pagination.offset == 100

        # Default values
        pagination_default = PaginationParams()
        assert pagination_default.page == 1
        assert pagination_default.limit == 50
        assert pagination_default.offset == 0

        # Invalid params
        with pytest.raises(ValueError):
            PaginationParams(page=0)  # Page must be >= 1

        with pytest.raises(ValueError):
            PaginationParams(limit=1001)  # Limit must be <= 1000

    def test_earthquake_filter(self):
        """Test earthquake filter validation"""
        # Valid filter
        filter_data = {
            "min_magnitude": 3.0,
            "max_magnitude": 6.0,
            "start_time": datetime(2023, 1, 1),
            "end_time": datetime(2023, 1, 2),
            "place_contains": "california"
        }
        filter_obj = EarthquakeFilter(**filter_data)
        assert filter_obj.min_magnitude == 3.0
        assert filter_obj.place_contains == "california"

    def test_earthquake_filter_validation_errors(self):
        """Test earthquake filter validation errors"""
        # Test magnitude range validation
        with pytest.raises(ValueError, match="max_magnitude must be greater"):
            EarthquakeFilter(min_magnitude=6.0, max_magnitude=4.0)

        # Test time range validation
        with pytest.raises(ValueError, match="end_time must be after start_time"):
            EarthquakeFilter(
                start_time=datetime(2023, 1, 2),
                end_time=datetime(2023, 1, 1)
            )

    def test_data_sync_request(self):
        """Test data sync request schema"""
        # Valid request
        request = DataSyncRequest(since_hours=48, limit=500)
        assert request.since_hours == 48
        assert request.limit == 500

        # Default values
        request_default = DataSyncRequest()
        assert request_default.since_hours == 24
        assert request_default.limit == 1000

        # Invalid values
        with pytest.raises(ValueError):
            DataSyncRequest(since_hours=200)  # Too many hours

        with pytest.raises(ValueError):
            DataSyncRequest(limit=25000)  # Too high limit

    def test_earthquake_response_from_dict(self):
        """Test EarthquakeResponse can be created from database model"""
        # Simulando dados que viriam do banco
        db_data = {
            "id": "us1000abcd",
            "time": datetime.now(timezone.utc),
            "latitude": 37.7749,
            "longitude": -122.4194,
            "depth": 10.5,
            "magnitude": 4.2,
            "magnitude_type": "mw",
            "place": "San Francisco, CA",
            "created_at": datetime.now(timezone.utc)
        }
        
        # Teste manual de conversão (similar ao from_attributes=True)
        response = EarthquakeResponse(**db_data)
        assert response.id == "us1000abcd"
        assert response.magnitude == 4.2
        assert response.created_at is not None

    def test_data_sync_response(self):
        """Test data sync response schema"""
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        response_data = {
            "success": True,
            "message": "Data synchronization completed successfully",
            "records_processed": 100,
            "records_inserted": 85,
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": 5.2
        }
        
        response = DataSyncResponse(**response_data)
        assert response.success is True
        assert response.records_processed == 100
        assert response.records_inserted == 85

