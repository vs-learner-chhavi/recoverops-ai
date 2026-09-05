"""
RecoverOps AI — Core Recovery Orchestration Engine
Coordinates the entire recovery pipeline:
    Ingest → Diagnose → Decide → Gate → Act → Verify → Log
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
# Keep the orchestration engine importable when the optional SQLAlchemy async
# extension is not available in the editor's selected environment.
AsyncSession = Any
from sqlalchemy import select  # pyright: ignore[reportMissingImports]

from app.models import (
    FailedTransaction, Intervention, PaymentStatus,
    InterventionType, InterventionStatus, FailureCategory,
)
from app.audit_logger import AuditLogger
from app.policy_gate import policy_gate
from app.razorpay_client import razorpay_service
from app.config import get_settings
from ml.predictor import predictor
from ml.explainer import xai_explainer

settings = get_settings()


class RecoveryEngine:
    """
    The central orchestrator that processes failed payments
    through the complete AI recovery pipeline.
    """

    async def process_failed_payment(
        self,
        db: AsyncSession,
        payment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Full pipeline for a single failed payment.
        Returns a summary of actions taken.
        """
        # ── Step 1: Ingest & Create Transaction Record ──
        transaction = await self._ingest_transaction(db, payment_data)

        await AuditLogger.log(
            db=db,
            event_type="payment_ingested",
            event_category="system",
            action="ingest_failed_payment",
            description=f"Failed payment ₹{transaction.amount:,.2f} ingested",
            transaction_id=transaction.id,
            metadata={"razorpay_payment_id": transaction.razorpay_payment_id},
        )

        # ── Step 2: AI Diagnosis ──
        diagnosis = await self._diagnose(db, transaction, payment_data)

        # ── Step 3: ML Prediction ──
        prob, should_recover, recommended = predictor.predict({
            "amount": transaction.amount,
            "payment_method": transaction.payment_method or "card",
            "bank": transaction.bank or "Unknown",
            "failure_category": transaction.failure_category.value if transaction.failure_category else "unknown",
            "hour": transaction.failed_at.hour if transaction.failed_at else 12,
            "day_of_week": transaction.failed_at.weekday() if transaction.failed_at else 0,
        })

        # Update transaction with ML results
        transaction.recovery_probability = prob
        transaction.recommended_intervention = InterventionType(recommended)
        transaction.xai_explanation = diagnosis

        await AuditLogger.log_ai_decision(
            db=db,
            transaction_id=transaction.id,
            action=f"predict_recovery",
            confidence=prob,
            reasoning=f"Recovery probability: {prob:.2%}. Recommended: {recommended}",
            features=diagnosis.get("all_contributions", [])[:5],
        )

        # ── Step 4: Should we attempt recovery? ──
        if not should_recover:
            transaction.status = PaymentStatus.ABANDONED
            await db.commit()
            return {
                "transaction_id": transaction.id,
                "status": "abandoned",
                "reason": "Recovery probability too low or fraud suspected",
                "recovery_probability": prob,
                "diagnosis": diagnosis,
            }

        # ── Step 5: Policy Gate ──
        transaction.status = PaymentStatus.AT_RISK
        approved, reason, checks = await policy_gate.evaluate(
            db=db,
            transaction=transaction,
            proposed_intervention=recommended,
            confidence_score=prob,
        )

        if not approved:
            # Create blocked intervention record
            intervention = Intervention(
                transaction_id=transaction.id,
                idempotency_key=f"idem_{uuid.uuid4().hex[:16]}",
                intervention_type=InterventionType(recommended),
                tier=self._get_tier(recommended),
                status=InterventionStatus.BLOCKED_BY_POLICY,
                confidence_score=prob,
                reasoning=reason,
                policy_approved=False,
                policy_rejection_reason=reason,
            )
            db.add(intervention)

            # Escalate to manual
            transaction.status = PaymentStatus.ESCALATED
            await db.commit()

            return {
                "transaction_id": transaction.id,
                "status": "escalated",
                "reason": reason,
                "policy_checks": checks,
                "recovery_probability": prob,
                "diagnosis": diagnosis,
            }

        # ── Step 6: Execute Intervention ──
        transaction.status = PaymentStatus.RECOVERING
        result = await self._execute_intervention(
            db=db,
            transaction=transaction,
            intervention_type=recommended,
            confidence=prob,
            reasoning=diagnosis.get("summary", ""),
        )

        await db.commit()

        intervention_result = result or {}
        final_status = transaction.status.value if transaction.status else "unknown"
        recovered = bool(intervention_result.get("recovered"))

        return {
            "transaction_id": transaction.id,
            "status": final_status,
            "recovery_probability": prob,
            "intervention": intervention_result,
            "diagnosis": diagnosis,
            "policy_checks": checks,
            "message": intervention_result.get("message")
                or intervention_result.get("ui_message")
                or f"Pipeline finished with status: {final_status}",
            "recovered": recovered,
            "recommended_intervention": recommended,
        }
    async def _ingest_transaction(
        self,
        db: AsyncSession,
        data: Dict[str, Any],
    ) -> FailedTransaction:
        """Create or update a FailedTransaction record."""
        razorpay_id = data.get("razorpay_payment_id", f"pay_sim_{uuid.uuid4().hex[:14]}")

        # Check if already exists
        existing = await db.execute(
            select(FailedTransaction).where(
                FailedTransaction.razorpay_payment_id == razorpay_id
            )
        )
        transaction = existing.scalar_one_or_none()

        if transaction:
            return transaction

        # Map failure category
        failure_cat = data.get("failure_category", "unknown")
        try:
            category = FailureCategory(failure_cat)
        except ValueError:
            category = FailureCategory.UNKNOWN

        transaction = FailedTransaction(
            razorpay_payment_id=razorpay_id,
            razorpay_order_id=data.get("razorpay_order_id"),
            amount=float(data.get("amount", 0)),
            currency=data.get("currency", "INR"),
            payment_method=data.get("payment_method"),
            bank=data.get("bank"),
            card_network=data.get("card_network"),
            card_type=data.get("card_type"),
            customer_email=data.get("customer_email"),
            customer_phone=data.get("customer_phone"),
            customer_id=data.get("customer_id"),
            error_code=data.get("error_code"),
            error_description=data.get("error_description"),
            error_source=data.get("error_source"),
            error_step=data.get("error_step"),
            error_reason=data.get("error_reason"),
            failure_category=category,
            status=PaymentStatus.FAILED,
            failed_at=datetime.now(timezone.utc),
        )
        db.add(transaction)
        await db.flush()
        return transaction

    async def _diagnose(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run XAI diagnostic on the transaction."""
        explanation = xai_explainer.explain({
            "amount": transaction.amount,
            "payment_method": transaction.payment_method or "card",
            "bank": transaction.bank or "Unknown",
            "failure_category": (
                transaction.failure_category.value
                if transaction.failure_category
                else "unknown"
            ),
            "hour": transaction.failed_at.hour if transaction.failed_at else 12,
            "day_of_week": (
                transaction.failed_at.weekday()
                if transaction.failed_at
                else 0
            ),
        })
        return explanation

    async def _execute_intervention(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention_type: str,
        confidence: float,
        reasoning: str,
    ) -> Dict[str, Any]:
        """Execute the approved intervention."""
        idempotency_key = f"idem_{transaction.id}_{intervention_type}_{uuid.uuid4().hex[:8]}"

        intervention = Intervention(
            transaction_id=transaction.id,
            idempotency_key=idempotency_key,
            intervention_type=InterventionType(intervention_type),
            tier=self._get_tier(intervention_type),
            status=InterventionStatus.EXECUTING,
            confidence_score=confidence,
            reasoning=reasoning,
            policy_approved=True,
            model_version="xgb_v1.0",
        )
        db.add(intervention)
        await db.flush()

        # Execute based on type
        result = {}

        if intervention_type == "smart_retry":
            result = await self._execute_smart_retry(
                db, transaction, intervention
            )
        elif intervention_type == "payment_link":
            result = await self._execute_payment_link(
                db, transaction, intervention
            )
        elif intervention_type in ("whatsapp_nudge", "email_reminder"):
            result = await self._execute_nudge(
                db, transaction, intervention, intervention_type
            )
        elif intervention_type == "manual_escalation":
            result = await self._execute_escalation(
                db, transaction, intervention
            )

        return result

    async def _execute_smart_retry(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention: Intervention,
    ) -> Dict[str, Any]:
        """Tier 1: Smart Retry."""
        success, order_data = razorpay_service.create_order(
            amount_inr=transaction.amount,
            receipt=f"retry_{transaction.razorpay_payment_id}",
        )

        await AuditLogger.log_api_call(
            db=db,
            transaction_id=transaction.id,
            api_name="create_order",
            success=success,
            response_data=order_data,
        )

        intervention.executed_at = datetime.now(timezone.utc)
        intervention.intervention_cost = 0.50
        transaction.retry_count = (transaction.retry_count or 0) + 1

        # Even if Razorpay test API fails (bad keys etc.), still simulate outcome for demo
        import random
        prob = float(transaction.recovery_probability or 0.5)
        recovered = random.random() < min(0.92, max(0.35, prob))

        if recovered:
            intervention.status = InterventionStatus.COMPLETED
            intervention.resulted_in_recovery = True
            intervention.recovered_amount = transaction.amount
            transaction.status = PaymentStatus.RECOVERED
            transaction.recovered_at = datetime.now(timezone.utc)
            await AuditLogger.log_recovery(
                db=db,
                transaction_id=transaction.id,
                amount_recovered=transaction.amount,
                intervention_type="smart_retry",
            )
        else:
            intervention.status = InterventionStatus.COMPLETED
            intervention.resulted_in_recovery = False
            transaction.status = PaymentStatus.RECOVERING  # still in pipeline for next tier

        return {
            "type": "smart_retry",
            "success": True,
            "api_success": success,
            "order_data": order_data,
            "recovered": recovered,
            "message": (
                f"✅ Payment of ₹{transaction.amount:,.2f} recovered via Smart Retry"
                if recovered
                else f"⏳ Smart Retry scheduled. Waiting for bank confirmation."
            ),
        }

    async def _execute_payment_link(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention: Intervention,
    ) -> Dict[str, Any]:
        """Tier 2: Payment Link."""
        expire_by = int(
            (datetime.now(timezone.utc) + timedelta(hours=settings.tier2_link_expiry_hours)).timestamp()
        )

        success, link_data = razorpay_service.create_payment_link(
            amount_inr=transaction.amount,
            customer_email=transaction.customer_email,
            customer_phone=transaction.customer_phone,
            description=f"Complete your payment of ₹{transaction.amount:,.2f}",
            expire_by=expire_by,
            idempotency_key=intervention.idempotency_key,
        )

        await AuditLogger.log_api_call(
            db=db,
            transaction_id=transaction.id,
            api_name="create_payment_link",
            success=success,
            response_data=link_data,
        )

        intervention.executed_at = datetime.now(timezone.utc)
        intervention.intervention_cost = 2.00
        intervention.channel = "sms_email"

        if success:
            intervention.razorpay_payment_link_id = link_data.get("payment_link_id")
            intervention.payment_link_url = link_data.get("short_url")

        import random
        prob = float(transaction.recovery_probability or 0.4)
        recovered = random.random() < min(0.75, max(0.25, prob * 0.85))

        if recovered:
            intervention.status = InterventionStatus.COMPLETED
            intervention.resulted_in_recovery = True
            intervention.recovered_amount = transaction.amount
            transaction.status = PaymentStatus.RECOVERED
            transaction.recovered_at = datetime.now(timezone.utc)
            await AuditLogger.log_recovery(
                db=db,
                transaction_id=transaction.id,
                amount_recovered=transaction.amount,
                intervention_type="payment_link",
            )
            msg = f"✅ Customer paid ₹{transaction.amount:,.2f} via Payment Link"
        else:
            intervention.status = InterventionStatus.COMPLETED
            intervention.resulted_in_recovery = False
            transaction.status = PaymentStatus.RECOVERING
            msg = f"🔗 Payment Link sent. Awaiting customer action."
            if link_data.get("short_url"):
                msg += f" Link: {link_data.get('short_url')}"

        return {
            "type": "payment_link",
            "success": True,
            "api_success": success,
            "link_data": link_data,
            "recovered": recovered,
            "message": msg,
        }

    async def _execute_nudge(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention: Intervention,
        nudge_type: str,
    ) -> Dict[str, Any]:
        """Tier 3: WhatsApp / Email nudge."""
        message = self._generate_nudge_message(transaction, nudge_type)

        intervention.message_content = message
        intervention.channel = "whatsapp" if nudge_type == "whatsapp_nudge" else "email"
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 1.50 if nudge_type == "whatsapp_nudge" else 0.25
        intervention.executed_at = datetime.now(timezone.utc)
        transaction.contact_count = (transaction.contact_count or 0) + 1

        await AuditLogger.log(
            db=db,
            event_type="nudge_sent",
            event_category="system",
            action=f"send_{nudge_type}",
            description=f"Nudge sent via {intervention.channel}",
            transaction_id=transaction.id,
            metadata={"message_preview": message[:100]},
        )

        import random
        prob = float(transaction.recovery_probability or 0.35)
        recovered = random.random() < min(0.55, max(0.15, prob * 0.6))

        if recovered:
            intervention.resulted_in_recovery = True
            intervention.recovered_amount = transaction.amount
            transaction.status = PaymentStatus.RECOVERED
            transaction.recovered_at = datetime.now(timezone.utc)
            await AuditLogger.log_recovery(
                db=db,
                transaction_id=transaction.id,
                amount_recovered=transaction.amount,
                intervention_type=nudge_type,
            )
            msg = f"✅ Customer returned and paid ₹{transaction.amount:,.2f} after {nudge_type.replace('_', ' ')}"
        else:
            intervention.resulted_in_recovery = False
            transaction.status = PaymentStatus.RECOVERING
            msg = f"📨 {nudge_type.replace('_', ' ').title()} sent. Monitoring response."

        return {
            "type": nudge_type,
            "message": message,
            "channel": intervention.channel,
            "recovered": recovered,
            "ui_message": msg,
        }

    
    async def _execute_escalation(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        intervention: Intervention,
    ) -> Dict[str, Any]:
        """Manual escalation — no automated action."""
        intervention.status = InterventionStatus.COMPLETED
        intervention.intervention_cost = 0.0
        transaction.status = PaymentStatus.ESCALATED

        await AuditLogger.log(
            db=db,
            event_type="manual_escalation",
            event_category="system",
            action="escalate_to_manual",
            description="Transaction escalated to merchant for manual review",
            transaction_id=transaction.id,
            severity="warning",
        )

        return {
            "type": "manual_escalation",
            "message": "Escalated to merchant review queue",
            "recovered": False,
        }

    async def mark_recovered(
        self, db: AsyncSession, razorpay_payment_id: str
    ) -> Dict[str, Any]:
        """Mark a transaction as recovered when payment.captured fires."""
        from app.models import FailedTransaction, PaymentStatus

        result = await db.execute(
            select(FailedTransaction).where(
                FailedTransaction.razorpay_payment_id == razorpay_payment_id
            )
        )
        tx = result.scalar_one_or_none()

        if tx and tx.status != PaymentStatus.RECOVERED:
            tx.status = PaymentStatus.RECOVERED
            tx.recovered_at = datetime.now(timezone.utc)
            await AuditLogger.log_recovery(
                db, tx.id, tx.amount, "smart_retry_capture"
            )
            return {"status": "recovered", "transaction_id": tx.id}

        return {"status": "no_action", "reason": "Transaction not found or already recovered"}

    async def mark_link_recovered(
        self, db: AsyncSession, payment_link_id: str
    ) -> Dict[str, Any]:
        """Mark transaction as recovered when payment_link.paid fires."""
        from app.models import Intervention, FailedTransaction, PaymentStatus

        result = await db.execute(
            select(Intervention).where(
                Intervention.razorpay_payment_link_id == payment_link_id
            )
        )
        intervention = result.scalar_one_or_none()

        if intervention:
            intervention.resulted_in_recovery = True
            tx_result = await db.execute(
                select(FailedTransaction).where(
                    FailedTransaction.id == intervention.transaction_id
                )
            )
            tx = tx_result.scalar_one_or_none()
            if tx:
                intervention.recovered_amount = tx.amount
                tx.status = PaymentStatus.RECOVERED
                tx.recovered_at = datetime.now(timezone.utc)
                await AuditLogger.log_recovery(
                    db, tx.id, tx.amount, "payment_link"
                )
                return {"status": "recovered", "transaction_id": tx.id}

        return {"status": "no_action"}

    async def escalate_expired_link(
        self, db: AsyncSession, payment_link_id: str
    ) -> Dict[str, Any]:
        """Escalate when a recovery payment link expires unpaid."""
        from app.models import Intervention, FailedTransaction, PaymentStatus

        result = await db.execute(
            select(Intervention).where(
                Intervention.razorpay_payment_link_id == payment_link_id
            )
        )
        intervention = result.scalar_one_or_none()

        if intervention and not intervention.resulted_in_recovery:
            intervention.status = InterventionStatus.FAILED
            tx_result = await db.execute(
                select(FailedTransaction).where(
                    FailedTransaction.id == intervention.transaction_id
                )
            )
            tx = tx_result.scalar_one_or_none()
            if tx and tx.status == PaymentStatus.RECOVERING:
                tx.status = PaymentStatus.ESCALATED
                await AuditLogger.log(
                    db, "link_expired", "system", "escalate_expired_link",
                    f"Payment link {payment_link_id} expired without payment",
                    tx.id, severity="warning",
                )
                return {"status": "escalated", "transaction_id": tx.id}

        return {"status": "no_action"}

    async def handle_cancelled_link(
        self, db: AsyncSession, payment_link_id: str
    ) -> Dict[str, Any]:
        """Handle customer cancelling a recovery payment link."""
        from app.models import Intervention

        result = await db.execute(
            select(Intervention).where(
                Intervention.razorpay_payment_link_id == payment_link_id
            )
        )
        intervention = result.scalar_one_or_none()

        if intervention and not intervention.resulted_in_recovery:
            intervention.status = InterventionStatus.FAILED
            await AuditLogger.log(
                db, "link_cancelled", "system", "handle_cancelled_link",
                f"Customer cancelled payment link {payment_link_id}",
                intervention.transaction_id, severity="info",
            )
            return {"status": "cancelled", "intervention_id": intervention.id}

        return {"status": "no_action"}

    def _generate_nudge_message(
        self,
        transaction: FailedTransaction,
        nudge_type: str,
    ) -> str:
        """Generate a localized, personalized recovery message."""
        amount = transaction.amount
        category = (
            transaction.failure_category.value
            if transaction.failure_category
            else "unknown"
        )

        if category == "insufficient_funds":
            return (
                f"Hi! Your payment of ₹{amount:,.2f} could not be completed "
                f"due to insufficient funds. We've kept your order reserved. "
                f"You can complete the payment anytime in the next 24 hours. 🙏"
            )
        elif category == "card_expired":
            return (
                f"Hello! We noticed your card may need updating. "
                f"Please use a different payment method to complete your "
                f"₹{amount:,.2f} purchase. We've saved your cart! 💳"
            )
        elif category == "authentication_failed":
            return (
                f"Hi! Your payment of ₹{amount:,.2f} needs to be retried. "
                f"Please ensure you have your OTP ready and try again. "
                f"Click the link below to complete securely. 🔐"
            )
        elif category in ("bank_technical", "network_error", "gateway_error"):
            return (
                f"Hi! There was a temporary technical issue with your "
                f"₹{amount:,.2f} payment. The issue has been resolved. "
                f"Click below to complete your purchase instantly! ⚡"
            )
        else:
            return (
                f"Hello! Your payment of ₹{amount:,.2f} is pending. "
                f"Complete it now to confirm your order. "
                f"We've kept everything ready for you! 🛒"
            )

    def _get_tier(self, intervention_type: str) -> int:
        tier_map = {
            "smart_retry": 1,
            "payment_link": 2,
            "whatsapp_nudge": 3,
            "email_reminder": 3,
            "voice_call": 3,
            "manual_escalation": 0,
        }
        return tier_map.get(intervention_type, 0)


# Singleton
recovery_engine = RecoveryEngine()