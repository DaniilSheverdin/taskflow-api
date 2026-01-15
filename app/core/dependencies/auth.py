from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dao.user import UserDAO
from app.core.dependencies.dao import get_session_without_commit
from app.core.models import User
from app.core.schemas.user import EmailModel, UserLogin
from app.exceptions import (
    IncorrectEmailOrPasswordException,
    UnauthorizedException,
    InvalidTokenException,
    RefreshTokenNotFoundException,
)
from app.utils.auth import validate_password, get_payload_for_credentials

http_bearer = HTTPBearer()


async def authenticate_user(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_session_without_commit),
) -> User:
    """
    Аутентифицирует пользователя по email и паролю. Возвращает пользователя
    """
    user_dao = UserDAO(session)
    user = await user_dao.find_one_or_none(filter=EmailModel(email=user_data.email))
    if not (
        user
        and validate_password(
            password=user_data.password, hashed_password=user.password
        )
    ):
        raise IncorrectEmailOrPasswordException
    return user


async def get_current_user_by_payload(payload, session: AsyncSession):
    user_id = payload.get("sub")

    if not user_id:
        logger.error('Токен не содержит поля "sub"')
        raise InvalidTokenException

    try:
        user_id = int(user_id)
        user_dao = UserDAO(session)
        user = await user_dao.find_one_or_none(
            filter_dict={"id": user_id}, options=[selectinload(User.role)]
        )
    except Exception as e:
        logger.error(e)
        raise UnauthorizedException

    if not user:
        raise UnauthorizedException

    return user


def get_refresh_token(request: Request) -> str:
    """Извлекаем refresh_token из кук."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise RefreshTokenNotFoundException
    return token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Возвращает текущего авторизованного пользователя
    :param session:
    :param credentials:
    :return:
    """
    payload = get_payload_for_credentials(credentials.credentials)
    return await get_current_user_by_payload(payload, session)


async def check_refresh_token(
    token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit),
):
    payload = get_payload_for_credentials(token)
    return await get_current_user_by_payload(payload, session)
