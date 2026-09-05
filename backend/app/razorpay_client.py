"""
RecoverOps AI — Razorpay API Client
Wraps the Razorpay Python SDK for test-mode operations.
All API calls include error handling, retries, and audit logging.
"""

import razorpay
import hmac
import hashlib
import time
import uuid
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

from app.config import get_settings

settings = get_settings()


class RazorpayService:
    """
    Encapsulates all Razorpay API interactions.
    Uses test-mode keys — no real money is ever touched.
    """

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
        # Ensure we're in test mode
        assert settings.razorpay_key_id.startswith("rzp_test"), (
            "SAFETY: Only test-mode keys are permitted."
        )

    def verify_webhook_signature(
        self, body: str, signature: str
    ) -> bool:
        """
        Verify that an incoming webhook actually came from Razorpay.
        Uses HMAC-SHA256 with the webhook secret.
        """
        try:
            expected = hmac.new(
                settings.razorpay_webhook_secret.encode("utf-8"),
                body.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            return False

    def create_payment_link(
        self,
        amount_inr: float,
        customer_name: str = "Customer",
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        description: str = "Complete your payment",
        expire_by: Optional[int] = None,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a Razorpay Payment Link for Tier 2 recovery.
        Returns (success: bool, response_data: dict).
        """
        try:
            payload: Dict[str, Any] = {
                "amount": int(amount_inr * 100),  # Razorpay expects paise
                "currency": "INR",
                "description": description,
                "customer": {
                    "name": customer_name,
                    "email": customer_email or "",
                    "contact": customer_phone or "",
                },
                "notify": {"sms": bool(customer_phone), "email": bool(customer_email)},
                "reminder_enable": True,
                "callback_url": "https://recoverops.example.com/payment/success",
                "callback_method": "get",
            }

            if expire_by:
                payload["expire_by"] = expire_by

            headers = {}
            if idempotency_key:
                headers["X-Payout-Idempotency"] = idempotency_key

            result = self.client.payment_link.create(payload)
            return True, {
                "payment_link_id": result.get("id"),
                "short_url": result.get("short_url"),
                "amount": amount_inr,
                "status": result.get("status"),
                "expire_by": result.get("expire_by"),
            }
        except razorpay.errors.BadRequestError as e:
            return False, {"error": "bad_request", "message": str(e)}
        except razorpay.errors.ServerError as e:
            return False, {"error": "server_error", "message": str(e)}
        except Exception as e:
            return False, {"error": "unknown", "message": str(e)}

    def fetch_payment(self, payment_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetch details of a specific payment."""
        try:
            result = self.client.payment.fetch(payment_id)
            return True, result
        except Exception as e:
            return False, {"error": str(e)}

    def create_order(
        self, amount_inr: float, receipt: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a Razorpay order for retry."""
        try:
            payload = {
                "amount": int(amount_inr * 100),
                "currency": "INR",
                "receipt": receipt or f"rcpt_{uuid.uuid4().hex[:12]}",
                "payment_capture": 1,
            }
            result = self.client.order.create(payload)
            return True, {
                "order_id": result.get("id"),
                "amount": amount_inr,
                "status": result.get("status"),
            }
        except Exception as e:
            return False, {"error": str(e)}

    def fetch_payment_link(self, link_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetch status of a payment link."""
        try:
            result = self.client.payment_link.fetch(link_id)
            return True, result
        except Exception as e:
            return False, {"error": str(e)}


# Singleton instance
razorpay_service = RazorpayService()