from typing import Text, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column

from app.core.models.base import Base, str_uniq
from app.core.models.mixins.created_updated import CreatedUpdated
from app.core.models.mixins.int_id_pk import IntIdPk


class Role(IntIdPk, CreatedUpdated, Base):
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str_uniq]
    description: Mapped[Optional[str]] = mapped_column(String(500))

    members: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
    )
