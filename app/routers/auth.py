from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao.user import UserDAO
from app.core.dependencies.auth import (
    authenticate_user,
    get_current_user,
    check_refresh_token,
)
from app.core.dependencies.dao import (
    get_session_with_commit,
)
from app.core.models import User
from app.core.schemas.token import Token
from app.core.schemas.user import (
    UserRegister,
    EmailModel,
    UserCreate,
    UserInfo,
)
from app.exceptions import UserAlreadyExistsException
from app.utils.auth import hash_password, create_tokens_pair

router = APIRouter()


@router.post("/register/")
async def register(
    user_data: UserRegister, session: AsyncSession = Depends(get_session_with_commit)
):
    user_dao = UserDAO(session)
    probably_existing_user = await user_dao.find_one_or_none(
        filter=EmailModel(email=user_data.email)
    )
    if probably_existing_user:
        raise UserAlreadyExistsException

    user_data_dict = user_data.model_dump()
    user_data_dict["password"] = hash_password(user_data_dict["password"])

    await user_dao.create(data=UserCreate(**user_data_dict))

    return {"message": "Регистрация прошла успешно"}


@router.post("/login/", response_model=Token)
async def jwt_login(
    response: Response,
    user: User = Depends(authenticate_user),
):
    return _update_tokens(response, user.id)


@router.post("/refresh/", response_model=Token)
async def jwt_refresh(response: Response, user: User = Depends(check_refresh_token)):
    return _update_tokens(response, user.id)


@router.get("/users/me/")
async def get_current_user(user: User = Depends(get_current_user)):
    return UserInfo.model_validate(user)


@router.post("/logout/")
async def logout(response: Response):
    """
    Удаляет рефреш токен из кук
    :param response:
    :return:
    """
    response.delete_cookie("refresh_token")
    return {"ok": True}


def _update_tokens(response: Response, user_id: int):
    tokens = create_tokens_pair(str(user_id))
    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        secure=False,
    )

    return Token(
        access_token=tokens.get("access_token"), message="Токены обновлены.", ok=True
    )
