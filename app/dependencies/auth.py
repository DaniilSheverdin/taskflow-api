from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from app.core.exceptions import (
    RefreshTokenNotFoundException,
    EmptyUserAgentException,
)
from app.schemas.token import ContextData

http_bearer = HTTPBearer()


def get_user_agent(request: Request) -> str:
    ua = request.headers.get("User-Agent", "")
    if ua:
        return ua
    raise EmptyUserAgentException()


def get_client_host(request: Request) -> str:
    return request.client.host


def get_auth_context(
    user_agent: str = Depends(get_user_agent),
    client_host: str = Depends(get_client_host),
) -> ContextData:
    return ContextData(user_agent=user_agent, client_host=client_host)


def get_refresh_token(request: Request) -> str:
    """Извлекает refresh token из кук."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise RefreshTokenNotFoundException
    return token
