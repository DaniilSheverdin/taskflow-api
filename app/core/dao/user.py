from loguru import logger
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError

from app.core.dao.base import BaseDAO
from app.core.models.user import User


class UserDAO(BaseDAO):
    model = User

    async def search_by_name_or_email(self, query: str) -> list[User]:
        """
        Ищет пользователей по части имени, фамилии или email (без учета регистра).
        """
        logger.debug(f"Поиск пользователей по запросу: '{query}'")
        try:
            stmt = (
                select(self.model)
                .where(
                    or_(
                        self.model.first_name.ilike(f"%{query}%"),
                        self.model.last_name.ilike(f"%{query}%"),
                        self.model.email.ilike(f"%{query}%"),
                    )
                )
            )
            result = await self._session.execute(stmt)
            records = list(result.scalars().all())
            logger.debug(f"Найдено {len(records)} пользователей")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске пользователей: {e}")
            raise
