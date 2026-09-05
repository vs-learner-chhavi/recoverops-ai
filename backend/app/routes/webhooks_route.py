"""
RecoverOps AI — Webhook Endpoint
Receives Razorpay webhook events and triggers the recovery pipeline.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Any

from app.database import get_db
from app.recovery_engine import recovery_engine
from app.razorpay_client import razorpay_service
from app.audit_logger import AuditLogger

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    db: Any = Depends(get_db),
):
    """
    Receive and process Razorpay webhook events.
    Validates signature, then triggers the recovery engine.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    # Verify webhook signature (skip for simulator events)
    payload = await request.json()
    is_simulated = payload.get("_simulated", False)

    if not is_simulated:
        is_valid = razorpay_service.verify_webhook_signature(
            body.decode("utf-8"), signature
        )
        if not is_valid:
            await AuditLogger.log_error(
                db=db,
                action="webhook_signature_verification",
                error_message="Invalid webhook signature",
            )
            await db.commit()
            raise HTTPException(
                status_code=400, detail="Invalid webhook signature"
            )

    event = payload.get("event", "")

        # Only process events we subscribed to in Razorpay dashboard
    supported_events = [
        "payment.failed",          # Core trigger
        "payment.captured",        # Retry success confirmation
        "payment_link.paid",       # Payment link recovery success
        "payment_link.expired",    # Payment link expired → escalate
        "payment_link.cancelled",  # Customer cancelled link → follow up
    ]

    if event not in supported_events:
        return {"status": "ignored", "event": event}

    # Route to appropriate handler
    if event == "payment.failed":
        payment_entity = (
            payload.get("payload", {})
            .get("payment", {})
            .get("entity", payload)
        )
        result = await recovery_engine.process_failed_payment(
            db=db, payment_data=payment_entity
        )

    elif event == "payment.captured":
        # Mark a previously failed payment as recovered
        payment_entity = (
            payload.get("payload", {})
            .get("payment", {})
            .get("entity", {})
        )
        result = await recovery_engine.mark_recovered(
            db=db, razorpay_payment_id=payment_entity.get("id", "")
        )

    elif event == "payment_link.paid":
        # Payment link was paid — mark associated transaction as recovered
        link_entity = (
            payload.get("payload", {})
            .get("payment_link", {})
            .get("entity", {})
        )
        result = await recovery_engine.mark_link_recovered(
            db=db, payment_link_id=link_entity.get("id", "")
        )

    elif event == "payment_link.expired":
        link_entity = (
            payload.get("payload", {})
            .get("payment_link", {})
            .get("entity", {})
        )
        result = await recovery_engine.escalate_expired_link(
            db=db, payment_link_id=link_entity.get("id", "")
        )

    elif event == "payment_link.cancelled":
        link_entity = (
            payload.get("payload", {})
            .get("payment_link", {})
            .get("entity", {})
        )
        result = await recovery_engine.handle_cancelled_link(
            db=db, payment_link_id=link_entity.get("id", "")
        )