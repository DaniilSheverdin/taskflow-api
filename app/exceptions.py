from fastapi import status, HTTPException

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь с таким email уже существует",
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неправильный логин или пароль",
)

UnauthorizedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неправильный токен",
)

InvalidTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильная структура токена"
)

RefreshTokenNotFoundException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Рефреш Токен отсутствует в заголовке",
)

ExpiredTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Срок жизни токена истек."
)
