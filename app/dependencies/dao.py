from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session_maker


async def get_session_without_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная сессия без авто-коммита
    :return:
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(e)
            raise
        finally:
            await session.close()
