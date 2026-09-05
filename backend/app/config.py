"""
RecoverOps AI — Configuration Management
Centralizes all environment variables and system constants.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Razorpay
    razorpay_key_id: str
    razorpay_key_secret: str
    razorpay_webhook_secret: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./recoverops.db"

    # OpenAI
    openai_api_key: Optional[str] = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS — comma-separated browser origins, e.g.
    # https://recoverops-ai.vercel.app,http://localhost:3000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Policy Configuration
    max_retries_per_payment: int = 3
    max_contact_attempts: int = 5
    dnd_start_hour: int = 21
    dnd_end_hour: int = 9
    cost_cap_percentage: float = 15.0
    min_confidence_threshold: float = 0.65

    # Recovery Timing (minutes)
    tier1_retry_delay_minutes: int = 45
    tier2_link_expiry_hours: int = 24
    tier3_nudge_delay_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def normalized_database_url(self) -> str:
        """Render often supplies postgresql://; async SQLAlchemy needs asyncpg."""
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
