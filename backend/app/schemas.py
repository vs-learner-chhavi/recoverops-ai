"""
RecoverOps AI — Pydantic Schemas
Request/Response validation models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ──────────────────────────── Enums ────────────────────────────

class PaymentStatusEnum(str, Enum):
    FAILED = "failed"
    AT_RISK = "at_risk"
    RECOVERING = "recovering"
    RECOVERED = "recovered"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"


class InterventionTypeEnum(str, Enum):
    SMART_RETRY = "smart_retry"
    PAYMENT_LINK = "payment_link"
    WHATSAPP_NUDGE = "whatsapp_nudge"
    EMAIL_REMINDER = "email_reminder"
    VOICE_CALL = "voice_call"
    MANUAL_ESCALATION = "manual_escalation"


# ──────────────────────── Webhook Schemas ──────────────────────

class RazorpayWebhookPayload(BaseModel):
    """Incoming Razorpay webhook event."""
    entity: str = "event"
    account_id: Optional[str] = None
    event: str
    contains: List[str] = []
    payload: Dict[str, Any]
    created_at: Optional[int] = None


# ──────────────────────── Transaction Schemas ─────────────────

class TransactionBase(BaseModel):
    razorpay_payment_id: str
    amount: float
    currency: str = "INR"
    payment_method: Optional[str] = None
    error_code: Optional[str] = None
    error_description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    razorpay_payment_id: str
    amount: float
    currency: str
    payment_method: Optional[str]
    status: str
    failure_category: Optional[str]
    recovery_probability: Optional[float]
    churn_risk_score: Optional[float]
    xai_explanation: Optional[Dict[str, Any]]
    recommended_intervention: Optional[str]
    retry_count: int
    failed_at: Optional[datetime]
    recovered_at: Optional[datetime]

    class Config:
        from_attributes = True


class TransactionDetail(TransactionResponse):
    customer_email: Optional[str]
    customer_phone: Optional[str]
    bank: Optional[str]
    card_network: Optional[str]
    error_source: Optional[str]
    error_step: Optional[str]
    interventions: List["InterventionResponse"] = []
    audit_logs: List["AuditLogResponse"] = []


# ──────────────────── Intervention Schemas ────────────────────

class InterventionResponse(BaseModel):
    id: str
    intervention_type: str
    tier: int
    status: str
    confidence_score: Optional[float]
    reasoning: Optional[str]
    payment_link_url: Optional[str]
    message_content: Optional[str]
    channel: Optional[str]
    policy_approved: bool
    policy_rejection_reason: Optional[str]
    resulted_in_recovery: bool
    recovered_amount: float
    intervention_cost: float
    created_at: Optional[datetime]
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ──────────────────── Audit Log Schemas ───────────────────────

class AuditLogResponse(BaseModel):
    id: str
    event_type: str
    event_category: str
    severity: str
    actor: str
    action: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="event_metadata")
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


# ──────────────────── Dashboard Schemas ───────────────────────

class DashboardMetrics(BaseModel):
    total_failed_revenue: float = Field(description="Total ₹ of failed payments")
    total_recovered_revenue: float = Field(description="Total ₹ successfully recovered")
    recovery_rate: float = Field(description="Recovery rate percentage")
    total_transactions: int = Field(description="Total failed transactions processed")
    active_recoveries: int = Field(description="Currently in recovery pipeline")
    interventions_executed: int = Field(description="Total interventions run")
    policy_blocks: int = Field(description="Interventions blocked by policy")
    avg_recovery_time_minutes: Optional[float] = Field(
        default=None, description="Average time to recover in minutes"
    )
    roi_multiplier: Optional[float] = Field(
        default=None, description="Revenue recovered / intervention cost"
    )


class RecoveryTrend(BaseModel):
    date: str
    failed_amount: float
    recovered_amount: float
    recovery_rate: float
    intervention_count: int


class FailureCategoryBreakdown(BaseModel):
    category: str
    count: int
    total_amount: float
    recovery_rate: float


class InterventionEffectiveness(BaseModel):
    intervention_type: str
    total_executed: int
    successful: int
    success_rate: float
    total_recovered: float
    avg_cost: float


# ──────────────────── Simulator Schemas ───────────────────────

class SimulatePaymentRequest(BaseModel):
    """Request to simulate a failed payment for demo purposes."""
    amount: float = Field(default=1500.0, ge=1.0, le=1000000.0)
    payment_method: str = Field(default="card")
    failure_reason: str = Field(default="bank_technical")
    customer_email: Optional[str] = "test@example.com"
    customer_phone: Optional[str] = "9876543210"
    bank: Optional[str] = "HDFC"
    card_network: Optional[str] = "visa"


class SimulatePaymentResponse(BaseModel):
    transaction_id: str
    razorpay_payment_id: str
    status: str
    diagnosis: Dict[str, Any]
    recommended_intervention: str
    message: str


# ──────────────────── Evaluation Schemas ──────────────────────

class EvaluationReport(BaseModel):
    total_test_transactions: int
    total_interventions: int
    successful_recoveries: int
    recovery_rate: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    avg_intervention_cost: float
    total_revenue_recovered: float
    total_intervention_cost: float
    roi_multiplier: float
    avg_recovery_time_minutes: float
    policy_block_rate: float