from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums.task_status import Status


class TaskBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    status: Status = Status.PENDING
    deadline: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: Optional[int] = None


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    creator_id: int
    project_id: Optional[int]

    class Config:
        from_attributes = True
