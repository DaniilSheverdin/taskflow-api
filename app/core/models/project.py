from typing import Optional

from sqlalchemy import ForeignKey, Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.core.models.base import Base


class Project(Base):
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    private: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["User"] = relationship(back_populates="created_projects")
    members: Mapped[list["User"]] = relationship(
        back_populates="projects",
        secondary="project_members",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
    )
