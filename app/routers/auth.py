from fastapi import APIRouter, Response, Body
from fastapi.params import Depends
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.auth import (
    get_auth_context,
    get_refresh_token,
)
from app.dependencies.dao import (
    get_session_without_commit,
)
from app.schemas.token import LoginResponse, ContextData, TokensPair
from app.schemas.user import (
    UserRegister,
    UserCredentials,
    UserLogin,
)
from app.services import auth
from app.services.auth import register_new_user, update_tokens

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/")
async def register(
    user_data: UserRegister, session: AsyncSession = Depends(get_session_without_commit)
):
    await register_new_user(user_data, session)
    return {"message": "Регистрация прошла успешно"}


@router.post("/login/", response_model=LoginResponse)
async def jwt_login(
    response: Response,
    data: UserCredentials,
    context: ContextData = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Устанавливает refresh токен в куку, access token в тело ответа
    :param response:
    :param data:
    :param context:
    :param session:
    :return:
    """
    user = await auth.get_auth_user(
        UserLogin(email=data.email, password=data.password), session
    )

    tokens_pair = await update_tokens(
        user_agent=context.user_agent,
        fingerprint=data.fingerprint,
        client_host=context.client_host,
        user_id=user.id,
        session=session,
    )
    return _update_tokens(response, tokens_pair)


@router.post("/refresh", response_model=LoginResponse)
async def jwt_refresh(
    response: Response,
    fingerprint: str = Body(...),
    refresh_token: str = Depends(get_refresh_token),
    context: ContextData = Depends(get_auth_context),
    session: AsyncSession = Depends(get_session_without_commit),
):
    tokens_pair = await auth.refresh(
        fingerprint=fingerprint,
        refresh_token=refresh_token,
        session=session,
        user_agent=context.user_agent,
        client_host=context.client_host,
    )
    return _update_tokens(response, tokens_pair)


def _update_tokens(response: Response, tokens_pair: TokensPair):
    response.set_cookie(
        domain=f".{settings.DOMAIN}",
        max_age=settings.auth_jwt.refresh_token_expire_minutes * 60,
        path="/api/auth",
        key="refresh_token",
        value=tokens_pair.refresh.token,
        httponly=True,
        secure=settings.auth_jwt.secure_cookie,
        samesite="lax",
    )
    return LoginResponse(
        ok=True,
        access_token=tokens_pair.access.token,
        expires_in=tokens_pair.access.exp,
        message="Токены успешно обновлены.",
    )


@router.post("/logout/")
async def logout(
    response: Response,
    all_sessions: bool = False,
    refresh_token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_session_without_commit),
):
    """
    Удаляет рефреш токен из кук. Удаляет рефреш сессию.
    :param all_sessions:
    :param session:
    :param refresh_token:
    :param response:
    :return:
    """
    response.delete_cookie("refresh_token")
    await auth.delete_session_for_token(
        refresh_token=refresh_token, delete_all_sessions=all_sessions, session=session
    )

    return {"ok": True}
