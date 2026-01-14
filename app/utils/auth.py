import datetime

import bcrypt
import jwt


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


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
