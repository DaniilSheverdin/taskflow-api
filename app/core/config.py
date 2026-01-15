from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

BASE_DIR = Path(__file__).parent.parent.parent


class AuthJWT(BaseSettings):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 10080


class ApiConfig(BaseSettings):
    prefix: str = "/api"


class Settings(BaseSettings):
    """Настройки приложения"""

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    POOL_SIZE: int
    POOL_OVERFLOW: int
    POOL_TIMEOUT: int
    LOGS_DIR: Path = BASE_DIR / "logs"
    LOG_INFO_ENABLED: bool
    LOG_ERROR_ENABLED: bool
    LOG_DEBUG_ENABLED: bool
    api_config: ApiConfig = ApiConfig()
    auth_jwt: AuthJWT = AuthJWT()
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
