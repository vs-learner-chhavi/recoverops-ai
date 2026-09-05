"""Tests for the Diagnostic Engine."""

from app.diagnostic_engine import diagnostic_engine


def test_diagnostic_returns_structure():
    result = diagnostic_engine.diagnose({
        "amount": 1500,
        "payment_method": "card",
        "bank": "HDFC",
        "failure_category": "bank_technical",
        "hour": 14,
        "day_of_week": 2,
    })

    assert "recovery_probability" in result
    assert "recommended_intervention" in result
    assert "xai_explanation" in result
    assert 0 <= result["recovery_probability"] <= 1