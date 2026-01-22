from loguru import logger
from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base import BaseDAO
from app.models.user import User
from app.schemas.user import EmailModel, UserLogin, UserCreate
from app.core.exceptions import IncorrectEmailOrPasswordException
from app.services.crypto import CryptoService


class UserDAO(BaseDAO):
    model = User

    async def create(self, data: UserCreate):
        await super().create(data=data)
        await self._session.commit()

    async def get_user_by_credentials(self, email: EmailStr, password: str) -> User:
        """
        Осуществляет поиск пользователя по email и паролю
        :param password:
        :param email:
        :return:
        """
        user = await self.find_one_or_none(filter=EmailModel(email=email))
        if not (
            user
            and CryptoService.validate_hashed(
                compared_str=password, hashed_str=user.password
            )
        ):
            raise IncorrectEmailOrPasswordException
        return user

    async def search_by_name_or_email(self, query: str) -> list[User]:
        """
        Ищет пользователей по части имени, фамилии или email (без учета регистра).
        """
        logger.debug(f"Поиск пользователей по запросу: '{query}'")
        try:
            stmt = select(self.model).where(
                or_(
                    self.model.first_name.ilike(f"%{query}%"),
                    self.model.last_name.ilike(f"%{query}%"),
                    self.model.email.ilike(f"%{query}%"),
                )
            )
            result = await self._session.execute(stmt)
            records = list(result.scalars().all())
            logger.debug(f"Найдено {len(records)} пользователей")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске пользователей: {e}")
            raise
