"""Tests for Policy Gate safety checks."""

from app.config import get_settings


def test_dnd_hours_configured():
    settings = get_settings()
    assert settings.dnd_start_hour == 21
    assert settings.dnd_end_hour == 9


def test_max_retries_configured():
    settings = get_settings()
    assert settings.max_retries_per_payment == 3
    assert settings.max_contact_attempts == 5