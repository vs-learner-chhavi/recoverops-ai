"""
RecoverOps AI — Webhook Event Parser
Parses raw Razorpay webhook payloads into standardized transaction dicts.
"""

from typing import Dict, Any, Optional


def parse_payment_failed_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a 'payment.failed' webhook event into a flat transaction dict
    that the RecoveryEngine can consume.
    """
    payment_entity = (
        payload.get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    if not payment_entity:
        payment_entity = payload

    return {
        "razorpay_payment_id": payment_entity.get("id", ""),
        "razorpay_order_id": payment_entity.get("order_id", ""),
        "amount": float(payment_entity.get("amount", 0)) / 100,  # paise → INR
        "currency": payment_entity.get("currency", "INR"),
        "payment_method": payment_entity.get("method"),
        "bank": payment_entity.get("bank"),
        "card_network": payment_entity.get("card", {}).get("network") if isinstance(payment_entity.get("card"), dict) else None,
        "card_type": payment_entity.get("card", {}).get("type") if isinstance(payment_entity.get("card"), dict) else None,
        "customer_email": payment_entity.get("email"),
        "customer_phone": payment_entity.get("contact"),
        "customer_id": payment_entity.get("customer_id"),
        "error_code": payment_entity.get("error_code"),
        "error_description": payment_entity.get("error_description"),
        "error_source": payment_entity.get("error_source"),
        "error_step": payment_entity.get("error_step"),
        "error_reason": payment_entity.get("error_reason"),
        "failure_category": _classify_failure(payment_entity),
    }


def parse_subscription_halted_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a 'subscription.halted' event."""
    sub_entity = (
        payload.get("payload", {})
        .get("subscription", {})
        .get("entity", {})
    )

    return {
        "razorpay_payment_id": sub_entity.get("id", f"sub_{sub_entity.get('id', 'unknown')}"),
        "razorpay_order_id": sub_entity.get("offer_id", ""),
        "amount": float(sub_entity.get("quantity", 0)) * float(sub_entity.get("amount", 0)) / 100,
        "currency": "INR",
        "payment_method": "subscription",
        "failure_category": "mandate_failed",
        "error_code": "SUBSCRIPTION_HALTED",
        "error_description": f"Subscription halted: {sub_entity.get('status', 'unknown')}",
    }


def _classify_failure(payment_entity: Dict[str, Any]) -> str:
    """
    Classify the failure reason from Razorpay error codes/descriptions
    into one of our standard failure categories.
    """
    error_code = (payment_entity.get("error_code") or "").upper()
    error_desc = (payment_entity.get("error_description") or "").lower()
    error_source = (payment_entity.get("error_source") or "").lower()

    # Fraud
    if "fraud" in error_desc or "risk" in error_desc or "blocked" in error_desc:
        return "fraud_suspected"

    # Card expired
    if "expired" in error_desc or "expiry" in error_desc:
        return "card_expired"

    # Insufficient funds
    if any(kw in error_desc for kw in ["insufficient", "balance", "limit exceeded", "funds"]):
        return "insufficient_funds"

    # Authentication
    if any(kw in error_desc for kw in ["authentication", "otp", "3d secure", "verify"]):
        return "authentication_failed"

    # User cancelled
    if any(kw in error_desc for kw in ["cancel", "abandon", "closed"]):
        return "user_cancelled"

    # Gateway / network
    if error_source == "gateway" or "gateway" in error_desc:
        return "gateway_error"
    if any(kw in error_desc for kw in ["timeout", "network", "connection"]):
        return "network_error"

    # Bank technical
    if error_source == "bank" or "server" in error_desc or "maintenance" in error_desc:
        return "bank_technical"

    return "unknown"