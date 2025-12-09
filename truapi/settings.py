from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    NAME: str = "McGuire Technology"
    VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()


# Convenient module-level singleton
settings = get_settings()
