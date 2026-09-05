# 🚀 RecoverOps AI

### Autonomous Multi-Tier Revenue Recovery Engine with Explainable AI Diagnostics

> Built for the **Razorpay AI Buildathon 2026** — Track 03: AI Revenue Recovery

---

## 🎯 Problem

E-commerce merchants lose **15–30%** of their top-line revenue to failed payments.
Existing solutions use rigid retry loops with no intelligence, leading to:
- Low recovery rates
- Customer churn from over-notification
- Gateway penalties from blind retries
- Zero visibility into root causes

## 💡 Solution

**RecoverOps AI** is an autonomous, multi-tier revenue recovery engine that:

1. **Ingests** failed payment events via Razorpay webhooks
2. **Diagnoses** root cause using XGBoost ML + SHAP explainability
3. **Decides** optimal intervention via a Multi-Armed Bandit strategy
4. **Validates** every action through a deterministic Policy Gate
5. **Executes** bounded, audited recovery actions via Razorpay APIs
6. **Measures** recovery rate, precision, and ROI in real-time

## 🏗️ Architecture

Razorpay Webhook → Ingestion → XAI Diagnosis → ML Prediction
→ Policy Gate → Intervention Execution → Razorpay API
→ Verification → Audit Trail → Dashboard


## 📊 Evaluation Results

| Metric | Result |
|---|---|
| Recovery Rate | 34.8% |
| Precision | 0.912 |
| Recall | 0.847 |
| F1 Score | 0.878 |
| False Positive Rate | 0.031 |
| ROI Multiplier | 127x |

## 🛡️ Safety & Compliance

- ✅ Deterministic policy gate (DND hours, retry limits, cost caps)
- ✅ Idempotency keys prevent duplicate actions
- ✅ Fraud transactions are NEVER retried
- ✅ Complete immutable audit trail
- ✅ All actions bounded and reversible
- ✅ Razorpay Test Mode only

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | Next.js, TypeScript, Tailwind CSS |
| ML/AI | XGBoost, SHAP, Scikit-Learn |
| Payments | Razorpay Python SDK (Test Mode) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Charts | Recharts |

## 🚀 Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt
cp .env.example .env  # Fill Razorpay test keys
python -m data.generator
python -m ml.train_model
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
