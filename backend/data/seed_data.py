"""
RecoverOps AI — Database Seeder (HIGH-RECOVERY FIXED)
Populates database with realistic recovered amounts, policy blocks, and active pipeline.
"""

import asyncio
import random
from datetime import datetime, timezone, timedelta

from app.database import init_db, async_session, engine
from app.models import (
    Base, FailedTransaction, Intervention, AuditLog,
    PaymentStatus, InterventionType, InterventionStatus, FailureCategory
)
from data.generator import generate_dataset
from ml.predictor import predictor
from ml.explainer import xai_explainer


async def seed_database(count: int = 200):
    # Reset DB tables cleanly
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print(f"🌱 Seeding database with {count} realistic transactions...")
    dataset = generate_dataset(count)

    async with async_session() as db:
        recovered_count = 0
        total_recovered_amount = 0.0

        for i, record in enumerate(dataset):
            # Predict probability
            prob, should_recover, recommended = predictor.predict({
                "amount": record["amount"],
                "payment_method": record["payment_method"],
                "bank": record["bank"],
                "failure_category": record["failure_category"],
                "hour": record["failed_at"].hour,
                "day_of_week": record["failed_at"].weekday(),
            })

            explanation = xai_explainer.explain({
                "amount": record["amount"],
                "payment_method": record["payment_method"],
                "bank": record["bank"],
                "failure_category": record["failure_category"],
                "hour": record["failed_at"].hour,
                "day_of_week": record["failed_at"].weekday(),
            })

            cat = record["failure_category"]

            # Determine realistic status
            if cat == "fraud_suspected" or prob < 0.20:
                status = PaymentStatus.ABANDONED
                rec_at = None
            elif random.random() < 0.15:  # Policy block / Escalated
                status = PaymentStatus.ESCALATED
                rec_at = None
            elif prob > 0.45 and random.random() < 0.75:  # RECOVERED!
                status = PaymentStatus.RECOVERED
                rec_at = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))
                recovered_count += 1
                total_recovered_amount += float(record["amount"])
            elif prob > 0.30:
                status = PaymentStatus.RECOVERING
                rec_at = None
            else:
                status = PaymentStatus.FAILED
                rec_at = None

            tx = FailedTransaction(
                razorpay_payment_id=record["razorpay_payment_id"],
                razorpay_order_id=record["razorpay_order_id"],
                amount=float(record["amount"]),
                currency="INR",
                payment_method=record["payment_method"],
                bank=record["bank"],
                card_network=record.get("card_network"),
                card_type=record.get("card_type"),
                customer_email=record["customer_email"],
                customer_phone=record["customer_phone"],
                failure_category=FailureCategory(cat) if cat in FailureCategory.__members__ else FailureCategory.UNKNOWN,
                error_code=record["error_code"],
                error_description=record["error_description"],
                error_source=record.get("error_source"),
                error_step=record.get("error_step"),
                recovery_probability=float(prob),
                recommended_intervention=InterventionType(recommended) if recommended in InterventionType.__members__ else InterventionType.PAYMENT_LINK,
                xai_explanation=explanation,
                status=status,
                failed_at=record["failed_at"],
                recovered_at=rec_at,
                retry_count=random.randint(1, 2) if status in [PaymentStatus.RECOVERED, PaymentStatus.RECOVERING] else 0,
            )
            db.add(tx)
            await db.flush()

            # Add corresponding intervention
            if status != PaymentStatus.ABANDONED:
                itype = InterventionType(recommended) if recommended in InterventionType.__members__ else InterventionType.PAYMENT_LINK
                istatus = (
                    InterventionStatus.COMPLETED if status == PaymentStatus.RECOVERED
                    else InterventionStatus.BLOCKED_BY_POLICY if status == PaymentStatus.ESCALATED
                    else InterventionStatus.EXECUTING
                )
                cost = 0.50 if recommended == "smart_retry" else 2.00 if recommended == "payment_link" else 1.50

                inv = Intervention(
                    transaction_id=tx.id,
                    idempotency_key=f"idem_{tx.id}_{i}",
                    intervention_type=itype,
                    tier=1 if recommended == "smart_retry" else 2,
                    status=istatus,
                    confidence_score=float(prob),
                    reasoning=explanation.get("summary", ""),
                    policy_approved=(status != PaymentStatus.ESCALATED),
                    policy_rejection_reason="Blocked by policy gate: High risk / DND / Cost cap" if status == PaymentStatus.ESCALATED else None,
                    resulted_in_recovery=(status == PaymentStatus.RECOVERED),
                    recovered_amount=float(record["amount"]) if status == PaymentStatus.RECOVERED else 0.0,
                    intervention_cost=cost,
                    payment_link_url=f"https://rzp.io/i/{record['razorpay_payment_id'][-8:]}" if recommended == "payment_link" else None,
                    created_at=record["failed_at"],
                    executed_at=record["failed_at"] + timedelta(minutes=5),
                )
                db.add(inv)

            # Add Audit Log
            log = AuditLog(
                transaction_id=tx.id,
                event_type="payment_ingested" if status != PaymentStatus.RECOVERED else "recovery_success",
                event_category="ai_decision",
                severity="info" if status != PaymentStatus.ESCALATED else "warning",
                actor="ai_engine",
                action=f"intervention_{recommended}",
                description=f"AI evaluated recovery probability: {prob:.1%}. Status: {status.value}",
                event_metadata={"prob": float(prob), "category": cat},
                created_at=record["failed_at"],
            )
            db.add(log)

        await db.commit()

    print(f"\n🎉 Seeding complete!")
    print(f"   → Total Transactions: {count}")
    print(f"   → Recovered: {recovered_count} transactions")
    print(f"   → Recovered Revenue: ₹{total_recovered_amount:,.2f}")


if __name__ == "__main__":
    asyncio.run(seed_database(200))