"""
RecoverOps AI — Immutable Audit Logger
Every AI decision, policy check, API call, and system event is recorded.
This is a core Razorpay requirement: explainability and accountability.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


class AuditLogger:
    """
    Creates immutable audit trail entries.
    Categories: system, ai_decision, policy, api_call, error, recovery
    """

    @staticmethod
    async def log(
        db: AsyncSession,
        event_type: str,
        event_category: str,
        action: str,
        description: Optional[str] = None,
        transaction_id: Optional[str] = None,
        intervention_id: Optional[str] = None,
        severity: str = "info",
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        entry = AuditLog(
            transaction_id=transaction_id,
            intervention_id=intervention_id,
            event_type=event_type,
            event_category=event_category,
            severity=severity,
            actor=actor,
            action=action,
            description=description,
            event_metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def log_ai_decision(
        db: AsyncSession,
        transaction_id: str,
        action: str,
        confidence: float,
        reasoning: str,
        features: Optional[Dict] = None,
    ):
        return await AuditLogger.log(
            db=db,
            event_type="ai_decision",
            event_category="ai_decision",
            action=action,
            description=reasoning,
            transaction_id=transaction_id,
            actor="ai_engine",
            metadata={
                "confidence": confidence,
                "features": features or {},
            },
        )

    @staticmethod
    async def log_policy_check(
        db: AsyncSession,
        transaction_id: str,
        approved: bool,
        reason: str,
        checks_performed: Dict,
    ):
        return await AuditLogger.log(
            db=db,
            event_type="policy_check",
            event_category="policy",
            action="policy_gate_evaluation",
            description=reason,
            transaction_id=transaction_id,
            severity="info" if approved else "warning",
            actor="policy_gate",
            metadata={
                "approved": approved,
                "checks": checks_performed,
            },
        )

    @staticmethod
    async def log_api_call(
        db: AsyncSession,
        transaction_id: str,
        api_name: str,
        success: bool,
        response_data: Optional[Dict] = None,
    ):
        return await AuditLogger.log(
            db=db,
            event_type="api_call",
            event_category="api_call",
            action=f"razorpay_{api_name}",
            description=f"API call to {api_name}: {'success' if success else 'failed'}",
            transaction_id=transaction_id,
            severity="info" if success else "error",
            actor="system",
            metadata={"success": success, "response": response_data or {}},
        )

    @staticmethod
    async def log_recovery(
        db: AsyncSession,
        transaction_id: str,
        amount_recovered: float,
        intervention_type: str,
    ):
        return await AuditLogger.log(
            db=db,
            event_type="recovery_success",
            event_category="recovery",
            action="payment_recovered",
            description=f"₹{amount_recovered:,.2f} recovered via {intervention_type}",
            transaction_id=transaction_id,
            actor="system",
            metadata={
                "amount_recovered": amount_recovered,
                "intervention_type": intervention_type,
            },
        )

    @staticmethod
    async def log_error(
        db: AsyncSession,
        action: str,
        error_message: str,
        transaction_id: Optional[str] = None,
    ):
        return await AuditLogger.log(
            db=db,
            event_type="system_error",
            event_category="error",
            action=action,
            description=error_message,
            transaction_id=transaction_id,
            severity="error",
            actor="system",
        )