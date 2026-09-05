"""
RecoverOps AI — Main FastAPI Application
Autonomous Multi-Tier Revenue Recovery Engine with XAI Diagnostics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.config import get_settings
from app.routes import webhooks_route, dashboard, simulator, audit

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and ML models on startup."""
    print("🚀 RecoverOps AI starting up...")
    await init_db()
    print("✅ Database initialized")

    # Verify Razorpay connection
    print(f"🔑 Razorpay Key: {settings.razorpay_key_id[:12]}...")
    print(f"📊 Policy: max {settings.max_retries_per_payment} retries, "
          f"DND {settings.dnd_start_hour}:00–{settings.dnd_end_hour}:00, "
          f"cost cap {settings.cost_cap_percentage}%")

    yield

    print("👋 RecoverOps AI shutting down...")


app = FastAPI(
    title="RecoverOps AI",
    description=(
        "Autonomous Multi-Tier Revenue Recovery Engine with "
        "Explainable AI Diagnostics — Built for Razorpay AI Buildathon"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(webhooks_route.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "RecoverOps AI",
        "version": "1.0.0",
        "description": "Autonomous Revenue Recovery Engine",
        "status": "operational",
        "endpoints": {
            "dashboard": "/api/dashboard/metrics",
            "transactions": "/api/dashboard/transactions",
            "simulator": "/api/simulator/trigger",
            "batch_simulator": "/api/simulator/batch",
            "webhooks": "/api/webhooks/razorpay",
            "audit": "/api/audit/logs",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "recoverops-ai"}