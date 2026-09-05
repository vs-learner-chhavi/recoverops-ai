# 🚀 RecoverOps AI

### Autonomous Multi-Tier Revenue Recovery Engine with Explainable AI

<p align="center">
  <strong>Turn failed payments into recoverable revenue — intelligently, safely, and measurably.</strong>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-evaluation-results">Results</a>
</p>

> 🏆 Built for the **Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**

---

## 📌 Overview

**RecoverOps AI** is an autonomous revenue recovery platform designed to help e-commerce businesses recover revenue lost because of failed payments.

Instead of blindly retrying failed transactions, RecoverOps AI combines **machine learning, explainable AI, policy-based guardrails, and adaptive intervention strategies** to determine what should happen next — and whether an action is safe to execute.

The platform provides a real-time **Recovery Command Center** where operators can monitor failed payments, understand why they failed, simulate interventions, inspect recovery analytics, and review a complete audit trail.

### The core idea

```text
Failed Payment
      ↓
Understand Why
      ↓
Predict Recovery Probability
      ↓
Choose Best Intervention
      ↓
Check Safety Policies
      ↓
Execute Bounded Action
      ↓
Verify Outcome
      ↓
Learn & Measure
```

---

## 🎯 Problem

Failed payments represent a significant source of avoidable revenue leakage for online merchants. Traditional recovery systems often rely on fixed retry schedules and generic customer notifications.

This creates several problems:

- ❌ **Low recovery efficiency** — the same retry strategy is applied to different failure scenarios.
- ❌ **Customer fatigue** — unnecessary or excessive notifications can damage the customer experience.
- ❌ **Gateway and operational costs** — blind retries consume resources without considering expected value.
- ❌ **Poor explainability** — teams may know that a payment failed without knowing what caused it or why an action was chosen.
- ❌ **Limited control** — automated actions can become risky without explicit retry, timing, cost, and fraud safeguards.
- ❌ **Weak observability** — recovery decisions and outcomes are difficult to audit end-to-end.

RecoverOps AI addresses these gaps with an intelligent, explainable, and policy-controlled recovery loop.

---

## 💡 Solution

RecoverOps AI turns payment recovery into a **closed-loop decision system**:

1. **Ingest** failed payment events through Razorpay webhooks.
2. **Diagnose** the likely root cause using an XGBoost model and SHAP explanations.
3. **Predict** the likelihood that a payment can be recovered.
4. **Select** an intervention using a Multi-Armed Bandit strategy.
5. **Validate** the proposed action through a deterministic Policy Gate.
6. **Execute** bounded recovery actions through Razorpay APIs.
7. **Verify** the result and prevent duplicate execution with idempotency controls.
8. **Audit** every decision and action.
9. **Measure** recovery performance, precision, ROI, and intervention effectiveness in real time.

---

## ✨ Features

### 🧠 Explainable AI Diagnosis

Understand *why* a payment is likely to fail or recover instead of relying on a black-box prediction.

- XGBoost-based prediction
- SHAP feature attribution
- Root-cause diagnosis
- Positive and negative recovery factors
- Recovery probability and confidence signals

### 🎯 Adaptive Intervention Selection

Choose recovery strategies dynamically instead of using one fixed retry policy.

- Multi-Armed Bandit strategy
- Intervention effectiveness tracking
- Data-driven action selection
- Continuous performance measurement

### 🛡️ Deterministic Safety Layer

AI can recommend an action, but policy rules decide whether that action is allowed.

- DND-hour protection
- Retry limits per payment
- Contact-attempt limits
- Cost caps
- Minimum confidence thresholds
- Fraud transactions are never retried
- Idempotency protection against duplicate actions

### ⚡ Autonomous Recovery Execution

Execute approved interventions through Razorpay Test Mode while keeping actions bounded and auditable.

### 📊 Real-Time Recovery Command Center

The Next.js dashboard provides a unified view of:

- Revenue at risk
- Revenue recovered
- Active recovery pipeline
- ROI multiplier
- Live recovery feed
- Failure distribution
- Intervention effectiveness
- Explainable AI breakdowns
- Payment recovery simulator
- Audit trail

### 🔍 Complete Auditability

