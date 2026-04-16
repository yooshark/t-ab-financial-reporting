from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

print(ENV_FILE)


class SeedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="SEED_",
        extra="ignore",
    )

    ENABLED: bool = True
    BATCH: int = 1000
    USERS_COUNT: int = 120
    TRANSACTIONS_COUNT: int = 12000


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="DB_",
        extra="ignore",
    )
    USER: str = "postgres"
    PASSWORD: str = Field(default=...)
    NAME: str = "ab-financial-reporting"
    HOST: str = "localhost"
    PORT: int = 5432
    DRIVER: str = "asyncpg"

    ECHO: bool = False
    TIMEOUT: int = 5

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{self.DRIVER}",
                username=self.USER,
                password=self.PASSWORD,
                host=self.HOST,
                port=self.PORT,
                path=self.NAME,
            ),
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix="APP_",
        extra="ignore",
    )

    DEBUG: bool = True

    HOST: str = "localhost"
    PORT: int = 8000
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:8000",
    ]
    ALLOW_ORIGIN_REGEX: str | None = r"https://(.*\.)?localhost\.com"

    db: DatabaseSettings = DatabaseSettings()
    seed: SeedSettings = SeedSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
