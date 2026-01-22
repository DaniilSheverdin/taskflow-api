from fastapi import status, HTTPException

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь с таким email уже существует",
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неправильный логин или пароль",
)

InvalidTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильная структура токена"
)

RefreshTokenNotFoundException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Рефреш Токен отсутствует в заголовке",
)

RefreshSessionNotFoundException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Рефреш токен заблокирован",
)

ExpiredTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Срок жизни токена истек."
)

FingerprintNotFoundException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Fingerprint отсутствует в заголовке",
)

InvalidFingerprintException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неправильный fingerprint",
)

EmptyUserAgentException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Не указан заголовок User-Agent",
)

UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь не найден",
)
