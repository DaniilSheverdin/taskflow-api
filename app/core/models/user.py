from sqlalchemy import ForeignKey, text, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.core.models.base import Base, str_uniq
from app.core.models.mixins.created_updated import CreatedUpdated
from app.core.models.mixins.int_id_pk import IntIdPk


class User(IntIdPk, CreatedUpdated, Base):
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str_uniq]
    password: Mapped[bytes]
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), default=2, server_default=text("2")
    )

    role: Mapped["Role"] = relationship(back_populates="members")
    projects: Mapped[list["Project"]] = relationship(
        back_populates="members", secondary="project_members"
    )
    created_projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="creator", foreign_keys="Project.creator_id"
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="assigned_to", secondary="task_responsibles"
    )
