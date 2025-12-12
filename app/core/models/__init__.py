"""Import all models here for Alembic and SQLAlchemy to discover."""

from app.core.models.base import Base
from app.core.models.comment import Comment
from app.core.models.project import Project
from app.core.models.project_members import ProjectMembers
from app.core.models.role import Role
from app.core.models.task import Task
from app.core.models.task_responsibles import TaskResponsibles
from app.core.models.user import User

__all__ = (
    "Base",
    "User",
    "Role",
    "Project",
    "ProjectMembers",
    "Task",
    "TaskResponsibles",
    "Comment",
)
