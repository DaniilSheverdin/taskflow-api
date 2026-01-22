import datetime
from pathlib import Path

import bcrypt
import jwt

from app.core.exceptions import ExpiredTokenException, InvalidTokenException
from app.schemas.token import TokensPair, TokenData


class CryptoService:
    def __init__(self, public_key: Path, private_key: Path, algorithm: str):
        self._public_key = public_key
        self._algorithm = algorithm
        self._private_key = private_key

    def encode_jwt(self, payload: dict, private_key: str, algorithm: str):
        encoded = jwt.encode(payload, private_key, algorithm=algorithm)
        return encoded

    def decode_jwt(self, token: str | bytes, public_key: str, algorithm: str):
        return jwt.decode(token, public_key, algorithms=[algorithm])

    def get_payload(self, token: str | bytes) -> dict:
        try:
            payload = self.decode_jwt(
                token, self._public_key.read_text(), algorithm=self._algorithm
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise InvalidTokenException

    def create_tokens_pair(
        self, sub: str, refresh_exp_minutes: int, access_exp_minutes
    ) -> TokensPair:
        now = datetime.datetime.now(datetime.UTC)
        refresh_exp = now + datetime.timedelta(minutes=refresh_exp_minutes)
        access_exp = now + datetime.timedelta(minutes=access_exp_minutes)
        token = self.encode_jwt(
            payload={
                "sub": sub,
                "exp": int(access_exp.timestamp()),
                "iat": int(now.timestamp()),
            },
            private_key=self._private_key.read_text(),
            algorithm=self._algorithm,
        )
        refresh_token = self.encode_jwt(
            payload={
                "sub": sub,
                "exp": int(refresh_exp.timestamp()),
                "iat": int(now.timestamp()),
            },
            private_key=self._private_key.read_text(),
            algorithm=self._algorithm,
        )

        return TokensPair(
            refresh=TokenData(token=refresh_token, exp=int(refresh_exp.timestamp())),
            access=TokenData(token=token, exp=int(access_exp.timestamp())),
        )

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    @staticmethod
    def validate_hashed(compared_str: str, hashed_str: bytes) -> bool:
        return bcrypt.checkpw(compared_str.encode(), hashed_str)
