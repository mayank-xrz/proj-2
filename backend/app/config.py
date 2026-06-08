"""Application configuration loaded from environment variables and business YAML."""

import yaml
from pathlib import Path
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OmniDimension integration
    omnidim_api_key: str = Field(default="sk-omni-placeholder", alias="OMNIDIM_API_KEY")
    omnidim_agent_id: str = Field(default="agent_placeholder_id", alias="OMNIDIM_AGENT_ID")
    omnidim_webhook_secret: str = Field(default="whsec_placeholder", alias="OMNIDIM_WEBHOOK_SECRET")
    omnidim_base_url: str = Field(default="https://api.omnidim.io/v1", alias="OMNIDIM_BASE_URL")

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    app_secret_key: str = Field(default="change-me-in-production", alias="APP_SECRET_KEY")
    database_url: str = Field(default="sqlite+aiosqlite:///./voice_receptionist.db", alias="DATABASE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    # Business config path
    business_config_path: str = Field(
        default="business_config.yaml",
        alias="BUSINESS_CONFIG_PATH",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def load_business_config() -> dict:
    """Load and return the per-business YAML configuration."""
    settings = get_settings()
    config_path = Path(settings.business_config_path)
    if not config_path.exists():
        config_path = Path(__file__).parent.parent / "business_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
