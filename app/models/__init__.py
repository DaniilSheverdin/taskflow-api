"""Import all models here for Alembic and SQLAlchemy to discover."""

from app.models.base import Base
from app.models.comment import Comment
from app.models.project import Project
from app.models.project_members import ProjectMembers
from app.models.role import Role
from app.models.task import Task
from app.models.task_responsibles import TaskResponsibles
from app.models.user import User

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
