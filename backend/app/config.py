"""
RecoverOps AI — Configuration Management
Centralizes all environment variables and system constants.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


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
    debug: bool = True

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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()