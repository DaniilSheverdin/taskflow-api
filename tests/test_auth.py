import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.user import UserDAO
from app.schemas.user import UserCreate
from app.services.crypto import CryptoService


@pytest.fixture(scope="module")
def password():
    return "testpassword"


@pytest.fixture(scope="module")
def hashed_password(password):
    return CryptoService.hash_password(password)


@pytest.fixture(autouse=True)
async def create_user(override_get_session: AsyncSession, hashed_password):
    user_dao = UserDAO(override_get_session)
    await user_dao.create(
        UserCreate(
            email="test@test.com",
            password=hashed_password,
            first_name="Test",
            last_name="User",
        )
    )
    return await override_get_session.commit()


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register/",
        json={
            "email": "test2@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Регистрация прошла успешно"}


@pytest.mark.asyncio
async def test_register_user_already_exists(client: AsyncClient):
    response = await client.post(
        "/api/auth/register/",
        json={
            "email": "test@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Пользователь с таким email уже существует"}


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, password):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": "test@test.com",
            "password": password,
            "fingerprint": "test_fingerprint",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "access_token" in data
    assert "expires_in" in data
    assert data["message"] == "Токены успешно обновлены."


@pytest.mark.asyncio
async def test_login_user_incorrect_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": "test@test.com",
            "password": "wrong_password",
            "fingerprint": "test_fingerprint",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Неправильный логин или пароль"}


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, password):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": "test@test.com",
            "password": password,
            "fingerprint": "test_fingerprint",
        },
    )
    cookies = response.cookies
    refresh_token = cookies.get("refresh_token")
    response = await client.post(
        "/api/auth/refresh",
        json="test_fingerprint",
        cookies={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "access_token" in data
    assert "expires_in" in data
    assert data["message"] == "Токены успешно обновлены."


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    response = await client.post(
        "/api/auth/refresh",
        json="test_fingerprint",
        cookies={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token_invalid_fingerprint(client: AsyncClient, password):
    response = await client.post(
        "/api/auth/login/",
        json={
            "email": "test@test.com",
            "password": password,
            "fingerprint": "test_fingerprint",
        },
    )
    cookies = response.cookies
    refresh_token = cookies.get("refresh_token")
    response = await client.post(
        "/api/auth/refresh",
        json="wrong_fingerprint",
        cookies={"refresh_token": refresh_token},
    )
    assert response.status_code == 401
