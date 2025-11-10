from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Настройки приложения"""

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
