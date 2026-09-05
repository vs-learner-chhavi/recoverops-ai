"""
RecoverOps AI — Intervention Execution Engine
Handles the actual execution of each intervention type.
Separated from RecoveryEngine for modularity.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    FailedTransaction, Intervention, PaymentStatus,
    InterventionType, InterventionStatus,
)
from app.razorpay_client import razorpay_service
from app.audit_logger import AuditLogger
from app.config import get_settings

settings = get_settings()


class InterventionEngine:
    """
    Executes individual intervention types.
    Each method returns (success, result_data).
    """

    async def execute(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Route to the correct execution method based on intervention type.
        """
        itype = intervention.intervention_type

        if itype == InterventionType.SMART_RETRY:
            return await self._smart_retry(db, transaction, intervention)
        elif itype == InterventionType.PAYMENT_LINK:
            return await self._payment_link(db, transaction, intervention)
        elif itype == InterventionType.WHATSAPP_NUDGE:
            return await self._whatsapp_nudge(db, transaction, intervention)
        elif itype == InterventionType.EMAIL_REMINDER:
            return await self._email_reminder(db, transaction, intervention)
        elif itype == InterventionType.VOICE_CALL:
            return await self._voice_call(db, transaction, intervention)
        elif itype == InterventionType.MANUAL_ESCALATION:
            return await self._manual_escalation(db, transaction, intervention)
        else:
            return False, {"error": f"Unknown intervention type: {itype}"}

    async def _smart_retry(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a new Razorpay order for retry."""
        success, data = razorpay_service.create_order(
            amount_inr=tx.amount,
            receipt=f"retry_{tx.razorpay_payment_id}",
        )

        await AuditLogger.log_api_call(
            db, tx.id, "create_order", success, data
        )

        if success:
            intervention.status = InterventionStatus.COMPLETED
            intervention.intervention_cost = 0.50
            intervention.executed_at = datetime.now(timezone.utc)
            tx.retry_count += 1
        else:
            intervention.status = InterventionStatus.FAILED

        return success, data

    async def _payment_link(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Generate a Razorpay Payment Link."""
        expire_by = int(
            (datetime.now(timezone.utc) + timedelta(
                hours=settings.tier2_link_expiry_hours
            )).timestamp()
        )

        success, data = razorpay_service.create_payment_link(
            amount_inr=tx.amount,
            customer_email=tx.customer_email,
            customer_phone=tx.customer_phone,
            description=f"Complete your ₹{tx.amount:,.2f} payment",
            expire_by=expire_by,
            idempotency_key=intervention.idempotency_key,
        )

        await AuditLogger.log_api_call(
            db, tx.id, "create_payment_link", success, data
        )

        if success:
            intervention.razorpay_payment_link_id = data.get("payment_link_id")
            intervention.payment_link_url = data.get("short_url")
            intervention.status = InterventionStatus.COMPLETED
            intervention.intervention_cost = 2.00
            intervention.channel = "sms_email"
            intervention.executed_at = datetime.now(timezone.utc)
        else:
            intervention.status = InterventionStatus.FAILED

        return success, data

    async def _whatsapp_nudge(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Send a WhatsApp nudge (simulated in test mode)."""
        message = self._build_nudge_message(tx, "whatsapp")

        intervention.message_content = message
        intervention.channel = "whatsapp"
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 1.50
        intervention.executed_at = datetime.now(timezone.utc)
        tx.contact_count += 1

        await AuditLogger.log(
            db, "nudge_sent", "system", "send_whatsapp_nudge",
            f"WhatsApp nudge sent for ₹{tx.amount:,.2f}",
            tx.id, metadata={"message_preview": message[:80]},
        )

        return True, {"channel": "whatsapp", "message": message}

    async def _email_reminder(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Send an email reminder (simulated)."""
        message = self._build_nudge_message(tx, "email")

        intervention.message_content = message
        intervention.channel = "email"
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 0.25
        intervention.executed_at = datetime.now(timezone.utc)
        tx.contact_count += 1

        await AuditLogger.log(
            db, "nudge_sent", "system", "send_email_reminder",
            f"Email reminder sent for ₹{tx.amount:,.2f}",
            tx.id, metadata={"message_preview": message[:80]},
        )

        return True, {"channel": "email", "message": message}

    async def _voice_call(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Initiate a voice call (simulated)."""
        intervention.channel = "voice"
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 3.00
        intervention.executed_at = datetime.now(timezone.utc)
        tx.contact_count += 1

        await AuditLogger.log(
            db, "voice_call_initiated", "system", "initiate_voice_call",
            f"Voice call initiated for ₹{tx.amount:,.2f}",
            tx.id,
        )

        return True, {"channel": "voice", "status": "initiated"}

    async def _manual_escalation(
        self,
        db: AsyncSession,
        tx: FailedTransaction,
        intervention: Intervention,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Escalate to manual review queue."""
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 0.0
        intervention.executed_at = datetime.now(timezone.utc)
        tx.status = PaymentStatus.ESCALATED

        await AuditLogger.log(
            db, "manual_escalation", "system", "escalate_to_manual",
            "Escalated to merchant review queue",
            tx.id, severity="warning",
        )

        return True, {"status": "escalated"}

    def _build_nudge_message(
        self, tx: FailedTransaction, channel: str
    ) -> str:
        """Build a localized recovery message."""
        amt = tx.amount
        cat = tx.failure_category.value if tx.failure_category else "unknown"

        messages = {
            "insufficient_funds": (
                f"Hi! Your ₹{amt:,.2f} payment couldn't complete due to "
                f"insufficient funds. Your order is reserved for 24 hours. "
                f"Complete payment now! 🙏"
            ),
            "card_expired": (
                f"Hello! Your card may need updating. Use a different "
                f"payment method to complete your ₹{amt:,.2f} purchase. "
                f"We've saved your cart! 💳"
            ),
            "authentication_failed": (
                f"Hi! Your ₹{amt:,.2f} payment needs a retry. Keep your "
                f"OTP ready and click below to complete securely. 🔐"
            ),
            "bank_technical": (
                f"Hi! A temporary bank issue affected your ₹{amt:,.2f} "
                f"payment. It's resolved now — click below to retry! ⚡"
            ),
        }

        return messages.get(
            cat,
            f"Hello! Your ₹{amt:,.2f} payment is pending. "
            f"Complete it now to confirm your order! 🛒",
        )


# Singleton
intervention_engine = InterventionEngine()