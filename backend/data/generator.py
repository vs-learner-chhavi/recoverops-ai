"""
RecoverOps AI — Synthetic Transaction Data Generator (FIXED)
Generates 1,500+ realistic failed payment events with correct ML features.
"""

import random
import uuid
import json
import csv
import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from pathlib import Path


# ──────────────────────── Configuration ────────────────────────

BANKS = [
    "HDFC", "ICICI", "SBI", "Axis", "Kotak", "Yes Bank",
    "PNB", "BOB", "IndusInd", "IDBI", "Federal", "RBL",
]

CARD_NETWORKS = ["visa", "mastercard", "rupay", "amex"]
CARD_TYPES = ["credit", "debit"]
PAYMENT_METHODS = ["card", "upi", "netbanking", "wallet"]

FAILURE_PROFILES = {
    "bank_technical": {
        "weight": 0.25,
        "codes": ["BAD_REQUEST_ERROR", "GATEWAY_ERROR", "SERVER_ERROR"],
        "descriptions": [
            "Bank servers are currently unavailable",
            "Transaction timed out at bank end",
            "Issuer bank system under maintenance",
            "Gateway response timeout exceeded",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.72,
    },
    "insufficient_funds": {
        "weight": 0.20,
        "codes": ["BAD_REQUEST_ERROR"],
        "descriptions": [
            "Insufficient funds in the account",
            "Card limit exceeded for the day",
            "Available balance is less than transaction amount",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.35,
    },
    "card_expired": {
        "weight": 0.10,
        "codes": ["BAD_REQUEST_ERROR"],
        "descriptions": [
            "Card has expired",
            "Card validity date has passed",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.25,
    },
    "authentication_failed": {
        "weight": 0.15,
        "codes": ["BAD_REQUEST_ERROR"],
        "descriptions": [
            "3D Secure authentication failed",
            "OTP verification failed",
            "Customer failed to complete authentication",
            "Authentication was not completed in time",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.55,
    },
    "network_error": {
        "weight": 0.10,
        "codes": ["GATEWAY_ERROR", "SERVER_ERROR"],
        "descriptions": [
            "Network connection lost during transaction",
            "Request timed out",
            "Connection reset by peer",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.80,
    },
    "fraud_suspected": {
        "weight": 0.05,
        "codes": ["BAD_REQUEST_ERROR"],
        "descriptions": [
            "Transaction declined due to risk check",
            "Suspected fraudulent transaction",
            "Card blocked by issuing bank",
        ],
        "recoverable": False,
        "base_recovery_prob": 0.05,
    },
    "user_cancelled": {
        "weight": 0.10,
        "codes": ["BAD_REQUEST_ERROR"],
        "descriptions": [
            "Payment cancelled by user",
            "Customer closed the payment page",
            "Transaction abandoned at checkout",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.40,
    },
    "gateway_error": {
        "weight": 0.05,
        "codes": ["GATEWAY_ERROR"],
        "descriptions": [
            "Payment gateway is temporarily down",
            "Gateway returned an unexpected response",
        ],
        "recoverable": True,
        "base_recovery_prob": 0.75,
    },
}

# ── These MUST match ml/feature_engineering.py exactly ──
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

HIGH_RISK_BANKS = {"Yes Bank", "RBL", "IDBI", "PNB"}

CUSTOMER_NAMES = [
    "Aarav Sharma", "Priya Patel", "Rohan Gupta", "Sneha Reddy",
    "Vikram Singh", "Ananya Joshi", "Karthik Nair", "Divya Kumar",
    "Rahul Verma", "Meera Iyer", "Arjun Mehta", "Pooja Desai",
    "Siddharth Rao", "Neha Agarwal", "Amit Tiwari", "Kavitha Menon",
    "Rajesh Pandey", "Swathi Krishnan", "Manish Saxena", "Lakshmi Bhat",
]


def _generate_amount() -> float:
    ranges = [
        (99, 500, 0.25),
        (500, 2000, 0.30),
        (2000, 10000, 0.25),
        (10000, 50000, 0.15),
        (50000, 200000, 0.05),
    ]
    r = random.random()
    cumulative = 0
    for low, high, weight in ranges:
        cumulative += weight
        if r <= cumulative:
            return round(random.uniform(low, high), 2)
    return round(random.uniform(500, 5000), 2)


def _generate_timestamp(days_back: int = 30) -> datetime:
    now = datetime.now(timezone.utc)
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return now - delta


def _select_failure_category() -> str:
    categories = list(FAILURE_PROFILES.keys())
    weights = [FAILURE_PROFILES[c]["weight"] for c in categories]
    return random.choices(categories, weights=weights, k=1)[0]


def _compute_features(record: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute features that EXACTLY match ml/feature_engineering.py get_feature_names().
    This is the critical fix — previously the column names were mismatched.
    """
    amount = record["amount"]
    hour = record["failed_at"].hour
    day_of_week = record["failed_at"].weekday()
    payment_method = record["payment_method"]
    bank = record["bank"]
    failure_category = record["failure_category"]

    return {
        # Amount features
        "amount": amount,
        "amount_log": round(math.log10(max(1, amount)), 4),
        "amount_bucket": float(
            0 if amount < 500
            else 1 if amount < 2000
            else 2 if amount < 10000
            else 3 if amount < 50000
            else 4
        ),

        # Time features
        "hour": float(hour),
        "day_of_week": float(day_of_week),
        "is_business_hours": 1.0 if 9 <= hour <= 18 else 0.0,
        "is_late_night": 1.0 if hour >= 22 or hour <= 5 else 0.0,
        "is_weekend": 1.0 if day_of_week >= 5 else 0.0,
        "is_peak_hours": 1.0 if (10 <= hour <= 14 or 18 <= hour <= 21) else 0.0,

        # Payment method one-hot
        "is_card": 1.0 if payment_method == "card" else 0.0,
        "is_upi": 1.0 if payment_method == "upi" else 0.0,
        "is_netbanking": 1.0 if payment_method == "netbanking" else 0.0,
        "is_wallet": 1.0 if payment_method == "wallet" else 0.0,

        # Bank risk
        "bank_risk_score": 0.7 if bank in HIGH_RISK_BANKS else 0.3,

        # Failure category (encoded as float)
        "failure_category_encoded": float(
            FAILURE_CATEGORY_MAP.get(failure_category, 9)
        ),

        # Recoverability
        "is_recoverable_category": 0.0 if failure_category == "fraud_suspected" else 1.0,
    }


def generate_transaction() -> Dict[str, Any]:
    failure_category = _select_failure_category()
    profile = FAILURE_PROFILES[failure_category]

    payment_method = random.choice(PAYMENT_METHODS)
    customer = random.choice(CUSTOMER_NAMES)
    failed_at = _generate_timestamp()

    record = {
        "razorpay_payment_id": f"pay_test_{uuid.uuid4().hex[:14]}",
        "razorpay_order_id": f"order_test_{uuid.uuid4().hex[:12]}",
        "amount": _generate_amount(),
        "currency": "INR",
        "payment_method": payment_method,
        "bank": random.choice(BANKS),
        "card_network": random.choice(CARD_NETWORKS) if payment_method == "card" else None,
        "card_type": random.choice(CARD_TYPES) if payment_method == "card" else None,
        "customer_name": customer,
        "customer_email": f"{customer.lower().replace(' ', '.')}@example.com",
        "customer_phone": f"98{random.randint(10000000, 99999999)}",
        "error_code": random.choice(profile["codes"]),
        "error_description": random.choice(profile["descriptions"]),
        "error_source": random.choice(["bank", "gateway", "customer"]),
        "error_step": random.choice(["payment_authorization", "payment_capture", "otp_verification"]),
        "failure_category": failure_category,
        "failed_at": failed_at,
    }

    # Compute ML features (now correctly aligned)
    features = _compute_features(record)
    record["features"] = features

    # ── Ground truth label with STRONG feature correlations ──
    

    base_prob = profile["base_recovery_prob"]

    # Strong feature adjustments (these create learnable signal)
    score = base_prob

    # Time effects (strong)
    if features["is_business_hours"]:
        score += 0.12
    if features["is_late_night"]:
        score -= 0.18
    if features["is_peak_hours"]:
        score += 0.08
    if features["is_weekend"]:
        score -= 0.06

    # Amount effects (strong)
    if features["amount_bucket"] >= 4:      # >50K
        score -= 0.20
    elif features["amount_bucket"] >= 3:    # 10K-50K
        score -= 0.12
    elif features["amount_bucket"] <= 0:    # <500
        score += 0.10

    # Payment method effects (strong)
    if payment_method == "upi":
        score += 0.12
    elif payment_method == "wallet":
        score += 0.08
    elif payment_method == "netbanking":
        score -= 0.05

    # Bank risk (strong)
    if features["bank_risk_score"] > 0.5:
        score -= 0.15

    # Failure category overrides (very strong)
    if failure_category == "fraud_suspected":
        score = 0.02
    elif failure_category == "network_error":
        score += 0.10
    elif failure_category == "bank_technical":
        score += 0.05
    elif failure_category == "card_expired":
        score -= 0.08

    # Clamp
    score = max(0.01, min(0.99, score))

    # Deterministic label with LOW noise (only 15% random flip)
    
    noise = random.gauss(0, 0.08)  # Small Gaussian noise
    final_prob = max(0.01, min(0.99, score + noise))

    record["recovery_probability_true"] = round(final_prob, 4)
    record["was_recovered"] = final_prob > 0.50  # Deterministic threshold
    return record


def generate_dataset(n: int = 1500) -> List[Dict[str, Any]]:
    return [generate_transaction() for _ in range(n)]


def save_dataset(
    dataset: List[Dict[str, Any]],
    output_dir: str = "data/synthetic",
):
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    # JSON export
    json_data = []
    for record in dataset:
        r = {**record}
        r["failed_at"] = r["failed_at"].isoformat()
        json_data.append(r)

    with open(path / "transactions.json", "w") as f:
        json.dump(json_data, f, indent=2, default=str)

    if not dataset:
        return

    # CSV headers (strictly deduplicated)
    feature_keys = list(dataset[0]["features"].keys())
    meta_headers = ["razorpay_payment_id", "payment_method", "bank", "failure_category", "was_recovered"]
    csv_headers = meta_headers + feature_keys

    with open(path / "training_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()
        for record in dataset:
            row = {
                "razorpay_payment_id": record["razorpay_payment_id"],
                "payment_method": record["payment_method"],
                "bank": record["bank"],
                "failure_category": record["failure_category"],
                "was_recovered": int(record["was_recovered"]),
            }
            # Add features without duplicate keys
            row.update(record["features"])
            writer.writerow(row)

    print(f"✅ Generated {len(dataset)} transactions")
    print(f"   → JSON: {path / 'transactions.json'}")
    print(f"   → CSV:  {path / 'training_data.csv'}")

    recovered = sum(1 for r in dataset if r["was_recovered"])
    total_amount = sum(r["amount"] for r in dataset)
    recovered_amount = sum(r["amount"] for r in dataset if r["was_recovered"])
    print(f"   → Recovery rate: {recovered/len(dataset)*100:.1f}%")
    print(f"   → Total failed: ₹{total_amount:,.2f}")
    print(f"   → Recoverable:  ₹{recovered_amount:,.2f}")


if __name__ == "__main__":
    dataset = generate_dataset(1500)
    save_dataset(dataset)