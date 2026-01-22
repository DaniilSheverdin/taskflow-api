from pydantic import BaseModel, Field, ConfigDict


class Role(BaseModel):
    id: int = Field(description="Идентификатор роли")
    name: str = Field(description="Название роли")
    description: str | None = Field(description="Описание роли")
    code: str = Field(description="Код")
    model_config = ConfigDict(from_attributes=True)
