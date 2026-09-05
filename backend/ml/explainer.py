"""
RecoverOps AI — SHAP-based Explainability Engine (FIXED)
Generates human-readable explanations with strictly sanitized native Python types.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

from ml.feature_engineering import extract_features, get_feature_names


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively converts numpy numbers and arrays to native Python types
    so SQLite/SQLAlchemy JSON columns serialize without error.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return [sanitize_for_json(v) for v in obj.tolist()]
    return obj


class XAIExplainer:
    """
    Produces SHAP-based explanations for model predictions.
    Guarantees all output values are native JSON-serializable Python types.
    """

    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = Path(model_dir)
        self.explainer = None
        self.model = None
        self.feature_names = get_feature_names()
        self._load()

    def _load(self):
        explainer_path = self.model_dir / "shap_explainer.joblib"
        model_path = self.model_dir / "xgb_recovery_model.joblib"

        if explainer_path.exists():
            self.explainer = joblib.load(explainer_path)
            print("✅ SHAP Explainer loaded")
        if model_path.exists():
            self.model = joblib.load(model_path)

    def explain(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        features = extract_features(transaction_data)
        feature_vector = pd.DataFrame([features], columns=self.feature_names)

        if self.explainer is None or self.model is None:
            return self._rule_based_explanation(transaction_data)

        # Compute SHAP values
        shap_values = self.explainer.shap_values(feature_vector)

        if isinstance(shap_values, list):
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(getattr(shap_values, "shape", [])) == 3:
            sv = shap_values[0, :, 1]
        elif len(getattr(shap_values, "shape", [])) == 2:
            sv = shap_values[0]
        else:
            sv = shap_values

        # Base value handling
        exp_val = self.explainer.expected_value
        if isinstance(exp_val, (list, np.ndarray)):
            base_val = float(exp_val[1]) if len(exp_val) > 1 else float(exp_val[0])
        else:
            base_val = float(exp_val)

        # Build feature contributions with explicit float casts
        contributions = []
        for i, fname in enumerate(self.feature_names):
            val = float(features[fname])
            shap_val = float(sv[i])
            contributions.append({
                "feature": str(fname),
                "value": round(val, 4),
                "shap_value": round(shap_val, 4),
                "impact": "positive" if shap_val > 0 else "negative",
                "magnitude": round(abs(shap_val), 4),
            })

        # Sort contributions by magnitude
        contributions.sort(key=lambda x: x["magnitude"], reverse=True)

        top_positive = [c for c in contributions if c["impact"] == "positive"][:3]
        top_negative = [c for c in contributions if c["impact"] == "negative"][:3]

        pred_shift = float(np.sum(sv))
        summary = self._generate_summary(transaction_data, top_positive, top_negative)
        diagnosis = self._diagnose_failure(transaction_data)

        raw_result = {
            "base_value": round(base_val, 4),
            "prediction_shift": round(pred_shift, 4),
            "top_positive_factors": top_positive,
            "top_negative_factors": top_negative,
            "all_contributions": contributions[:10],
            "summary": summary,
            "diagnosis": diagnosis,
        }

        # Run through JSON sanitizer to guarantee zero numpy types
        return sanitize_for_json(raw_result)

    def _generate_summary(
        self,
        transaction: Dict[str, Any],
        top_positive: List[Dict],
        top_negative: List[Dict],
    ) -> str:
        category = str(transaction.get("failure_category", "unknown"))

        category_descriptions = {
            "bank_technical": "bank-side technical failure",
            "insufficient_funds": "insufficient funds in customer account",
            "card_expired": "expired payment card",
            "authentication_failed": "authentication/OTP failure",
            "network_error": "network connectivity issue",
            "fraud_suspected": "suspected fraudulent activity",
            "user_cancelled": "customer-initiated cancellation",
            "gateway_error": "payment gateway error",
        }

        cause = category_descriptions.get(category, "unknown failure")
        summary = f"Primary failure cause: {cause}."

        if top_positive:
            factor = self._feature_to_human(top_positive[0]["feature"])
            summary += f" Recovery is supported by {factor}."

        if top_negative:
            factor = self._feature_to_human(top_negative[0]["feature"])
            summary += f" Recovery is hindered by {factor}."

        return summary

    def _feature_to_human(self, feature_name: str) -> str:
        mapping = {
            "amount": "transaction amount",
            "amount_log": "transaction size",
            "amount_bucket": "payment tier",
            "hour": "time of day",
            "day_of_week": "day of week",
            "is_business_hours": "business hours timing",
            "is_late_night": "late-night timing",
            "is_weekend": "weekend timing",
            "is_peak_hours": "peak shopping hours",
            "is_card": "card payment method",
            "is_upi": "UPI payment method",
            "is_netbanking": "netbanking method",
            "is_wallet": "wallet payment method",
            "bank_risk_score": "bank reliability score",
            "failure_category_encoded": "failure type",
            "is_recoverable_category": "failure recoverability",
        }
        return mapping.get(feature_name, feature_name.replace("_", " "))

    def _diagnose_failure(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        category = str(transaction.get("failure_category", "unknown"))

        diagnoses = {
            "bank_technical": {
                "root_cause": "Bank infrastructure issue",
                "recommended_action": "Wait for bank recovery, then smart retry",
                "urgency": "medium",
                "retry_window": "30-60 minutes",
            },
            "insufficient_funds": {
                "root_cause": "Customer has insufficient balance",
                "recommended_action": "Send payment link with grace period",
                "urgency": "low",
                "retry_window": "24-48 hours",
            },
            "card_expired": {
                "root_cause": "Payment card has expired",
                "recommended_action": "Notify customer to update card details",
                "urgency": "low",
                "retry_window": "24-72 hours",
            },
            "authentication_failed": {
                "root_cause": "Customer failed OTP/3DS verification",
                "recommended_action": "Send new payment link with simplified flow",
                "urgency": "medium",
                "retry_window": "15-30 minutes",
            },
            "network_error": {
                "root_cause": "Network connectivity disruption",
                "recommended_action": "Immediate smart retry",
                "urgency": "high",
                "retry_window": "5-15 minutes",
            },
            "fraud_suspected": {
                "root_cause": "Transaction flagged by risk engine",
                "recommended_action": "Do NOT retry. Escalate to manual review.",
                "urgency": "critical",
                "retry_window": "N/A — manual review required",
            },
            "user_cancelled": {
                "root_cause": "Customer abandoned payment flow",
                "recommended_action": "Send gentle reminder with incentive",
                "urgency": "low",
                "retry_window": "1-4 hours",
            },
            "gateway_error": {
                "root_cause": "Payment gateway malfunction",
                "recommended_action": "Retry via alternate gateway if available",
                "urgency": "high",
                "retry_window": "15-45 minutes",
            },
        }

        return diagnoses.get(category, {
            "root_cause": "Unknown failure",
            "recommended_action": "Escalate to manual review",
            "urgency": "medium",
            "retry_window": "30 minutes",
        })

    def _rule_based_explanation(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "base_value": 0.5,
            "prediction_shift": 0.0,
            "top_positive_factors": [],
            "top_negative_factors": [],
            "all_contributions": [],
            "summary": f"Rule-based diagnosis: {transaction.get('failure_category', 'unknown')} failure detected.",
            "diagnosis": self._diagnose_failure(transaction),
        }


# Singleton instance
xai_explainer = XAIExplainer()