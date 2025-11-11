from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

engine = create_async_engine(
    url=settings.DATABASE_URL,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.POOL_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