Every important decision is traceable through a structured audit trail, making the system easier to inspect, debug, and evaluate.

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   Razorpay Webhook   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Ingestion       │
                    │  Event Normalization │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    XAI Diagnosis     │
                    │   XGBoost + SHAP     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Recovery Prediction  │
                    │ Probability/Signals  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Intervention Policy  │
                    │  Multi-Armed Bandit  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Policy Gate      │
                    │ Safety + Constraints │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                   BLOCK               ALLOW
                     │                   │
                     ▼                   ▼
                 Audit Log      ┌─────────────────┐
                                 │ Intervention    │
                                 │   Execution     │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Razorpay API    │
                                 │   Test Mode     │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   Verification  │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Audit + Metrics │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Recovery        │
                                 │ Command Center  │
                                 └─────────────────┘
```

---

## 🔄 How It Works

### 1. Event ingestion

A failed payment event enters the system through a Razorpay webhook and is normalized into a form the recovery engine can process.

### 2. AI diagnosis

The ML layer analyzes payment and transaction signals to estimate recovery potential. SHAP provides feature-level explanations so operators can understand the prediction.

### 3. Intervention decision

The decision layer evaluates available recovery interventions and selects a strategy using adaptive reward signals rather than a fixed retry sequence.

### 4. Policy validation

Before any action is executed, the deterministic Policy Gate checks business and safety constraints such as retry limits, DND hours, confidence thresholds, cost caps, and fraud rules.

### 5. Controlled execution

Only approved interventions are executed, with idempotency controls designed to prevent duplicate actions.

### 6. Verification & learning

The system verifies the outcome, records the decision in the audit trail, and updates operational metrics so recovery performance can be evaluated continuously.

---

## 📊 Evaluation Results

The current evaluation reports the following results:

| Metric | Result |
|---|---:|
| Recovery Rate | **34.8%** |
| Precision | **0.912** |
| Recall | **0.847** |
| F1 Score | **0.878** |
| False Positive Rate | **0.031** |
| ROI Multiplier | **127×** |

> These figures represent the project's current evaluation results and should be interpreted in the context of the project's test/evaluation setup rather than as production guarantees.

---

## 🛡️ Safety, Reliability & Compliance-Oriented Controls

RecoverOps AI follows a **policy-first automation model**: the ML system can recommend an intervention, but deterministic rules constrain what the system is allowed to execute.

- ✅ DND-hour protection
- ✅ Maximum retries per payment
- ✅ Maximum customer contact attempts
- ✅ Configurable cost cap
- ✅ Minimum confidence threshold
- ✅ Fraud transactions are never retried
- ✅ Idempotency keys for duplicate-action prevention
- ✅ Complete audit trail
- ✅ Bounded and reversible recovery actions where supported
- ✅ Razorpay **Test Mode** for payment integration

> **Important:** This project is a buildathon/prototype system. It is not presented as production-ready financial infrastructure or as a substitute for merchant, payment-network, legal, or compliance review.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript |
| UI | Tailwind CSS, Framer Motion, Lucide React |
| Data Visualization | Recharts |
| Backend | Python, FastAPI |
| Database | SQLite (development) / PostgreSQL (production target) |
| ML | XGBoost, Scikit-Learn |
| Explainability | SHAP |
| Payments | Razorpay Python SDK — Test Mode |
| API/HTTP | FastAPI, HTTPX, WebSockets |
| Scheduling | APScheduler |
| AI/LLM | OpenAI, LangChain / LangChain OpenAI |
| Data | Pandas, NumPy, Joblib |

---

## 📁 Project Structure

```text
recoverops-ai/
├── backend/
│   ├── app/                  # FastAPI application and API routes
│   ├── data/                 # Data generation / datasets
│   ├── ml/                   # Model training and ML logic
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment configuration template
│
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages and global styles
│   │   ├── components/       # Dashboard UI components
│   │   ├── hooks/             # React hooks
│   │   ├── lib/               # Client utilities / API helpers
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

Make sure you have:

- **Python 3.10+**
- **Node.js 18+**
- **npm**
- A **Razorpay Test Mode** account/credential set if you want to exercise the payment integration
- PostgreSQL if you want to run with the production-target database configuration

### 1. Clone the repository

