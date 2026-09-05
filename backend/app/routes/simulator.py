"""
RecoverOps AI — Payment Failure Simulator
Allows judges/users to trigger simulated failed payments for demo purposes.
"""

import random
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit_logger import AuditLogger
from app.database import get_db
from app.recovery_engine import recovery_engine
from app.schemas import SimulatePaymentRequest, SimulatePaymentResponse

router = APIRouter(prefix="/simulator", tags=["Simulator"])


FAILURE_TEMPLATES = {
    "bank_technical": {
        "error_code": "GATEWAY_ERROR",
        "error_description": "Bank servers are currently unavailable",
        "error_source": "bank",
        "error_step": "payment_authorization",
    },
    "insufficient_funds": {
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "Insufficient funds in the account",
        "error_source": "bank",
        "error_step": "payment_authorization",
    },
    "card_expired": {
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "Card has expired",
        "error_source": "customer",
        "error_step": "payment_authorization",
    },
    "authentication_failed": {
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "3D Secure authentication failed",
        "error_source": "customer",
        "error_step": "otp_verification",
    },
    "network_error": {
        "error_code": "GATEWAY_ERROR",
        "error_description": "Network connection lost during transaction",
        "error_source": "gateway",
        "error_step": "payment_authorization",
    },
    "fraud_suspected": {
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "Transaction declined due to risk check",
        "error_source": "bank",
        "error_step": "payment_authorization",
    },
    "user_cancelled": {
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "Payment cancelled by user",
        "error_source": "customer",
        "error_step": "payment_authorization",
    },
    "gateway_error": {
        "error_code": "GATEWAY_ERROR",
        "error_description": "Payment gateway is temporarily down",
        "error_source": "gateway",
        "error_step": "payment_authorization",
    },
}


@router.post("/trigger", response_model=SimulatePaymentResponse)
async def simulate_failed_payment(
    request: SimulatePaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Simulate a failed payment and trigger the full recovery pipeline."""
    template = FAILURE_TEMPLATES.get(
        request.failure_reason,
        FAILURE_TEMPLATES["bank_technical"],
    )

    razorpay_payment_id = f"pay_sim_{uuid.uuid4().hex[:14]}"
    payment_data = {
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_order_id": f"order_sim_{uuid.uuid4().hex[:12]}",
        "amount": request.amount,
        "currency": "INR",
        "payment_method": request.payment_method,
        "bank": request.bank,
        "card_network": request.card_network,
        "customer_email": request.customer_email,
        "customer_phone": request.customer_phone,
        "failure_category": request.failure_reason,
        **template,
    }

    await AuditLogger.log(
        db=db,
        event_type="simulation_triggered",
        event_category="system",
        action="simulate_payment_failure",
        description=f"Simulated {request.failure_reason} failure for ₹{request.amount:,.2f}",
        metadata={"payment_data": payment_data},
    )

    result = await recovery_engine.process_failed_payment(
        db=db, payment_data=payment_data
    )
    await db.commit()

    intervention = result.get("intervention") or {}
    status = result.get("status", "unknown")
    recovered = bool(result.get("recovered"))

    nice_message = result.get("message")
    if not nice_message:
        if recovered:
            nice_message = f"✅ Recovered ₹{request.amount:,.2f}"
        elif status == "escalated":
            nice_message = "⚠️ Escalated to manual review (policy/fraud gate)"
        elif status == "abandoned":
            nice_message = "⛔ Abandoned — recovery not attempted"
        else:
            nice_message = f"⏳ In recovery pipeline ({intervention.get('type', 'n/a')})"

    return SimulatePaymentResponse(
        transaction_id=result["transaction_id"],
        razorpay_payment_id=razorpay_payment_id,
        status=status,
        diagnosis=result.get("diagnosis", {}),
        recommended_intervention=(
            intervention.get("type")
            or result.get("recommended_intervention")
            or "none"
        ),
        message=nice_message,
    )


@router.post("/batch")
async def simulate_batch(
    count: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Simulate a bounded batch of failed payments for bulk testing."""
    results = []
    failure_types = list(FAILURE_TEMPLATES.keys())

    for i in range(count):
        failure_reason = random.choice(failure_types)
        amount = round(random.uniform(100, 50000), 2)

        request = SimulatePaymentRequest(
            amount=amount,
            payment_method=random.choice(["card", "upi", "netbanking"]),
            failure_reason=failure_reason,
            bank=random.choice(["HDFC", "ICICI", "SBI", "Axis", "Kotak"]),
        )

        template = FAILURE_TEMPLATES[failure_reason]
        razorpay_payment_id = f"pay_batch_{uuid.uuid4().hex[:14]}"
        payment_data = {
            "razorpay_payment_id": razorpay_payment_id,
            "amount": request.amount,
            "currency": "INR",
            "payment_method": request.payment_method,
            "bank": request.bank,
            "failure_category": failure_reason,
            "customer_email": f"batch_test_{i}@example.com",
            "customer_phone": f"98{random.randint(10000000, 99999999)}",
            **template,
        }

        result = await recovery_engine.process_failed_payment(
            db=db, payment_data=payment_data
        )
        results.append({
            "index": i,
            "payment_id": razorpay_payment_id,
            "amount": amount,
            "failure": failure_reason,
            "status": result["status"],
            "recovery_probability": result.get("recovery_probability"),
        })

    await db.commit()

    recovered = sum(1 for r in results if r["status"] == "recovered")
    total_amount = sum(r["amount"] for r in results)
    recovered_amount = sum(
        r["amount"] for r in results if r["status"] == "recovered"
    )

    return {
        "total_simulated": len(results),
        "recovered": recovered,
        "recovery_rate": f"{recovered / len(results) * 100:.1f}%",
        "total_amount": f"₹{total_amount:,.2f}",
        "recovered_amount": f"₹{recovered_amount:,.2f}",
        "results": results,
    }
