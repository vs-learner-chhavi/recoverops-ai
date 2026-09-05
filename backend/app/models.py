"""
RecoverOps AI — SQLAlchemy ORM Models
Complete data model for transactions, interventions, audit logs, and analytics.
"""

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Boolean,
    Text, Enum, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
import uuid

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class PaymentStatus(str, enum.Enum):
    FAILED = "failed"
    AT_RISK = "at_risk"
    RECOVERING = "recovering"
    RECOVERED = "recovered"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"


class InterventionType(str, enum.Enum):
    SMART_RETRY = "smart_retry"
    PAYMENT_LINK = "payment_link"
    WHATSAPP_NUDGE = "whatsapp_nudge"
    EMAIL_REMINDER = "email_reminder"
    VOICE_CALL = "voice_call"
    MANUAL_ESCALATION = "manual_escalation"


class InterventionStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    SKIPPED = "skipped"


class FailureCategory(str, enum.Enum):
    BANK_TECHNICAL = "bank_technical"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_EXPIRED = "card_expired"
    AUTHENTICATION_FAILED = "authentication_failed"
    NETWORK_ERROR = "network_error"
    FRAUD_SUSPECTED = "fraud_suspected"
    USER_CANCELLED = "user_cancelled"
    GATEWAY_ERROR = "gateway_error"
    MANDATE_FAILED = "mandate_failed"
    UNKNOWN = "unknown"


class FailedTransaction(Base):
    """Represents a failed payment event ingested from Razorpay webhooks."""
    __tablename__ = "failed_transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    razorpay_payment_id = Column(String, unique=True, nullable=False, index=True)
    razorpay_order_id = Column(String, nullable=True)
    merchant_id = Column(String, nullable=False, default="merchant_test_001")

    # Payment Details
    amount = Column(Float, nullable=False)  # in INR
    currency = Column(String, default="INR")
    payment_method = Column(String, nullable=True)  # card, upi, netbanking, wallet
    bank = Column(String, nullable=True)
    card_network = Column(String, nullable=True)  # visa, mastercard, rupay
    card_type = Column(String, nullable=True)  # credit, debit

    # Customer Info
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_id = Column(String, nullable=True)

    # Failure Details
    error_code = Column(String, nullable=True)
    error_description = Column(Text, nullable=True)
    error_source = Column(String, nullable=True)
    error_step = Column(String, nullable=True)
    error_reason = Column(String, nullable=True)

    # AI Diagnostics
    failure_category = Column(
        Enum(FailureCategory), default=FailureCategory.UNKNOWN
    )
    recovery_probability = Column(Float, nullable=True)
    churn_risk_score = Column(Float, nullable=True)
    xai_explanation = Column(JSON, nullable=True)
    recommended_intervention = Column(
        Enum(InterventionType), nullable=True
    )

    # Status Tracking
    status = Column(
        Enum(PaymentStatus), default=PaymentStatus.FAILED
    )
    retry_count = Column(Integer, default=0)
    contact_count = Column(Integer, default=0)

    # Timestamps
    failed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    recovered_at = Column(DateTime, nullable=True)

    # Relationships
    interventions = relationship("Intervention", back_populates="transaction")
    audit_logs = relationship("AuditLog", back_populates="transaction")

    __table_args__ = (
        Index("ix_failed_transactions_status", "status"),
        Index("ix_failed_transactions_merchant", "merchant_id"),
        Index("ix_failed_transactions_failed_at", "failed_at"),
    )


class Intervention(Base):
    """Represents an AI-driven recovery action taken on a failed payment."""
    __tablename__ = "interventions"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(
        String, ForeignKey("failed_transactions.id"), nullable=False
    )
    idempotency_key = Column(String, unique=True, nullable=False)

    # Intervention Details
    intervention_type = Column(Enum(InterventionType), nullable=False)
    tier = Column(Integer, nullable=False)  # 1, 2, or 3
    status = Column(
        Enum(InterventionStatus), default=InterventionStatus.PENDING
    )

    # AI Decision Context
    confidence_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    model_version = Column(String, nullable=True)

    # Execution Details
    razorpay_payment_link_id = Column(String, nullable=True)
    payment_link_url = Column(String, nullable=True)
    message_content = Column(Text, nullable=True)
    channel = Column(String, nullable=True)  # sms, whatsapp, email

    # Cost Tracking
    intervention_cost = Column(Float, default=0.0)
    cost_percentage = Column(Float, nullable=True)

    # Policy Checks
    policy_approved = Column(Boolean, default=False)
    policy_rejection_reason = Column(String, nullable=True)

    # Results
    resulted_in_recovery = Column(Boolean, default=False)
    recovered_amount = Column(Float, default=0.0)

    # Timestamps
    scheduled_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("FailedTransaction", back_populates="interventions")

    __table_args__ = (
        Index("ix_interventions_status", "status"),
        Index("ix_interventions_type", "intervention_type"),
    )


class AuditLog(Base):
    """Immutable audit trail for every AI decision and system action."""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(
        String, ForeignKey("failed_transactions.id"), nullable=True
    )
    intervention_id = Column(String, nullable=True)

    # Event Details
    event_type = Column(String, nullable=False)
    event_category = Column(String, nullable=False)  # system, ai_decision, policy, api, error
    severity = Column(String, default="info")  # info, warning, error, critical

    # Context
    actor = Column(String, default="system")  # system, ai_engine, policy_gate, user
    action = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_metadata = Column(JSON, nullable=True)  # Renamed from metadata

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction = relationship("FailedTransaction", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_event_type", "event_type"),
        Index("ix_audit_logs_created_at", "created_at"),
    )


class SystemMetrics(Base):
    """Aggregated system performance metrics (updated periodically)."""
    __tablename__ = "system_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    metric_metadata = Column(JSON, nullable=True)  # Renamed from metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))