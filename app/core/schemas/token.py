from pydantic import BaseModel


class Token(BaseModel):
    ok: bool
    message: str | None = None
    access_token: str
    token_type: str = "bearer"
