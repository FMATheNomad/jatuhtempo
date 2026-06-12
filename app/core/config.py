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

    api_rate_limit: int = 30
    api_rate_window_seconds: int = 60
    auth_rate_limit: int = 10
    auth_rate_window_seconds: int = 60

    platform_rate_confidence_divisor: int = 20
    platform_rate_outlier_min: float = 0.1
    platform_rate_outlier_max: float = 50.0
    platform_rate_ema_alpha_max: float = 0.3
    platform_rate_time_decay_max: float = 2.0
    platform_rate_time_decay_period_days: int = 90

    platform_matcher_tiebreaker_min: int = 3
    platform_matcher_tiebreaker_ratio: float = 0.25
    platform_matcher_confidence_reinforce_weight: float = 0.5
    platform_matcher_min_keyword_length: int = 3

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    web_url: str = ""

    encryption_key: str = ""
    crypto_salt: str = "jatuh-tempo-salt"
    sentry_dsn: str = ""
    polar_access_token: str = ""
    polar_product_id: str = ""
    polar_success_url: str = ""
    polar_webhook_secret: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_from: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("database_url")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
