import pytest
from unittest.mock import patch

from database.connection import DatabaseManager


class TestDatabase:
    """Test suite for general database functionality"""
    
    def test_database_manager_setup(self):
        """Test DatabaseManager initialization and basic configuration"""

        # Mock the DATABASE_URL from config
        
        with patch('database.connection.DATABASE_URL', "postgresql+asyncpg://test:test@localhost:5432/test_db"):

            db_manager = DatabaseManager()
            
            assert db_manager.database_url == "postgresql+asyncpg://test:test@localhost:5432/test_db"
            assert db_manager.engine is not None
            assert db_manager.async_session is not None
            
    
    def test_database_manager_missing_url_fails(self):
        """Test DatabaseManager fails gracefully without DATABASE_URL"""
        # Mock the config to return None for DATABASE_URL
        
        with patch('database.connection.DATABASE_URL', None):
            with pytest.raises(ValueError, match="DATABASE_URL must be configured in config.py"):
                DatabaseManager()