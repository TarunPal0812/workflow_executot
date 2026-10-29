from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./workflows.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


setting = Settings()
settings = setting
