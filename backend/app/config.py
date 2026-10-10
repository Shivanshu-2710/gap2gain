from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_service_role_key: str
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5-5"
    free_daily_auto_applies: int = 5
    cors_origins: str = "http://localhost:5173"
    demo_mode: bool = False
    demo_email: str = "demo@gap2gain.app"
    demo_password: str = "change-me-demo-123"
    digest_max_delay_hours: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()