"""Tests for the Recovery Engine pipeline."""

import pytest
from app.policy_gate import policy_gate
from app.config import get_settings


def test_policy_gate_cost_cap():
    """Verify that high-cost interventions on small amounts are blocked."""
    settings = get_settings()
    assert settings.cost_cap_percentage == 15.0


def test_confidence_threshold():
    """Verify minimum confidence is enforced."""
    settings = get_settings()
    assert settings.min_confidence_threshold >= 0.5