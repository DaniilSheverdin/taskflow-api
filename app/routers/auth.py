from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies.auth import authenticate_user, get_current_user
from app.core.dependencies.dao import (
    get_session_with_commit,
    get_session_without_commit,
)
from app.core.models import User
from app.core.schemas.user import (
    UserRegister,
    EmailModel,
    UserCreate,
    TokenInfo,
    UserInfo,
)
from app.core.dao.user import UserDAO
from app.exceptions import UserAlreadyExistsException
from app.utils.auth import encode_jwt, hash_password

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


@router.post("/login/", response_model=TokenInfo)
async def jwt_login(
    user: User = Depends(authenticate_user),
):
    jwt_payload = {
        "sub": user.email,
    }
    token = encode_jwt(
        payload=jwt_payload,
        private_key=settings.auth_jwt.private_key.read_text(),
        algorithm=settings.auth_jwt.algorithm,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )
    return TokenInfo(access_token=token, token_type="bearer")


@router.get("/users/me/")
async def get_current_user(user: User = Depends(get_current_user)):
    return UserInfo.model_validate(user)
