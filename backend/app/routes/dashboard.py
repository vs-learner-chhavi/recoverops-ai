"""
RecoverOps AI — Dashboard API
Provides real-time analytics, metrics, and transaction data for the frontend.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from app.database import get_db
from app.models import (
    FailedTransaction, Intervention, AuditLog,
    PaymentStatus, InterventionType, InterventionStatus,
)
from app.schemas import (
    DashboardMetrics, TransactionResponse, TransactionDetail,
    InterventionResponse, AuditLogResponse,
    RecoveryTrend, FailureCategoryBreakdown, InterventionEffectiveness,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated dashboard metrics."""
    # Total failed revenue
    total_failed = await db.execute(
        select(func.coalesce(func.sum(FailedTransaction.amount), 0))
    )
    total_failed_revenue = float(total_failed.scalar())

    # Total recovered revenue
    recovered = await db.execute(
        select(func.coalesce(func.sum(FailedTransaction.amount), 0)).where(
            FailedTransaction.status == PaymentStatus.RECOVERED
        )
    )
    total_recovered_revenue = float(recovered.scalar())

    # Recovery rate
    total_count = await db.execute(
        select(func.count(FailedTransaction.id))
    )
    total_transactions = int(total_count.scalar())

    recovered_count = await db.execute(
        select(func.count(FailedTransaction.id)).where(
            FailedTransaction.status == PaymentStatus.RECOVERED
        )
    )
    recovered_transactions = int(recovered_count.scalar())

    recovery_rate = (
        (recovered_transactions / total_transactions * 100)
        if total_transactions > 0
        else 0
    )

    # Active recoveries
    active = await db.execute(
        select(func.count(FailedTransaction.id)).where(
            FailedTransaction.status.in_([
                PaymentStatus.AT_RISK, PaymentStatus.RECOVERING
            ])
        )
    )
    active_recoveries = int(active.scalar())

    # Interventions
    interventions_count = await db.execute(
        select(func.count(Intervention.id))
    )
    interventions_executed = int(interventions_count.scalar())

    # Policy blocks
    policy_blocks_count = await db.execute(
        select(func.count(Intervention.id)).where(
            Intervention.status == InterventionStatus.BLOCKED_BY_POLICY
        )
    )
    policy_blocks = int(policy_blocks_count.scalar())

    # Average recovery time
    avg_time = await db.execute(
        select(
            func.avg(
                func.julianday(FailedTransaction.recovered_at) -
                func.julianday(FailedTransaction.failed_at)
            ) * 24 * 60  # Convert days to minutes
        ).where(
            FailedTransaction.status == PaymentStatus.RECOVERED,
            FailedTransaction.recovered_at.isnot(None),
        )
    )
    avg_recovery_time = avg_time.scalar()

    # ROI
    total_cost = await db.execute(
        select(func.coalesce(func.sum(Intervention.intervention_cost), 0))
    )
    total_intervention_cost = float(total_cost.scalar())
    roi = (
        total_recovered_revenue / total_intervention_cost
        if total_intervention_cost > 0
        else 0
    )

    return DashboardMetrics(
        total_failed_revenue=round(total_failed_revenue, 2),
        total_recovered_revenue=round(total_recovered_revenue, 2),
        recovery_rate=round(recovery_rate, 1),
        total_transactions=total_transactions,
        active_recoveries=active_recoveries,
        interventions_executed=interventions_executed,
        policy_blocks=policy_blocks,
        avg_recovery_time_minutes=round(avg_recovery_time, 1) if avg_recovery_time else None,
        roi_multiplier=round(roi, 1),
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get recent transactions with optional filtering."""
    query = select(FailedTransaction).order_by(
        FailedTransaction.created_at.desc()
    )

    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.where(FailedTransaction.status == status_enum)
        except ValueError:
            pass

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    transactions = result.scalars().all()

    return [
        TransactionResponse(
            id=t.id,
            razorpay_payment_id=t.razorpay_payment_id,
            amount=t.amount,
            currency=t.currency,
            payment_method=t.payment_method,
            status=t.status.value if t.status else "unknown",
            failure_category=t.failure_category.value if t.failure_category else None,
            recovery_probability=t.recovery_probability,
            churn_risk_score=t.churn_risk_score,
            xai_explanation=t.xai_explanation,
            recommended_intervention=(
                t.recommended_intervention.value
                if t.recommended_intervention
                else None
            ),
            retry_count=t.retry_count,
            failed_at=t.failed_at,
            recovered_at=t.recovered_at,
        )
        for t in transactions
    ]


@router.get("/transactions/{transaction_id}", response_model=TransactionDetail)
async def get_transaction_detail(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed transaction information with interventions and audit logs."""
    result = await db.execute(
        select(FailedTransaction).where(FailedTransaction.id == transaction_id)
    )
    t = result.scalar_one_or_none()

    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Get interventions
    interventions_result = await db.execute(
        select(Intervention).where(
            Intervention.transaction_id == transaction_id
        ).order_by(Intervention.created_at.desc())
    )
    interventions = interventions_result.scalars().all()

    # Get audit logs
    logs_result = await db.execute(
        select(AuditLog).where(
            AuditLog.transaction_id == transaction_id
        ).order_by(AuditLog.created_at.desc())
    )
    logs = logs_result.scalars().all()

    return TransactionDetail(
        id=t.id,
        razorpay_payment_id=t.razorpay_payment_id,
        amount=t.amount,
        currency=t.currency,
        payment_method=t.payment_method,
        status=t.status.value if t.status else "unknown",
        failure_category=t.failure_category.value if t.failure_category else None,
        recovery_probability=t.recovery_probability,
        churn_risk_score=t.churn_risk_score,
        xai_explanation=t.xai_explanation,
        recommended_intervention=(
            t.recommended_intervention.value
            if t.recommended_intervention
            else None
        ),
        retry_count=t.retry_count,
        failed_at=t.failed_at,
        recovered_at=t.recovered_at,
        customer_email=t.customer_email,
        customer_phone=t.customer_phone,
        bank=t.bank,
        card_network=t.card_network,
        error_source=t.error_source,
        error_step=t.error_step,
        interventions=[
            InterventionResponse(
                id=i.id,
                intervention_type=i.intervention_type.value if i.intervention_type else "unknown",
                tier=i.tier,
                status=i.status.value if i.status else "unknown",
                confidence_score=i.confidence_score,
                reasoning=i.reasoning,
                payment_link_url=i.payment_link_url,
                message_content=i.message_content,
                channel=i.channel,
                policy_approved=i.policy_approved,
                policy_rejection_reason=i.policy_rejection_reason,
                resulted_in_recovery=i.resulted_in_recovery,
                recovered_amount=i.recovered_amount,
                intervention_cost=i.intervention_cost,
                created_at=i.created_at,
                executed_at=i.executed_at,
            )
            for i in interventions
        ],
                audit_logs=[
            AuditLogResponse(
                id=l.id,
                event_type=l.event_type,
                event_category=l.event_category,
                severity=l.severity,
                actor=l.actor,
                action=l.action,
                description=l.description,
                metadata=l.event_metadata,
                created_at=l.created_at,
            )
            for l in logs
        ],
    )


@router.get("/failure-breakdown", response_model=List[FailureCategoryBreakdown])
async def get_failure_breakdown(
    db: AsyncSession = Depends(get_db),
):
    """Get failure category distribution with recovery rates."""
    result = await db.execute(
        select(
            FailedTransaction.failure_category,
            func.count(FailedTransaction.id).label("count"),
            func.sum(FailedTransaction.amount).label("total_amount"),
            func.sum(
                case(
                    (FailedTransaction.status == PaymentStatus.RECOVERED, 1),
                    else_=0,
                )
            ).label("recovered_count"),
        ).group_by(FailedTransaction.failure_category)
    )

    rows = result.all()
    return [
        FailureCategoryBreakdown(
            category=row[0].value if row[0] else "unknown",
            count=int(row[1]),
            total_amount=float(row[2] or 0),
            recovery_rate=round(
                int(row[3] or 0) / int(row[1]) * 100, 1
            ) if int(row[1]) > 0 else 0,
        )
        for row in rows
    ]


@router.get("/intervention-effectiveness", response_model=List[InterventionEffectiveness])
async def get_intervention_effectiveness(
    db: AsyncSession = Depends(get_db),
):
    """Get effectiveness metrics for each intervention type."""
    result = await db.execute(
        select(
            Intervention.intervention_type,
            func.count(Intervention.id).label("total"),
            func.sum(
                case(
                    (Intervention.resulted_in_recovery == True, 1),
                    else_=0,
                )
            ).label("successful"),
            func.sum(
                case(
                    (Intervention.resulted_in_recovery == True, Intervention.recovered_amount),
                    else_=0,
                )
            ).label("total_recovered"),
            func.avg(Intervention.intervention_cost).label("avg_cost"),
        ).where(
            Intervention.status != InterventionStatus.BLOCKED_BY_POLICY
        ).group_by(Intervention.intervention_type)
    )

    rows = result.all()
    return [
        InterventionEffectiveness(
            intervention_type=row[0].value if row[0] else "unknown",
            total_executed=int(row[1]),
            successful=int(row[2] or 0),
            success_rate=round(
                int(row[2] or 0) / int(row[1]) * 100, 1
            ) if int(row[1]) > 0 else 0,
            total_recovered=float(row[3] or 0),
            avg_cost=round(float(row[4] or 0), 2),
        )
        for row in rows
    ]