```bash
git clone https://github.com/vs-learner-chhavi/recoverops-ai.git
cd recoverops-ai
```

### 2. Configure the backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, you can use:

```powershell
Copy-Item .env.example .env
```

Then configure the required values in `.env`, including Razorpay Test Mode credentials and the database URL.

### 3. Prepare data and model

From the `backend` directory:

```bash
python -m data.generator
python -m ml.train_model
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation is typically available at:

```text
http://localhost:8000/docs
```

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Next.js development server will normally be available at:

```text
http://localhost:3000
```

---

## 🔐 Environment Variables

The backend `.env.example` defines configuration for Razorpay, PostgreSQL, OpenAI, the API server, and recovery policies.

| Variable | Purpose |
|---|---|
| `RAZORPAY_KEY_ID` | Razorpay Test Mode key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay Test Mode secret |
| `RAZORPAY_WEBHOOK_SECRET` | Webhook signature verification secret |
| `DATABASE_URL` | Database connection string |
| `OPENAI_API_KEY` | LLM-powered dunning message functionality |
| `HOST` | Backend host |
| `PORT` | Backend port |
| `DEBUG` | Development/debug configuration |
| `MAX_RETRIES_PER_PAYMENT` | Maximum retry count |
| `MAX_CONTACT_ATTEMPTS` | Maximum customer contact attempts |
| `DND_START_HOUR` | Start of DND window |
| `DND_END_HOUR` | End of DND window |
| `COST_CAP_PERCENTAGE` | Maximum configured recovery-action cost |
| `MIN_CONFIDENCE_THRESHOLD` | Minimum confidence required by the policy layer |

**Never commit real API keys, secrets, webhook secrets, or production credentials to Git.**

---

## 🖥️ Dashboard

The frontend is designed as a **Recovery Command Center** rather than a static analytics page.

### Main sections

- **Overview** — high-level recovery performance and revenue metrics.
- **Recovery Activity** — live failed-payment feed with filtering and explainable AI details.
- **Analytics** — failure distribution and intervention effectiveness.
- **Simulator** — test recovery scenarios before taking action.
- **Audit Trail** — inspect system decisions and recovery events.

The UI uses responsive layouts, glassmorphism-inspired surfaces, animated transitions, interactive states, and a custom dark visual system for a focused operations experience.

---

## 🧪 Development

### Frontend

```bash
cd frontend
npm run dev
```

Production build:

```bash
npm run build
npm run start
```

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Recommended development flow

1. Start the backend API.
2. Start the Next.js frontend.
3. Generate/prepare evaluation data if needed.
4. Train the ML model when the training pipeline changes.
5. Use the dashboard to inspect recovery activity and diagnostics.
6. Use the simulator to validate intervention behavior.
7. Review the audit trail after executing test actions.

---

## 🔮 Future Roadmap

- [ ] Production-grade event streaming and queue infrastructure
- [ ] Richer intervention policies and merchant-specific strategies
- [ ] Online learning for intervention optimization
- [ ] Advanced fraud/risk signals
- [ ] Multi-merchant tenancy and role-based access control
- [ ] Deeper cohort and customer-level analytics
- [ ] Automated model monitoring and drift detection
- [ ] Expanded payment-provider integrations
- [ ] Production observability, alerting, and SLOs
- [ ] Comprehensive automated testing and CI/CD

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

A typical workflow is:

```bash
git checkout -b feature/your-feature
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

Then open a pull request with:

- What changed
- Why the change was needed
- How it was tested
- Any screenshots or demo notes for UI changes

---

## 📜 License

No license file is currently defined in the repository. Until a license is added, the project should be treated as **all rights reserved**.

---

## 👩‍💻 Built With

Built with **Python, FastAPI, Next.js, TypeScript, XGBoost, SHAP, Razorpay Test Mode, and a policy-first approach to autonomous revenue recovery.**

---

## ⭐ Why RecoverOps AI?

RecoverOps AI is not simply a payment retry script.

It is designed around a stronger principle:

> **Predict → Explain → Decide → Guard → Act → Verify → Learn**

That combination of **AI intelligence + deterministic safety + measurable outcomes** is what makes the platform suitable as a foundation for intelligent revenue recovery.
