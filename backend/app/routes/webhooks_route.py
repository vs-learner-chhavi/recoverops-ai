"""
RecoverOps AI — Webhook Endpoint
Receives Razorpay webhook events and triggers the recovery pipeline.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.audit_logger import AuditLogger
from app.database import get_db
from app.recovery_engine import recovery_engine
from app.razorpay_client import razorpay_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    db: Any = Depends(get_db),
):
    """Receive and process Razorpay webhook events."""
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    # Simulator events are intentionally unsigned; real Razorpay events must verify.
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
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = payload.get("event", "")

    supported_events = [
        "payment.failed",
        "payment.captured",
        "payment_link.paid",
        "payment_link.expired",
        "payment_link.cancelled",
    ]

    if event not in supported_events:
        return {"status": "ignored", "event": event}

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
        payment_entity = (
            payload.get("payload", {})
            .get("payment", {})
            .get("entity", {})
        )
        result = await recovery_engine.mark_recovered(
            db=db, razorpay_payment_id=payment_entity.get("id", "")
        )

    elif event == "payment_link.paid":
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

    else:  # payment_link.cancelled
        link_entity = (
            payload.get("payload", {})
            .get("payment_link", {})
            .get("entity", {})
        )
        result = await recovery_engine.handle_cancelled_link(
            db=db, payment_link_id=link_entity.get("id", "")
        )

    await db.commit()
    return {"status": "processed", "event": event, "result": result}
