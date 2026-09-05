# 🚀 RecoverOps AI

<p align="center">
  <strong>Autonomous Multi-Tier Revenue Recovery Engine with Explainable AI</strong>
</p>

<p align="center">Turn failed payments into recoverable revenue — intelligently, safely, and measurably.</p>

<p align="center">
  <a href="https://recoverops-ai.vercel.app">🌐 Live Demo</a> •
  <a href="https://recoverops-ai-api.onrender.com/docs">⚡ API Docs</a> •
  <a href="https://github.com/vs-learner-chhavi/recoverops-ai">💻 GitHub</a>
</p>

> 🏆 Built for **Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery**

---

## 🌐 Live Deployment

| Component | Link |
|---|---|
| 🖥️ **RecoverOps AI Dashboard** | **https://recoverops-ai.vercel.app** |
| ⚡ **Backend API** | **https://recoverops-ai-api.onrender.com** |
| 📚 **Interactive API Docs** | **https://recoverops-ai-api.onrender.com/docs** |
| 💻 **Source Code** | **https://github.com/vs-learner-chhavi/recoverops-ai** |

### 🚀 Try the Demo

**[Open RecoverOps AI →](https://recoverops-ai.vercel.app)**

The live dashboard lets you explore recovery metrics, failed-payment activity, XAI diagnostics, intervention analytics, payment simulations, and the complete audit trail.

---

## 📌 Overview

**RecoverOps AI** is an autonomous revenue recovery platform designed to help e-commerce businesses recover revenue lost because of failed payments.

Instead of blindly retrying failed transactions, the system combines **machine learning, explainable AI, adaptive intervention strategies, and deterministic safety policies** to decide what should happen next — and whether an action is safe to execute.

The result is a real-time **Recovery Command Center** for monitoring failed payments, diagnosing root causes, simulating recovery scenarios, measuring intervention performance, and auditing every important decision.

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
Measure & Learn
```

---

## 🎯 Problem

Failed payments create avoidable revenue leakage for online merchants. Traditional recovery systems often rely on fixed retry schedules and generic customer notifications.

This leads to:

- ❌ Inefficient recovery strategies
- ❌ Customer fatigue from unnecessary outreach
- ❌ Higher gateway and operational costs
- ❌ Limited explainability
- ❌ Unsafe or excessive automation
- ❌ Poor end-to-end observability

RecoverOps AI addresses these gaps through an intelligent, explainable, and policy-controlled recovery loop.

---

## 💡 Solution

RecoverOps AI transforms payment recovery into a **closed-loop decision system**:

1. **Ingest** failed payment events through Razorpay webhooks.
2. **Diagnose** likely root causes using ML and XAI.
3. **Predict** recovery potential.
4. **Select** an intervention using adaptive decision logic.
5. **Validate** the action through a deterministic Policy Gate.
6. **Execute** approved recovery actions in Razorpay Test Mode.
7. **Verify** the outcome and prevent duplicate actions.
8. **Audit** the complete decision trail.
9. **Measure** recovery performance and ROI.

---

## ✨ Key Features

### 🧠 Explainable AI
- XGBoost-based recovery prediction
- SHAP feature attribution when the trained model is available
- Fallback feature attribution for simulated/demo scenarios
- Root-cause diagnosis
- Positive and negative recovery factors

### 🎯 Adaptive Intervention Engine
- Multi-Armed Bandit strategy
- Dynamic intervention selection
- Intervention effectiveness tracking
- Data-driven recovery optimization

### 🛡️ Policy-First Safety Layer
- DND-hour protection
- Per-payment retry limits
- Customer contact limits
- Cost caps
- Minimum confidence thresholds
- Fraud transactions are never retried
- Idempotency protection

### ⚡ Autonomous Recovery
Execute approved interventions through Razorpay Test Mode while keeping actions bounded and auditable.

### 📊 Recovery Command Center
- Revenue at risk
- Revenue recovered
- Active recovery pipeline
- ROI multiplier
- Live recovery feed
- Failure distribution
- Intervention effectiveness
- XAI breakdowns
- Payment recovery simulator
- Audit trail

---

## 🏗️ Architecture

```text
                    Razorpay Webhook
                           │
                           ▼
                    Event Ingestion
                           │
                           ▼
                  XAI / ML Diagnosis
                    XGBoost + SHAP
                           │
                           ▼
                 Recovery Prediction
                           │
                           ▼
                Intervention Selection
                 Multi-Armed Bandit
                           │
                           ▼
                     Policy Gate
                  Safety + Constraints
                     │         │
                   BLOCK      ALLOW
                     │         │
                     ▼         ▼
                  Audit    Intervention
                              │
                              ▼
                        Razorpay API
                          Test Mode
                              │
                              ▼
                         Verification
                              │
                              ▼
                       Audit + Metrics
                              │
                              ▼
                   Recovery Command Center
```

---

## 🔄 How It Works

**1. Ingestion** → Failed payment events are normalized into a consistent transaction format.

**2. Diagnosis** → ML/XAI signals identify likely failure causes and recovery factors.

**3. Prediction** → The system estimates recovery potential.

**4. Intervention** → The decision layer selects an appropriate recovery strategy.

**5. Policy validation** → Deterministic rules decide whether the proposed action is allowed.

**6. Execution** → Approved actions are executed with bounded controls and idempotency protection.

**7. Verification** → Outcomes are recorded and surfaced in the dashboard.

**8. Audit & measurement** → Decisions, interventions, and performance remain observable.

---

## 📊 Evaluation Results

| Metric | Result |
|---|---:|
| Recovery Rate | **34.8%** |
| Precision | **0.912** |
| Recall | **0.847** |
| F1 Score | **0.878** |
| False Positive Rate | **0.031** |
| ROI Multiplier | **127×** |

> These figures represent the project's current evaluation/test setup and are not production guarantees.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript |
| UI | Tailwind CSS, Framer Motion, Lucide React |
| Charts | Recharts |
| Backend | Python, FastAPI |
| Database | SQLite / PostgreSQL target |
| ML | XGBoost, Scikit-Learn |
| Explainability | SHAP |
| Payments | Razorpay Python SDK — Test Mode |
| Data | Pandas, NumPy, Joblib |
| Scheduling | APScheduler |
| AI/LLM | OpenAI, LangChain / LangChain OpenAI |

---

## 📁 Project Structure

```text
recoverops-ai/
├── backend/
│   ├── app/                  # FastAPI application and API routes
│   ├── data/                 # Data generation and datasets
│   ├── ml/                   # Training, prediction and XAI
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app and global styles
│   │   ├── components/       # Dashboard components
│   │   ├── hooks/            # React hooks
│   │   ├── lib/              # API helpers and utilities
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
│
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Razorpay Test Mode credentials for payment integration

### Clone

```bash
git clone https://github.com/vs-learner-chhavi/recoverops-ai.git
cd recoverops-ai
```

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure the required credentials.

Prepare data/model locally when required:

```bash
python -m data.generator
python -m ml.train_model
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Local dashboard: `http://localhost:3000`  
Local API: `http://localhost:8000`  
Local API docs: `http://localhost:8000/docs`

---

## 🔐 Environment Variables

Configure secrets through environment variables rather than committing them to Git.

| Variable | Purpose |
|---|---|
| `RAZORPAY_KEY_ID` | Razorpay Test Mode key ID |
| `RAZORPAY_KEY_SECRET` | Razorpay Test Mode secret |
| `RAZORPAY_WEBHOOK_SECRET` | Webhook verification secret |
| `DATABASE_URL` | Database connection string |
| `OPENAI_API_KEY` | Optional LLM functionality |
| `HOST` | Backend host |
| `PORT` | Backend port |
| `DEBUG` | Debug configuration |
| `MAX_RETRIES_PER_PAYMENT` | Retry limit |
| `MAX_CONTACT_ATTEMPTS` | Contact limit |
| `DND_START_HOUR` / `DND_END_HOUR` | DND window |
| `COST_CAP_PERCENTAGE` | Recovery cost cap |
| `MIN_CONFIDENCE_THRESHOLD` | Minimum confidence for policy approval |

> ⚠️ **Never commit API keys, webhook secrets, database credentials, or other production secrets to Git.**

---

## 🖥️ Dashboard

The frontend is designed as an operational **Recovery Command Center**, not a static analytics page.

### Main sections

- **Overview** — recovery KPIs and revenue metrics
- **Recovery Activity** — live failed-payment feed with filtering
- **XAI Breakdown** — diagnosis and recovery factors
- **Analytics** — failure distribution and intervention effectiveness
- **Simulator** — generate controlled payment-failure scenarios
- **Audit Trail** — inspect decisions and system events

---

## 🔮 Roadmap

- [ ] Production-grade event streaming and queue infrastructure
- [ ] Merchant-specific recovery policies
- [ ] Online learning for intervention optimization
- [ ] Advanced fraud/risk signals
- [ ] Multi-merchant tenancy and RBAC
- [ ] Model monitoring and drift detection
- [ ] Additional payment-provider integrations
- [ ] Production observability and alerting
- [ ] Expanded automated testing and CI/CD

---

## 🛡️ Prototype Disclaimer

RecoverOps AI is a **buildathon/prototype project**. It is not presented as production-ready financial infrastructure and should not be treated as a substitute for merchant, payment-network, legal, security, or compliance review.

Payment integrations are intended for **Razorpay Test Mode** during the prototype/demo.

---

## 🤝 Contributing

Contributions and feedback are welcome.

```bash
git checkout -b feature/your-feature
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

---

## 👩‍💻 Built With

**Python • FastAPI • Next.js • TypeScript • XGBoost • SHAP • Razorpay • Tailwind CSS • Recharts • Framer Motion**

<p align="center"><strong>Recover smarter. Recover safely. RecoverOps AI.</strong></p>
