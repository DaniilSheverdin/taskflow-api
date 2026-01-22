from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    task_id: int


class CommentUpdate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    author_id: int
    task_id: int

    class Config:
        from_attributes = True
