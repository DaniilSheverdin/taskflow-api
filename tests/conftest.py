import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.dependencies.dao import get_session_without_commit
from app.main import app
from app.models.base import Base


engine_test = create_async_engine("sqlite+aiosqlite:///:memory:")
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Создает все таблицы перед началом тестов и удаляет их после.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура, которая создает новую тестовую сессию для каждого теста
    и откатывает все изменения после его завершения.
    """
    connection = await engine_test.connect()
    trans = await connection.begin()

    async with async_session_maker(bind=connection, expire_on_commit=False) as session:
        yield session
        await trans.rollback()
        await connection.close()


@pytest.fixture(scope="function")
async def client(
    override_get_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Создает AsyncClient с переопределенной зависимостью для сессии БД.
    """
    app.dependency_overrides[get_session_without_commit] = lambda: override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url=f"http://{settings.DOMAIN}"
    ) as ac:
        yield ac

    del app.dependency_overrides[get_session_without_commit]


# Это необходимо для pytest-asyncio, чтобы он правильно работал с `scope="session"`
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
