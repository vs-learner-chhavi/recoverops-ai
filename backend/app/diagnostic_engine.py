"""
RecoverOps AI — Diagnostic Engine
Combines ML predictions with rule-based heuristics for comprehensive diagnosis.
"""

from typing import Dict, Any, Tuple
from ml.predictor import predictor
from ml.explainer import xai_explainer


class DiagnosticEngine:
    """
    Runs the full diagnostic pipeline on a failed transaction:
      1. Feature extraction
      2. ML prediction (recovery probability)
      3. SHAP explanation
      4. Intervention recommendation
    """

    def diagnose(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run full diagnostic on a transaction.
        Returns structured diagnosis with prediction + explanation.
        """
        # ML Prediction
        prob, should_recover, recommended = predictor.predict(transaction_data)

        # SHAP Explanation
        explanation = xai_explainer.explain(transaction_data)

        # Churn risk (inverse of recovery probability, adjusted)
        churn_risk = self._estimate_churn_risk(transaction_data, prob)

        return {
            "recovery_probability": round(prob, 4),
            "should_attempt_recovery": should_recover,
            "recommended_intervention": recommended,
            "churn_risk_score": round(churn_risk, 4),
            "xai_explanation": explanation,
            "confidence_tier": self._confidence_tier(prob),
        }

    def _estimate_churn_risk(
        self, data: Dict[str, Any], recovery_prob: float
    ) -> float:
        """
        Estimate churn risk based on failure type and recovery probability.
        Higher churn = customer more likely to abandon the merchant.
        """
        category = data.get("failure_category", "unknown")
        amount = float(data.get("amount", 0))

        base_churn = 1.0 - recovery_prob

        # High-value failures cause more churn
        if amount > 10000:
            base_churn += 0.10
        elif amount > 5000:
            base_churn += 0.05

        # Certain failure types frustrate customers more
        churn_multipliers = {
            "authentication_failed": 1.2,
            "card_expired": 1.1,
            "fraud_suspected": 1.5,
            "user_cancelled": 0.8,  # They already left
            "bank_technical": 0.9,  # Not merchant's fault
        }

        base_churn *= churn_multipliers.get(category, 1.0)

        return max(0.0, min(1.0, base_churn))

    def _confidence_tier(self, probability: float) -> str:
        """Classify confidence into human-readable tiers."""
        if probability >= 0.75:
            return "high"
        elif probability >= 0.50:
            return "medium"
        elif probability >= 0.25:
            return "low"
        else:
            return "very_low"


# Singleton
diagnostic_engine = DiagnosticEngine()