from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from app.core.models.base import Base
from app.core.models.mixins.created_updated import CreatedUpdated
from app.core.models.mixins.int_id_pk import IntIdPk


class Comment(IntIdPk, CreatedUpdated, Base):
    content: Mapped[str] = mapped_column(String(250))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))

    task: Mapped[int] = relationship(
        "Task",
        back_populates="comments",
    )
