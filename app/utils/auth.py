import datetime

import bcrypt
import jwt

from app.core.config import settings
from app.exceptions import ExpiredTokenException


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


def create_tokens_pair(sub: str) -> dict:
    jwt_payload = {
        "sub": sub,
    }
    token = encode_jwt(
        payload=jwt_payload,
        private_key=settings.auth_jwt.private_key.read_text(),
        algorithm=settings.auth_jwt.algorithm,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )
    refresh_token = encode_jwt(
        payload=jwt_payload,
        private_key=settings.auth_jwt.private_key.read_text(),
        algorithm=settings.auth_jwt.algorithm,
        expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )

    return {"access_token": token, "refresh_token": refresh_token}


def encode_jwt(payload: dict, private_key: str, algorithm: str, expire_minutes: int):
    to_encode = payload.copy()
    now = datetime.datetime.now(datetime.UTC)
    expires = now + datetime.timedelta(minutes=expire_minutes)
    to_encode.update(exp=expires, iat=now)
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str | bytes, public_key: str, algorithm: str):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def get_payload_for_credentials(token):
    try:
        payload = decode_jwt(
            token,
            public_key=settings.auth_jwt.public_key.read_text(),
            algorithm=settings.auth_jwt.algorithm,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException
