"""
RecoverOps AI — Deterministic Policy Gate
Enforces hard business rules BEFORE any AI-driven action is executed.
This is the core safety mechanism that Razorpay explicitly requires.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import get_settings
from app.models import (
    FailedTransaction, Intervention, InterventionType,
    InterventionStatus,
)
from app.audit_logger import AuditLogger

settings = get_settings()


class PolicyGate:
    """
    Validates every proposed intervention against hard safety policies.
    Returns (approved: bool, reason: str, checks: dict).
    """

    async def evaluate(
        self,
        db: AsyncSession,
        transaction: FailedTransaction,
        proposed_intervention: str,
        confidence_score: float,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run all policy checks. ALL must pass for approval.
        """
        checks = {}

        # ── Check 1: Confidence Threshold ──
        checks["confidence_check"] = {
            "threshold": settings.min_confidence_threshold,
            "actual": confidence_score,
            "passed": confidence_score >= settings.min_confidence_threshold,
        }

        # ── Check 2: Retry Count Limit ──
        retry_count = await self._get_retry_count(db, transaction.id)
        checks["retry_limit_check"] = {
            "max_retries": settings.max_retries_per_payment,
            "current_retries": retry_count,
            "passed": retry_count < settings.max_retries_per_payment,
        }

        # ── Check 3: Contact Frequency Limit ──
        contact_count = await self._get_contact_count(db, transaction.id)
        checks["contact_limit_check"] = {
            "max_contacts": settings.max_contact_attempts,
            "current_contacts": contact_count,
            "passed": contact_count < settings.max_contact_attempts,
        }

        # ── Check 4: DND Hours (9 PM – 9 AM) ──
        current_hour = datetime.now(timezone.utc).hour
        # Adjust for IST (+5:30)
        ist_hour = (current_hour + 5) % 24
        is_dnd = ist_hour >= settings.dnd_start_hour or ist_hour < settings.dnd_end_hour
        is_contact_intervention = proposed_intervention in (
            "whatsapp_nudge", "email_reminder", "voice_call"
        )
        checks["dnd_check"] = {
            "ist_hour": ist_hour,
            "dnd_start": settings.dnd_start_hour,
            "dnd_end": settings.dnd_end_hour,
            "is_dnd": is_dnd,
            "is_contact": is_contact_intervention,
            "passed": not (is_dnd and is_contact_intervention),
        }

        # ── Check 5: Cost Cap ──
        intervention_cost = self._estimate_cost(proposed_intervention)
        cost_percentage = (
            (intervention_cost / transaction.amount * 100)
            if transaction.amount > 0
            else 100
        )
        checks["cost_cap_check"] = {
            "intervention_cost": intervention_cost,
            "transaction_amount": transaction.amount,
            "cost_percentage": round(cost_percentage, 2),
            "max_percentage": settings.cost_cap_percentage,
            "passed": cost_percentage <= settings.cost_cap_percentage,
        }

        # ── Check 6: Fraud Block ──
        is_fraud = transaction.failure_category and \
            transaction.failure_category.value == "fraud_suspected"
        is_action = proposed_intervention not in ("manual_escalation",)
        checks["fraud_block_check"] = {
            "is_fraud": is_fraud,
            "is_automated_action": is_action,
            "passed": not (is_fraud and is_action),
        }

        # ── Check 7: Duplicate Prevention (Idempotency) ──
        has_active = await self._has_active_intervention(
            db, transaction.id, proposed_intervention
        )
        checks["duplicate_check"] = {
            "has_active_intervention": has_active,
            "passed": not has_active,
        }

        # ── Aggregate Result ──
        all_passed = all(check["passed"] for check in checks.values())
        failed_checks = [
            name for name, check in checks.items() if not check["passed"]
        ]
        reason = (
            "All policy checks passed"
            if all_passed
            else f"Failed checks: {', '.join(failed_checks)}"
        )

        # Log the policy evaluation
        await AuditLogger.log_policy_check(
            db=db,
            transaction_id=transaction.id,
            approved=all_passed,
            reason=reason,
            checks_performed=checks,
        )

        return all_passed, reason, checks

    async def _get_retry_count(
        self, db: AsyncSession, transaction_id: str
    ) -> int:
        """Count retry-type interventions for this transaction."""
        result = await db.execute(
            select(func.count(Intervention.id)).where(
                Intervention.transaction_id == transaction_id,
                Intervention.intervention_type == InterventionType.SMART_RETRY,
                Intervention.status != InterventionStatus.BLOCKED_BY_POLICY,
            )
        )
        return result.scalar() or 0

    async def _get_contact_count(
        self, db: AsyncSession, transaction_id: str
    ) -> int:
        """Count contact-type interventions for this transaction."""
        contact_types = [
            InterventionType.WHATSAPP_NUDGE,
            InterventionType.EMAIL_REMINDER,
            InterventionType.VOICE_CALL,
        ]
        result = await db.execute(
            select(func.count(Intervention.id)).where(
                Intervention.transaction_id == transaction_id,
                Intervention.intervention_type.in_(contact_types),
                Intervention.status != InterventionStatus.BLOCKED_BY_POLICY,
            )
        )
        return result.scalar() or 0

    async def _has_active_intervention(
        self,
        db: AsyncSession,
        transaction_id: str,
        intervention_type: str,
    ) -> bool:
        """Check if there's already an active intervention of this type."""
        active_statuses = [
            InterventionStatus.PENDING,
            InterventionStatus.EXECUTING,
        ]
        type_enum = InterventionType(intervention_type)
        result = await db.execute(
            select(func.count(Intervention.id)).where(
                Intervention.transaction_id == transaction_id,
                Intervention.intervention_type == type_enum,
                Intervention.status.in_(active_statuses),
            )
        )
        count = result.scalar() or 0
        return count > 0

    def _estimate_cost(self, intervention_type: str) -> float:
        """
        Estimate cost of an intervention in INR.
        These are approximate real-world costs.
        """
        cost_map = {
            "smart_retry": 0.50,       # Minimal API cost
            "payment_link": 2.00,      # SMS + link generation
            "whatsapp_nudge": 1.50,    # WhatsApp Business API
            "email_reminder": 0.25,    # Email sending
            "voice_call": 3.00,        # Voice API
            "manual_escalation": 0.00, # No automated cost
        }
        return cost_map.get(intervention_type, 1.00)


# Singleton
policy_gate = PolicyGate()