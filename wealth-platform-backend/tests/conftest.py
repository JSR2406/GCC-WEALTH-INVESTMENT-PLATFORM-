"""
Pytest Configuration
"""

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.base import Base


# Test database URL
TEST_DATABASE_URL = settings.database_url.replace(
    settings.postgres_db, f"{settings.postgres_db}_test"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database):
    """Get test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Get test client with overridden dependencies."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_bank_data():
    """Sample bank registration data."""
    return {
        "name": "Test Bank",
        "slug": "test-bank",
        "country": "AE",
        "revenue_model": "hybrid",
        "base_fee_usd": 25.00,
        "aum_share_percentage": 20.00
    }


@pytest.fixture
def sample_admin_data():
    """Sample bank admin data."""
    return {
        "email": "admin@testbank.com",
        "full_name": "Test Admin",
        "phone": "+971501234567",
        "password": "SecurePass123!"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data."""
    return {
        "email": "user@example.com",
        "phone": "+971509876543",
        "full_name": "Test User",
        "nationality": "AE",
        "residency_country": "AE"
    }
