from typing import Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    private: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True
