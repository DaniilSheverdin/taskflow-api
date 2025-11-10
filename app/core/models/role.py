from typing import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from app.core.models.base import Base, str_uniq


class Role(Base):
    name: Mapped[str]
    code: Mapped[str_uniq]
    description: Mapped[Text | None] = None

    members: Mapped[list["User"]] = relationship(
        back_populates="roles",
        secondary="users_roles",
    )
