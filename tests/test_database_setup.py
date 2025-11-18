import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import patch

from models.earthquake import Earthquake
from models.base import Base
from database.connection import DatabaseManager


class TestDatabase:
    """Test suite for general database functionality"""
    
    def test_earthquake_model_basic_functionality(self):
        """Test Earthquake model creation and basic operations"""
        test_time = datetime.now(timezone.utc)
        
        # Test model instantiation
        earthquake = Earthquake(
            id="test_001",
            time=test_time,
            latitude=37.7749,
            longitude=-122.4194,
            depth=10.5,
            magnitude=4.2,
            magnitude_type="ml",
            place="Test Location"
        )
        
        # Test basic attributes
        assert earthquake.id == "test_001"
        assert earthquake.magnitude == 4.2
        assert earthquake.place == "Test Location"
        
        # Test from_usgs_data method
        usgs_data = {
            "external_id": "test_002",
            "time": test_time,
            "latitude": 34.0522,
            "longitude": -118.2437,
            "depth": 15.0,
            "magnitude": 3.8,
            "magnitude_type": "mw",
            "place": "Los Angeles, CA"
        }
        
        earthquake_from_data = Earthquake.from_usgs_data(usgs_data)
        assert earthquake_from_data.id == "test_002"
        assert earthquake_from_data.magnitude == 3.8
        
        # Test to_dict method
        result_dict = earthquake.to_dict()
        assert result_dict["id"] == "test_001"
        assert result_dict["magnitude"] == 4.2
        
        # Test with null values
        usgs_data_null = {
            "external_id": "test_003",
            "time": test_time,
            "latitude": 45.0,
            "longitude": 90.0,
            "depth": None,
            "magnitude": None,
            "magnitude_type": None,
            "place": None
        }
        
        earthquake_null = Earthquake.from_usgs_data(usgs_data_null)
        assert earthquake_null.depth is None
        assert earthquake_null.magnitude is None
    
    def test_database_manager_setup(self):
        """Test DatabaseManager initialization and basic configuration"""
        # Mock the DATABASE_URL from config
        from unittest.mock import patch
        
        with patch('database.connection.DATABASE_URL', "postgresql+asyncpg://test:test@localhost:5432/test_db"):
            db_manager = DatabaseManager()
            
            assert db_manager.database_url == "postgresql+asyncpg://test:test@localhost:5432/test_db"
            assert db_manager.engine is not None
            assert db_manager.async_session is not None
            
            # Test that table metadata is properly defined
            table = Earthquake.__table__
            assert table.name == "earthquakes"
            
            # Test that primary key exists
            pk_columns = [col.name for col in table.primary_key.columns]
            assert "id" in pk_columns
            
            # Test that required columns are not nullable
            columns = {col.name: col for col in table.columns}
            assert not columns["id"].nullable
            assert not columns["time"].nullable
            assert not columns["latitude"].nullable
            assert not columns["longitude"].nullable
    
    def test_database_manager_missing_url_fails(self):
        """Test DatabaseManager fails gracefully without DATABASE_URL"""
        # Mock the config to return None for DATABASE_URL
        import sys
        from unittest.mock import patch
        
        with patch('database.connection.DATABASE_URL', None):
            with pytest.raises(ValueError, match="DATABASE_URL must be configured in config.py"):
                DatabaseManager()