from pydantic import BaseModel


class LoginResponse(BaseModel):
    ok: bool
    message: str | None = None
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenSession(BaseModel):
    user_id: int
    refresh_token: str
    user_agent: str
    fingerprint: str
    ip: str
    expires_in: int


class TokenData(BaseModel):
    token: str
    exp: int

class TokensPair(BaseModel):
    access: TokenData
    refresh: TokenData

class ContextData(BaseModel):
    user_agent: str
    client_host: str
