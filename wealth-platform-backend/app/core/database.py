"""
Database Configuration
======================

SQLAlchemy async engine and session management for PostgreSQL.
Provides:
- Async engine setup with connection pooling
- Session factory with scoped sessions
- Database dependency for FastAPI
- Transaction management helpers
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# SQLAlchemy Base
# =============================================================================

Base = declarative_base()

# =============================================================================
# Async Engine
# =============================================================================

_engine: Optional[AsyncEngine] = None


def get_engine() -> AsyncEngine:
    """
    Get or create the async SQLAlchemy engine.
    
    Uses connection pooling with the following settings:
    - pool_size: Number of connections to keep open
    - max_overflow: Max connections above pool_size
    - pool_pre_ping: Verify connections before use
    - pool_recycle: Recycle connections after 1 hour
    
    Returns:
        AsyncEngine instance
    """
    global _engine
    
    if _engine is None:
        logger.info(f"Creating database engine for: {settings.DATABASE_URL[:50]}...")
        
        _engine = create_async_engine(
            settings.DATABASE_URL,
            **settings.database_settings,
            future=True,
        )
        
        # Log connection events in debug mode
        if settings.DEBUG:
            @event.listens_for(_engine.sync_engine, "connect")
            def on_connect(dbapi_connection, connection_record):
                logger.debug("Database connection established")
            
            @event.listens_for(_engine.sync_engine, "checkout")
            def on_checkout(dbapi_connection, connection_record, connection_proxy):
                logger.debug("Database connection checked out from pool")
    
    return _engine


# =============================================================================
# Session Factory
# =============================================================================

def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get the async session maker.
    
    Returns:
        async_sessionmaker configured for the engine
    """
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# =============================================================================
# FastAPI Dependency
# =============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession instance
    """
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# =============================================================================
# Transaction Context Manager
# =============================================================================

@asynccontextmanager
async def transaction(session: AsyncSession):
    """
    Context manager for database transactions.
    
    Automatically commits on success, rolls back on error.
    
    Usage:
        async with transaction(db) as session:
            session.add(item)
            # Commits automatically if no exception
    
    Args:
        session: AsyncSession instance
        
    Yields:
        The same session within a transaction
    """
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Transaction rollback due to: {e}")
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Transaction rollback due to unexpected error: {e}")
        raise


# =============================================================================
# Health Check
# =============================================================================

async def check_database_connection() -> bool:
    """
    Verify database connectivity.
    
    Returns:
        True if database is accessible, False otherwise
    """
    try:
        async with get_async_session_maker()() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# =============================================================================
# Lifecycle Events
# =============================================================================

async def init_db() -> None:
    """
    Initialize database connection pool.
    
    Called on application startup.
    """
    logger.info("Initializing database connection pool...")
    engine = get_engine()
    
    # Verify connection
    if await check_database_connection():
        logger.info("Database connection verified successfully")
    else:
        logger.error("Failed to connect to database!")
        raise RuntimeError("Database connection failed")


async def close_db() -> None:
    """
    Close database connection pool.
    
    Called on application shutdown.
    """
    global _engine
    
    if _engine is not None:
        logger.info("Closing database connection pool...")
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")


# =============================================================================
# Query Helpers
# =============================================================================

async def get_or_none(
    session: AsyncSession,
    model,
    **filters
):
    """
    Get a single record or return None.
    
    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filter conditions (column=value)
        
    Returns:
        Model instance or None
    """
    from sqlalchemy import select
    
    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_or_404(
    session: AsyncSession,
    model,
    error_class,
    **filters
):
    """
    Get a single record or raise an exception.
    
    Args:
        session: Database session
        model: SQLAlchemy model class
        error_class: Exception class to raise if not found
        **filters: Filter conditions
        
    Returns:
        Model instance
        
    Raises:
        error_class: If record not found
    """
    result = await get_or_none(session, model, **filters)
    if result is None:
        raise error_class(**filters)
    return result


async def exists(
    session: AsyncSession,
    model,
    **filters
) -> bool:
    """
    Check if a record exists.
    
    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filter conditions
        
    Returns:
        True if record exists, False otherwise
    """
    from sqlalchemy import select, func
    
    stmt = select(func.count()).select_from(model).filter_by(**filters)
    result = await session.execute(stmt)
    return result.scalar() > 0


async def paginate(
    session: AsyncSession,
    stmt,
    page: int = 1,
    page_size: int = 20
):
    """
    Paginate a query.
    
    Args:
        session: Database session
        stmt: SQLAlchemy select statement
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Tuple of (items, total_count, total_pages)
    """
    from sqlalchemy import func, select
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await session.execute(count_stmt)).scalar()
    
    # Calculate pagination
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get items
    paginated_stmt = stmt.offset(offset).limit(page_size)
    result = await session.execute(paginated_stmt)
    items = result.scalars().all()
    
    return items, total_count, total_pages
