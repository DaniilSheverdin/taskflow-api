from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from app.core.models.base import Base, str_uniq
from app.core.models.users_roles import UsersRoles


class User(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]

    roles: Mapped[list["UsersRoles"]] = relationship(
        back_populates="members", secondary="users_roles"
    )
