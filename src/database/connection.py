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
        
        self.engine = create_async_engine(
            self.database_url,
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_timeout=DB_POOL_TIMEOUT,
            pool_recycle=DB_POOL_RECYCLE,
            pool_pre_ping=True,
            echo=DB_ECHO,
            future=True
        )
        
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

db_manager = DatabaseManager()