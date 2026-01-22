from typing import Optional

from sqlalchemy import ForeignKey, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.comment import Comment
from app.models.enums.task_status import Status
from app.models.mixins.created_updated import CreatedUpdated
from app.models.mixins.int_id_pk import IntIdPk
from app.models.project import Project
from app.models.user import User


class Task(IntIdPk, CreatedUpdated, Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    deadline: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[Status] = mapped_column(
        default=Status.PENDING,
        server_default=text(f"'{Status.PENDING.name}'"),
        nullable=False,
    )

    assigned_to: Mapped[list["User"]] = relationship(
        back_populates="assigned_tasks",
        secondary="task_responsibles",
    )
    creator: Mapped["User"] = relationship("User", back_populates="created_tasks")
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )
