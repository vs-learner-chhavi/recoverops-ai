"""
RecoverOps AI — Analytics Engine
Computes aggregate metrics and trends for the dashboard.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.models import FailedTransaction, Intervention, PaymentStatus, InterventionStatus


class AnalyticsEngine:
    """Computes real-time analytics from the database."""

    async def get_recovery_trend(
        self, db: AsyncSession, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get daily recovery trend for the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(
                func.date(FailedTransaction.failed_at).label("date"),
                func.sum(FailedTransaction.amount).label("failed_amount"),
                func.sum(
                    case(
                        (FailedTransaction.status == PaymentStatus.RECOVERED, FailedTransaction.amount),
                        else_=0,
                    )
                ).label("recovered_amount"),
                func.count(FailedTransaction.id).label("total"),
                func.sum(
                    case(
                        (FailedTransaction.status == PaymentStatus.RECOVERED, 1),
                        else_=0,
                    )
                ).label("recovered_count"),
            )
            .where(FailedTransaction.failed_at >= cutoff)
            .group_by(func.date(FailedTransaction.failed_at))
            .order_by(func.date(FailedTransaction.failed_at))
        )

        trends = []
        for row in result.all():
            total = int(row.total) if row.total else 1
            recovered = int(row.recovered_count or 0)
            trends.append({
                "date": str(row.date),
                "failed_amount": float(row.failed_amount or 0),
                "recovered_amount": float(row.recovered_amount or 0),
                "recovery_rate": round(recovered / total * 100, 1),
                "intervention_count": 0,  # Would need a join
            })

        return trends


# Singleton
analytics_engine = AnalyticsEngine()