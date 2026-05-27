"""Глобальные фикстуры для тестов"""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import create_app
from app.api.deps import get_db_session

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tenders_test"

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    return asyncio.new_event_loop()

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=True)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    async with AsyncSession(db_engine) as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app = create_app()
    app.dependency_overrides[get_db_session] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac