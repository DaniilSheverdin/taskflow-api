from typing import Optional

from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.core.models.base import Base
from app.core.models.mixins.created_updated import CreatedUpdated
from app.core.models.mixins.int_id_pk import IntIdPk
from app.core.models.project import Project
from app.core.models.user import User


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

    assigned_to: Mapped[list["User"]] = relationship(
        back_populates="assigned_tasks",
        secondary="task_responsibles",
    )
    creator: Mapped["User"] = relationship("User", back_populates="created_tasks")
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
