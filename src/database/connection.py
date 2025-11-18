from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE, DB_ECHO

logger = logging.getLogger(__name__)

class DatabaseManager:

    def __init__(self):
        self.database_url = DATABASE_URL
        if not self.database_url:
            raise ValueError("DATABASE_URL must be configured in config.py")
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            self.database_url,
            # Connection pooling settings
            pool_size=DB_POOL_SIZE,         # Keeps N active connections alive
            max_overflow=DB_MAX_OVERFLOW,   # Extra connections when needed
            pool_timeout=DB_POOL_TIMEOUT,   # Timeout to acquire connection
            pool_recycle=DB_POOL_RECYCLE,   # Recreate connections periodically
            pool_pre_ping=True,             # Test connection before using
            echo=DB_ECHO,                   # Log SQL queries (configurable)
            future=True                     # SQLAlchemy 2.0 mode
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(f"Database manager initialized with URL: {self.database_url.split('@')[1] if '@' in self.database_url else 'unknown'}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency to get database session
        """
        async with self.async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self):
        """
        Close the database engine
        """
        await self.engine.dispose()
        logger.info("Database engine closed")

# Global database manager instance
db_manager = DatabaseManager()