from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger
from app.core.config import settings
from app.core.dao.user import UserDAO
from app.core.dependencies.dao import get_session_without_commit
from app.core.models import User
from sqlalchemy.orm import selectinload
from app.core.schemas.user import EmailModel, UserLogin
from app.exceptions import (
    IncorrectEmailOrPasswordException,
    UnauthorizedException,
    InvalidTokenException,
)
from app.utils.auth import validate_password, decode_jwt

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


async def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    """
    Возвращает декодированный payload на основе токена
    :param credentials:
    :return:
    """
    token = credentials.credentials
    from jwt import ExpiredSignatureError

    try:
        payload = decode_jwt(
            token,
            public_key=settings.auth_jwt.public_key.read_text(),
            algorithm=settings.auth_jwt.algorithm,
        )
        return payload
    except ExpiredSignatureError:
        raise UnauthorizedException
    except Exception as e:
        logger.error(e)
        raise UnauthorizedException


async def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Возвращает текущего авторизованного пользователя
    :param payload:payload пользователя
    :param session: асинхронная сессия БД
    :return:
    """
    username = payload.get("sub")

    if not username:
        logger.error('Токен не содержит поля "sub"')
        raise InvalidTokenException

    try:
        user_dao = UserDAO(session)
        user = await user_dao.find_one_or_none(
            filter=EmailModel(email=username), options=[selectinload(User.role)]
        )
    except Exception as e:
        logger.error(e)
        raise UnauthorizedException

    if not user:
        raise UnauthorizedException

    return user
