from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column, Mapped


class IntIdPk:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
