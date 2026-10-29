import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_state = os.getenv("APP_ENV", "development")


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./workflows.db"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=f".env.{env_state}",
        extra="ignore",
    )


setting = Settings()  # type: ignore
settings = setting

