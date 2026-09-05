"""
RecoverOps AI — Model Training Pipeline (FIXED)
Trains an XGBoost classifier with robust Cross-Validation and SHAP explainability.
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_score, recall_score, f1_score,
    roc_auc_score,
)
from xgboost import XGBClassifier
import shap

from ml.feature_engineering import get_feature_names


def load_training_data(csv_path: str = "data/synthetic/training_data.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} records from {csv_path}")
    print(f"   Recovery rate: {df['was_recovered'].mean()*100:.1f}%")
    return df


def prepare_features(df: pd.DataFrame):
    """Prepare feature matrix X and target vector y with strict alignment."""
    feature_cols = get_feature_names()

    # Check alignment
    available_cols = [c for c in feature_cols if c in df.columns]
    missing_cols = [c for c in feature_cols if c not in df.columns]

    print(f"\n📋 Feature alignment check:")
    print(f"   Expected: {len(feature_cols)} features")
    print(f"   Found:    {len(available_cols)} features")

    if missing_cols:
        print(f"   ⚠️ Missing: {missing_cols}. Filling with 0.0")
        for col in missing_cols:
            df[col] = 0.0
    else:
        print(f"   ✅ All features aligned perfectly!")

    X = df[feature_cols].astype(float)
    y = df["was_recovered"].astype(int)

    return X, y


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    output_dir: str = "ml/models",
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 80/20 Stratified Split
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, test_idx = next(skf.split(X, y))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"   Train recovery rate: {y_train.mean()*100:.1f}%")
    print(f"   Test recovery rate:  {y_test.mean()*100:.1f}%")

    # XGBoost configuration (no early_stopping_rounds in constructor so cross_val_score works)
    model = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.06,
        subsample=0.80,
        colsample_bytree=0.75,
        min_child_weight=4,
        gamma=0.15,
        reg_alpha=0.05,
        reg_lambda=0.5,
        random_state=42,
        eval_metric="logloss",
        scale_pos_weight=float((y == 0).sum() / max((y == 1).sum(), 1)),
    )

    # Fit final model on train set
    model.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"\n🎯 Model Performance (Held-out Test Set):")
    print(f"   Precision:  {precision:.4f}")
    print(f"   Recall:     {recall:.4f}")
    print(f"   F1 Score:   {f1:.4f}")
    print(f"   ROC AUC:    {auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Not Recovered', 'Recovered'])}")

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"   False Positive Rate: {fpr:.4f}")
    print(f"   Confusion Matrix:\n{cm}")

    # 5-Fold Stratified Cross Validation
    print(f"\n🔄 Running 5-Fold Cross Validation...")
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring="f1")
    print(f"   5-Fold CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Feature Importance
    importance = dict(zip(X.columns, model.feature_importances_))
    sorted_importance = dict(
        sorted(importance.items(), key=lambda x: x[1], reverse=True)
    )
    print(f"\n📈 Feature Importance (Top 10):")
    for i, (feat, imp) in enumerate(sorted_importance.items()):
        if i >= 10:
            break
        print(f"   {i+1}. {feat}: {imp:.4f}")

    # SHAP Explainer
    print(f"\n🔍 Initializing SHAP Tree Explainer...")
    explainer = shap.TreeExplainer(model)

    # Save artifacts
    joblib.dump(model, output_path / "xgb_recovery_model.joblib")
    joblib.dump(explainer, output_path / "shap_explainer.joblib")

    metrics = {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "false_positive_rate": round(float(fpr), 4),
        "cv_f1_mean": round(float(cv_scores.mean()), 4),
        "cv_f1_std": round(float(cv_scores.std()), 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "feature_importance": {k: round(float(v), 4) for k, v in sorted_importance.items()},
        "training_samples": len(X_train),
        "test_samples": len(X_test),
    }

    with open(output_path / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✅ Model & Explainer successfully saved to {output_path}")
    print(f"   → xgb_recovery_model.joblib")
    print(f"   → shap_explainer.joblib")
    print(f"   → model_metrics.json")

    return model, explainer, metrics


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    csv_path = "data/synthetic/training_data.csv"
    if not Path(csv_path).exists():
        print("⚠️ No training data found. Run: python -m data.generator")
        sys.exit(1)

    df = load_training_data(csv_path)
    X, y = prepare_features(df)
    train_model(X, y)