from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    port: int = Field(default=8000, alias="PORT")
    database_url: str = Field(default="sqlite+pysqlite:///./local.db", alias="DATABASE_URL")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_audience: str = Field(default="daily-reporter", alias="JWT_AUDIENCE")
    jwt_issuer: str = Field(default="http://localhost", alias="JWT_ISSUER")

    teams_webhook_secret: str = Field(default="", alias="TEAMS_WEBHOOK_SECRET")
    default_timezone: str = Field(default="America/Sao_Paulo", alias="DEFAULT_TIMEZONE")

    ai_default_provider: str = Field(default="dummy", alias="AI_DEFAULT_PROVIDER")
    ai_timeout_seconds: int = Field(default=10, alias="AI_TIMEOUT_SECONDS")
    ai_max_cost_per_day_cents: int = Field(default=500, alias="AI_MAX_COST_PER_DAY_CENTS")

    rate_limit_teams_per_minute: int = Field(default=60, alias="RATE_LIMIT_TEAMS_PER_MINUTE")
    prometheus_metrics_enabled: bool = Field(default=True, alias="PROMETHEUS_METRICS_ENABLED")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # eager load for simplicity

