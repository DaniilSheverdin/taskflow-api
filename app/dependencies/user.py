from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import InvalidTokenException, UserNotFoundException
from app.dao.user import UserDAO
from app.dependencies.auth import http_bearer
from app.dependencies.dao import get_session_without_commit
from app.models import User
from app.services.crypto import CryptoService


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
    crypto_service = CryptoService(
        public_key=settings.auth_jwt.public_key,
        private_key=settings.auth_jwt.private_key,
        algorithm=settings.auth_jwt.algorithm,
    )
    payload = crypto_service.get_payload(credentials.credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise InvalidTokenException
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise InvalidTokenException
    user_dao = UserDAO(session)
    user = await user_dao.find_one_or_none(
        filter_dict={"id": user_id}, options=[selectinload(User.role)]
    )
    if not user:
        raise UserNotFoundException

    return user
