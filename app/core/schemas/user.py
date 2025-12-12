from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
)


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Эл. почта")
    model_config = ConfigDict(from_attributes=True)


class UserBase(EmailModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)


class UserCreate(UserBase):
    password: bytes


class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=50)


class UserLogin(EmailModel):
    password: str = Field(min_length=8, max_length=50)


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
