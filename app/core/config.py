from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "JatuhTempo"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/jatuhtempo"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    telegram_bot_token: str = ""

    media_dir: str = "media"
    max_image_size_mb: int = 10

    reminder_check_interval_minutes: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("database_url")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
