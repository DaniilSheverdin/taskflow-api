from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, DeclarativeBase, declared_attr

from app.utils.case_converter import camel_case_to_snake_case

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей таблиц
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Определяет правило образования названия таблиц из названия моделей: например, User -> users
        :return:
        """
        return camel_case_to_snake_case(cls.__name__) + "s"

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}>"
