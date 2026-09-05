"""
RecoverOps AI — Feature Engineering Pipeline
Transforms raw transaction data into ML-ready features.
"""

import math
from typing import Dict, Any


FAILURE_CATEGORY_MAP = {
    "bank_technical": 0,
    "insufficient_funds": 1,
    "card_expired": 2,
    "authentication_failed": 3,
    "network_error": 4,
    "fraud_suspected": 5,
    "user_cancelled": 6,
    "gateway_error": 7,
    "mandate_failed": 8,
    "unknown": 9,
}

PAYMENT_METHOD_MAP = {
    "card": 0,
    "upi": 1,
    "netbanking": 2,
    "wallet": 3,
}

HIGH_RISK_BANKS = {"Yes Bank", "RBL", "IDBI", "PNB"}


def extract_features(transaction: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract a fixed-dimension feature vector from a transaction record.
    Returns a dict of feature_name -> float value.
    """
    amount = float(transaction.get("amount", 0))
    hour = int(transaction.get("hour", 12))
    day_of_week = int(transaction.get("day_of_week", 0))
    payment_method = transaction.get("payment_method", "card")
    bank = transaction.get("bank", "Unknown")
    failure_category = transaction.get("failure_category", "unknown")

    features = {
        # Amount features
        "amount": amount,
        "amount_log": round(math.log10(max(1, amount)), 4),
        "amount_bucket": (
            0 if amount < 500
            else 1 if amount < 2000
            else 2 if amount < 10000
            else 3 if amount < 50000
            else 4
        ),

        # Time features
        "hour": hour,
        "day_of_week": day_of_week,
        "is_business_hours": 1.0 if 9 <= hour <= 18 else 0.0,
        "is_late_night": 1.0 if hour >= 22 or hour <= 5 else 0.0,
        "is_weekend": 1.0 if day_of_week >= 5 else 0.0,
        "is_peak_hours": 1.0 if 10 <= hour <= 14 or 18 <= hour <= 21 else 0.0,

        # Payment method one-hot
        "is_card": 1.0 if payment_method == "card" else 0.0,
        "is_upi": 1.0 if payment_method == "upi" else 0.0,
        "is_netbanking": 1.0 if payment_method == "netbanking" else 0.0,
        "is_wallet": 1.0 if payment_method == "wallet" else 0.0,

        # Bank risk
        "bank_risk_score": 0.7 if bank in HIGH_RISK_BANKS else 0.3,

        # Failure category
        "failure_category_encoded": float(
            FAILURE_CATEGORY_MAP.get(failure_category, 9)
        ),

        # Derived
        "is_recoverable_category": 0.0 if failure_category == "fraud_suspected" else 1.0,
    }

    return features


def get_feature_names() -> list:
    """Return ordered list of feature names for the ML model."""
    return [
        "amount", "amount_log", "amount_bucket",
        "hour", "day_of_week",
        "is_business_hours", "is_late_night", "is_weekend", "is_peak_hours",
        "is_card", "is_upi", "is_netbanking", "is_wallet",
        "bank_risk_score",
        "failure_category_encoded",
        "is_recoverable_category",
    ]