from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao.user import UserDAO
from app.core.dependencies.dao import get_session_without_commit
from app.core.models import User
from app.core.schemas.user import EmailModel, UserLogin
from app.exceptions import IncorrectEmailOrPasswordException
from app.utils.auth import validate_password


async def authenticate_user(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_session_without_commit),
) -> User:
    """
    Аутентифицирует пользователя по email и паролю.
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
