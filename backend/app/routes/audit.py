"""
RecoverOps AI — Audit Log API
Provides access to the immutable audit trail.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    transaction_id: Optional[str] = None,
    event_category: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Query audit logs with filtering."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    if transaction_id:
        query = query.where(AuditLog.transaction_id == transaction_id)
    if event_category:
        query = query.where(AuditLog.event_category == event_category)
    if severity:
        query = query.where(AuditLog.severity == severity)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    logs = result.scalars().all()

    return [
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
    ]

@router.get("/stats")
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get audit log statistics."""
    total = await db.execute(select(func.count(AuditLog.id)))

    by_category = await db.execute(
        select(
            AuditLog.event_category,
            func.count(AuditLog.id),
        ).group_by(AuditLog.event_category)
    )

    by_severity = await db.execute(
        select(
            AuditLog.severity,
            func.count(AuditLog.id),
        ).group_by(AuditLog.severity)
    )

    return {
        "total_entries": total.scalar(),
        "by_category": {
            row[0]: row[1] for row in by_category.all()
        },
        "by_severity": {
            row[0]: row[1] for row in by_severity.all()
        },
    }