from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    UserAlreadyExistsException,
    RefreshSessionNotFoundException,
    InvalidFingerprintException,
)
from app.dao.refresh_session import RefreshSessionDAO
from app.dao.user import UserDAO
from app.models.refresh_session import RefreshSession
from app.schemas.token import TokensPair, TokenSession
from app.schemas.user import (
    UserRegister,
    EmailModel,
    UserCreate,
    UserLogin,
)
from app.services.crypto import CryptoService

crypto_service = CryptoService(
    settings.auth_jwt.public_key,
    settings.auth_jwt.private_key,
    settings.auth_jwt.algorithm,
)


async def register_new_user(user_data: UserRegister, session: AsyncSession):
    """
    Регистрация нового пользователя
    :param session:
    :param user_data:
    :return:
    """
    dao = UserDAO(session)
    probably_existing_user = await dao.find_one_or_none(
        filter=EmailModel(email=user_data.email)
    )
    if probably_existing_user:
        raise UserAlreadyExistsException

    user_data_dict = user_data.model_dump()
    user_data_dict["password"] = CryptoService.hash_password(user_data_dict["password"])

    await dao.create(data=UserCreate(**user_data_dict))


async def get_auth_user(login_data: UserLogin, session: AsyncSession):
    """
    Возвращает пользователя по логину и паролю
    :param login_data:
    :param session:
    :return:
    """
    user_dao = UserDAO(session)
    return await user_dao.get_user_by_credentials(
        email=login_data.email, password=login_data.password
    )


async def update_tokens(
    user_agent: str,
    fingerprint: str,
    user_id: int,
    client_host: str,
    session: AsyncSession,
) -> TokensPair:
    """
    Общая функция для обновления токенов refresh и auth. Добавляет refresh сессию в БД.
    :return:
    """
    tokens_pair = crypto_service.create_tokens_pair(
        str(user_id),
        settings.auth_jwt.refresh_token_expire_minutes,
        settings.auth_jwt.access_token_expire_minutes,
    )
    refresh = tokens_pair.refresh

    session_dao = RefreshSessionDAO(session)
    await session_dao.create_session(
        TokenSession(
            user_id=user_id,
            refresh_token=refresh.token,
            user_agent=user_agent,
            fingerprint=fingerprint,
            ip=client_host,
            expires_in=refresh.exp,
        ),
        settings.auth_jwt.max_sessions,
    )

    return tokens_pair


# async def get_current_user_by_payload(self, payload):
#     user_id = payload.get("sub")
#
#     if not user_id:
#         logger.error('Токен не содержит поля "sub"')
#         raise InvalidTokenException
#
#     try:
#         user_id = int(user_id)
#         user_dao = UserDAO(session)
#         user = await user_dao.find_one_or_none(
#             filter_dict={"id": user_id}, options=[selectinload(User.role)]
#         )
#     except Exception as e:
#         logger.error(e)
#         raise UnauthorizedException
#
#     if not user:
#         raise UnauthorizedException
#
#     return user


async def delete_session(refresh_session: RefreshSession, session: AsyncSession):
    refresh_session_dao = RefreshSessionDAO(session)
    await refresh_session_dao.delete_session(refresh_session)


async def delete_session_for_token(
    refresh_token: str,
    session: AsyncSession,
    delete_all_sessions: bool = False,
):
    refresh_session_dao = RefreshSessionDAO(session)
    if delete_all_sessions:
        refresh_session = await refresh_session_dao.get_session_by_refresh_token(
            refresh_token
        )
        await refresh_session_dao.delete_all_user_sessions(refresh_session.user_id)
        return None
    await refresh_session_dao.delete_last_session_for_token(refresh_token)
    return None


async def check_refresh_session(
    refresh_token: str,
    fingerprint: str,
    session: AsyncSession,
) -> int:
    """
    Проверяет refresh токен и возвращает ID пользователя из сессии.
    1. Проверяет на время жизни
    2. Проверяет на соответствие fingerprint
    :param refresh_token:
    :param fingerprint:
    :param session:
    :return:
    """
    _ = crypto_service.get_payload(refresh_token)
    refresh_session_dao = RefreshSessionDAO(session)
    refresh_session = await refresh_session_dao.get_session_by_refresh_token(
        refresh_token
    )
    if not refresh_session:
        raise RefreshSessionNotFoundException

    if refresh_session.fingerprint != fingerprint:
        logger.error(
            f"Попытка обновления токена с неверным fingerprint. user_id={refresh_session.user_id}!"
        )
        await refresh_session_dao.delete_session(refresh_session)
        raise InvalidFingerprintException

    return refresh_session.user_id


async def refresh(
    fingerprint: str,
    refresh_token: str,
    user_agent: str,
    client_host: str,
    session: AsyncSession,
) -> TokensPair:
    """
    Осуществляет refresh токенов
    :param fingerprint:
    :param refresh_token:
    :param user_agent:
    :param client_host:
    :param session:
    :return:
    """
    user_id = await check_refresh_session(refresh_token, fingerprint, session)
    await delete_session_for_token(refresh_token=refresh_token, session=session)

    return await update_tokens(user_agent, fingerprint, user_id, client_host, session)
