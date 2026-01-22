from typing import TypeVar, Generic, Type, Any, Optional, List

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select, update, func, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """
    Базовый класс для Data Access Objects (DAO).
    Предоставляет CRUD операции для моделей SQLAlchemy.
    """

    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Необходимо определить атрибут 'model'")

    async def create(self, data: BaseModel) -> T:
        """
        Создает новую запись
        """
        values_dict = data.model_dump(exclude_unset=True)
        logger.debug(
            f"Добавление записи {self.model.__name__} с данными: {values_dict}"
        )
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            logger.debug(f"Запись {self.model.__name__} успешно добавлена")
            await self._session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка создания {self.model.__name__}: {e}")
            raise

    async def create_batch(self, batch: List[BaseModel]) -> list[T]:
        """
        Добавляет несколько записей
        :param batch:
        :return:
        """
        data_list = [_.model_dump(exclude_unset=True) for _ in batch]
        logger.debug(
            f"Добавление списка записей {self.model.__name__}: [{len(data_list)}]"
        )
        try:
            new_instances = [self.model(**_) for _ in data_list]
            self._session.add_all(new_instances)
            logger.debug(f"добавлено {len(new_instances)} записей")
            await self._session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка добавления списка записей {self.model.__name__}: {e}")
            raise

    async def find_by_id(self, pk: Any) -> T | None:
        """
        Получает запись по PK
        """
        try:
            result = await self._session.get(self.model, pk)
            message = f"Запись {'найдена' if result else 'не найдена'}"
            logger.debug(message)
            return result
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения {self.model.__name__} по ID={pk}: {e}")
            raise

    async def find_one_or_none(
        self,
        filter: Optional[BaseModel] = None,
        options: List[Any] = None,
        filter_dict: Optional[dict] = None,
        order_by_field: str = None,
        order_desc: bool = False,
    ) -> T | None:
        """
        Ищет одну запись по фильтру
        :param order_by_field:
        :param order_desc:
        :param options:
        :param filter_dict:
        :param filter:
        :return:
        """
        if filter is None and filter_dict is None:
            raise ValueError("Задайте значение для filter или filter_dict")
        if filter_dict is None and filter is not None:
            filter_dict = filter.model_dump(exclude_unset=True)
        logger.debug(
            f"Поиск (одной) записи {self.model.__name__} по фильтру: {filter_dict}"
        )
        try:
            stmt = select(self.model).filter_by(**filter_dict)
            if order_by_field:
                field = getattr(self.model, order_by_field, None)
                if field:
                    if order_desc:
                        stmt = stmt.order_by(desc(field))
                    else:
                        stmt = stmt.order_by(asc(field))

            if options:
                stmt = stmt.options(*options)
            result = await self._session.execute(stmt)
            record = result.scalar_one_or_none()
            message = f"Запись {'найдена' if record else 'не найдена'} по фильтру: {filter_dict}"
            logger.debug(message)
            return record
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка поиска {self.model.__name__} по фильтру: {filter_dict}: {e}"
            )
            raise

    async def find(
        self,
        offset: int = 0,
        limit: int = 100,
        filter: Optional[BaseModel] = None,
        filter_dict: Optional[dict] = None,
        options: List[Any] = None,
    ) -> list[T]:
        """
        Получает список объектов по фильтру и пагинации
        """

        if filter_dict is None:
            filter_dict = filter.model_dump(exclude_unset=True) if filter else {}
        logger.debug(
            f"Поиск всех записей {self.model.__name__} по фильтру: {filter_dict}; offset: {offset}, limit: {limit}"
        )
        try:
            stmt = (
                select(self.model).filter_by(**filter_dict).offset(offset).limit(limit)
            )
            if options:
                stmt = stmt.options(*options)
            result = await self._session.execute(stmt)
            records = list(result.scalars().all())
            logger.debug(f"Найдено {len(records)} записей")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения списка {self.model.__name__}: {e}")
            raise

    async def update(self, filters: BaseModel, data: BaseModel) -> list[T]:
        """
        Обновляет записи по фильтру
        """
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = data.model_dump(exclude_unset=True)
        logger.debug(
            f"Обновление {self.model.__name__} по фильтру {filter_dict} с данными {values_dict}"
        )

        try:
            conditions = [
                getattr(self.model, field) == value
                for field, value in filter_dict.items()
            ]

            stmt = (
                update(self.model)
                .where(*conditions)
                .values(**values_dict)
                .returning(self.model)
            )
            result = await self._session.execute(stmt)
            updated_records = list(result.scalars().all())
            logger.debug(f"Обновлено {len(updated_records)} записей")
            await self._session.flush()
            return updated_records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка обновления {self.model.__name__}: {e}")
            raise

    async def count(
        self, filters: Optional[BaseModel] = None, filter_dict: Optional[dict] = None
    ) -> int:
        if filters is None and filter_dict is None:
            raise ValueError("Задайте значение для filter или filter_dict")
        if filter_dict is None and filters is not None:
            filter_dict = filters.model_dump(exclude_unset=True)

        try:
            stmt = select(func.count()).select_from(self.model).filter_by(**filter_dict)
            result = await self._session.execute(stmt)
            count_value = result.scalar_one()
            return count_value
        except SQLAlchemyError as e:
            logger.error(f"Ошибка подсчёта {self.model.__name__}: {e}")
            raise
