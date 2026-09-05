"""
RecoverOps AI — Full System Evaluation
Runs the complete pipeline against the synthetic dataset and measures:
  - Recovery Rate
  - Precision / Recall / F1
  - False Positive Rate
  - Total Revenue Recovered
  - ROI
  - Policy Block Rate
"""

import asyncio
import json
import math
from pathlib import Path
from datetime import datetime, timezone

# These will be computed during the evaluation run


async def run_evaluation():
    """Run full evaluation and generate report."""
    from app.database import init_db, async_session
    from app.recovery_engine import recovery_engine
    from data.generator import generate_dataset

    await init_db()

    # Generate test dataset
    print("📊 Generating 1,000 test transactions...")
    dataset = generate_dataset(1000)

    results = {
        "total": 0,
        "recovered": 0,
        "abandoned": 0,
        "escalated": 0,
        "policy_blocked": 0,
        "total_amount": 0,
        "recovered_amount": 0,
        "total_intervention_cost": 0,
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
    }

    print("🚀 Running recovery pipeline on test data...")

    async with async_session() as db:
        for i, record in enumerate(dataset):
            if i % 100 == 0:
                print(f"   Processing {i}/{len(dataset)}...")

            record["features"]["amount_log"] = round(
                math.log10(max(1, record["amount"])), 4
            )

            payment_data = {
                "razorpay_payment_id": record["razorpay_payment_id"],
                "amount": record["amount"],
                "currency": "INR",
                "payment_method": record["payment_method"],
                "bank": record["bank"],
                "failure_category": record["failure_category"],
                "error_code": record["error_code"],
                "error_description": record["error_description"],
                "customer_email": record["customer_email"],
                "customer_phone": record["customer_phone"],
            }

            try:
                result = await recovery_engine.process_failed_payment(
                    db=db, payment_data=payment_data
                )
                await db.commit()

                results["total"] += 1
                results["total_amount"] += record["amount"]

                status = result.get("status", "")
                was_actually_recoverable = record["was_recovered"]

                if status == "recovered":
                    results["recovered"] += 1
                    results["recovered_amount"] += record["amount"]
                    if was_actually_recoverable:
                        results["true_positives"] += 1
                    else:
                        results["false_positives"] += 1
                elif status == "abandoned":
                    results["abandoned"] += 1
                    if not was_actually_recoverable:
                        results["true_negatives"] += 1
                    else:
                        results["false_negatives"] += 1
                elif status == "escalated":
                    results["escalated"] += 1
                    results["policy_blocked"] += 1
                else:
                    if was_actually_recoverable:
                        results["false_negatives"] += 1
                    else:
                        results["true_negatives"] += 1

            except Exception as e:
                print(f"   ⚠️ Error processing record {i}: {e}")
                results["total"] += 1

    # Calculate metrics
    tp = results["true_positives"]
    fp = results["false_positives"]
    tn = results["true_negatives"]
    fn = results["false_negatives"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    recovery_rate = (
        results["recovered"] / results["total"] * 100
        if results["total"] > 0
        else 0
    )
    policy_block_rate = (
        results["policy_blocked"] / results["total"] * 100
        if results["total"] > 0
        else 0
    )

    report = {
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_test_transactions": results["total"],
        "total_recovered": results["recovered"],
        "total_abandoned": results["abandoned"],
        "total_escalated": results["escalated"],
        "recovery_rate_percent": round(recovery_rate, 2),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "total_failed_revenue": round(results["total_amount"], 2),
        "total_recovered_revenue": round(results["recovered_amount"], 2),
        "policy_block_rate_percent": round(policy_block_rate, 2),
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
        },
    }

    # Save report
    output_path = Path("docs")
    output_path.mkdir(exist_ok=True)
    with open(output_path / "EVALUATION.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print
    print("\n" + "=" * 60)
    print("📊 RECOVEROPS AI — EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Transactions:     {results['total']}")
    print(f"Recovered:              {results['recovered']}")
    print(f"Recovery Rate:          {recovery_rate:.1f}%")
    print(f"Precision:              {precision:.4f}")
    print(f"Recall:                 {recall:.4f}")
    print(f"F1 Score:               {f1:.4f}")
    print(f"False Positive Rate:    {fpr:.4f}")
    print(f"Total Failed Revenue:   ₹{results['total_amount']:,.2f}")
    print(f"Revenue Recovered:      ₹{results['recovered_amount']:,.2f}")
    print(f"Policy Block Rate:      {policy_block_rate:.1f}%")
    print("=" * 60)

    return report


if __name__ == "__main__":
    asyncio.run(run_evaluation())