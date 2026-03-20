from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["local", "staging", "production"] = "local"
    app_name: str = "Fact-based AI Content Studio"
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str = "sqlite:///./factstudio.db"
    redis_url: str = "redis://localhost:6379/0"
    storage_mode: Literal["local", "s3"] = "local"
    local_storage_root: str = "./storage"
    s3_endpoint_url: str | None = None
    s3_bucket_name: str = "factstudio-assets"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    claude_api_key: str | None = None
    claude_api_url: str = "https://api.anthropic.com/v1/messages"
    claude_api_version: str = "2023-06-01"
    claude_model: str | None = None
    claude_max_tokens: int = 3000
    claude_temperature: float = 0.2
    script_provider_mode: Literal["mock", "anthropic"] = "mock"
    ecos_api_key: str | None = None
    fred_api_key: str | None = None
    kosis_api_key: str | None = None
    oecd_api_key: str | None = None
    yahoo_enabled: bool = True
    investing_enabled: bool = True
    seeking_alpha_enabled: bool = True
    image_provider: str = "mock-image"
    video_provider: str = "mock-veo"

    freshness_threshold_days: int = 45
    default_date_range_days: int = 365


@lru_cache
def get_settings() -> Settings:
    return Settings()
