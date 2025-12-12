from fastapi import status, HTTPException

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь с таким email уже существует",
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неправильный логин или пароль",
)
