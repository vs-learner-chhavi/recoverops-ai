"""
RecoverOps AI — ML Prediction Engine
Loads trained model and returns predictions with confidence scores.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from ml.feature_engineering import extract_features, get_feature_names


class RecoveryPredictor:
    """
    Wraps the trained XGBoost model for real-time prediction.
    Thread-safe, loads model once on initialization.
    """

    def __init__(self, model_dir: str = "ml/models"):
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_names = get_feature_names()
        self._load_model()

    def _load_model(self):
        model_path = self.model_dir / "xgb_recovery_model.joblib"
        if model_path.exists():
            self.model = joblib.load(model_path)
            print(f"✅ ML Model loaded from {model_path}")
        else:
            print(f"⚠️  No trained model found at {model_path}")
            self.model = None

    def predict(
        self, transaction_data: Dict[str, Any]
    ) -> Tuple[float, bool, str]:
        """
        Predict recovery probability for a transaction.
        Returns (probability, should_attempt_recovery, recommended_intervention).
        """
        if self.model is None:
            # Fallback: rule-based prediction
            return self._rule_based_prediction(transaction_data)

        features = extract_features(transaction_data)
        feature_vector = pd.DataFrame(
            [features], columns=self.feature_names
        )

        # Predict probability
        prob = float(self.model.predict_proba(feature_vector)[0, 1])

        # Determine intervention
        should_recover = prob >= 0.3  # Low threshold — we're trying to recover
        intervention = self._select_intervention(
            prob, transaction_data, features
        )

        return prob, should_recover, intervention

    def _select_intervention(
        self,
        probability: float,
        transaction: Dict[str, Any],
        features: Dict[str, float],
    ) -> str:
        """
        Select the optimal intervention based on probability,
        failure category, and transaction context.
        """
        category = transaction.get("failure_category", "unknown")

        # Tier 1: Smart Retry — for technical/gateway failures
        if category in ("bank_technical", "network_error", "gateway_error"):
            if probability >= 0.5:
                return "smart_retry"

        # Tier 2: Payment Link — for customer-side issues
        if category in (
            "insufficient_funds", "card_expired",
            "authentication_failed", "user_cancelled"
        ):
            return "payment_link"

        # Tier 3: Nudge — for lower probability but recoverable
        if probability >= 0.2 and category != "fraud_suspected":
            return "whatsapp_nudge"

        # Default: escalate
        if probability < 0.15 or category == "fraud_suspected":
            return "manual_escalation"

        return "payment_link"

    def _rule_based_prediction(
        self, transaction: Dict[str, Any]
    ) -> Tuple[float, bool, str]:
        """Fallback when no ML model is available."""
        category = transaction.get("failure_category", "unknown")

        rule_map = {
            "bank_technical": (0.72, True, "smart_retry"),
            "network_error": (0.80, True, "smart_retry"),
            "gateway_error": (0.75, True, "smart_retry"),
            "insufficient_funds": (0.35, True, "payment_link"),
            "card_expired": (0.25, True, "payment_link"),
            "authentication_failed": (0.55, True, "payment_link"),
            "user_cancelled": (0.40, True, "whatsapp_nudge"),
            "fraud_suspected": (0.05, False, "manual_escalation"),
            "unknown": (0.30, True, "payment_link"),
        }

        prob, should_recover, intervention = rule_map.get(
            category, (0.30, True, "payment_link")
        )
        return prob, should_recover, intervention


# Singleton
predictor = RecoveryPredictor()