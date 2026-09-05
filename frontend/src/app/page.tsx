"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DashboardMetrics as DashboardMetricsType } from "@/types";
import { formatCurrency } from "@/lib/utils";
import Navbar from "@/components/Navbar";
import MotionMetricCard from "@/components/MotionMetricCard";
import RecoveryFeed from "@/components/RecoveryFeed";
import RecoveryChart from "@/components/RecoveryChart";
import AuditLog from "@/components/AuditLog";
import Simulator from "@/components/Simulator";
import {
  TrendingDown, TrendingUp, Activity, Target,
} from "lucide-react";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetricsType | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await api.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--background)] relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 h-96 w-96 bg-indigo-500/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-40 h-96 w-96 bg-emerald-500/5 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="relative mx-auto max-w-[1440px] px-6 py-6 space-y-6">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-bold text-white">Recovery Dashboard</h2>
          <p className="text-sm text-zinc-500 mt-1">
            Real-time AI-driven payment recovery pipeline
          </p>
        </motion.div>

        {/* Primary Metric Cards — 4 clean cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MotionMetricCard
            title="Revenue at Risk"
            value={metrics ? formatCurrency(metrics.total_failed_revenue) : "—"}
            subtitle={metrics ? `${metrics.total_transactions} transactions` : ""}
            icon={TrendingDown}
            glowClass="glow-red"
            index={0}
          />
          <MotionMetricCard
            title="Revenue Recovered"
            value={metrics ? formatCurrency(metrics.total_recovered_revenue) : "—"}
            subtitle={
              metrics
                ? `${metrics.recovery_rate.toFixed(1)}% recovery rate`
                : ""
            }
            icon={TrendingUp}
            trend={metrics ? `↑ ${metrics.recovery_rate.toFixed(1)}%` : undefined}
            trendUp
            glowClass="glow-green"
            index={1}
          />
          <MotionMetricCard
            title="Active Pipeline"
            value={metrics ? String(metrics.active_recoveries) : "—"}
            subtitle={`${metrics?.interventions_executed || 0} interventions`}
            icon={Activity}
            glowClass="glow-blue"
            index={2}
          />
          <MotionMetricCard
            title="ROI Multiplier"
            value={
              metrics?.roi_multiplier
                ? `${metrics.roi_multiplier.toFixed(0)}x`
                : "—"
            }
            subtitle={`${metrics?.policy_blocks || 0} policy blocks`}
            icon={Target}
            glowClass="glow-amber"
            index={3}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: Feed + Charts */}
          <div className="lg:col-span-2 space-y-6">
            <RecoveryFeed />
            <RecoveryChart />
          </div>

          {/* Right column: Simulator + Audit */}
          <div className="space-y-6">
            <Simulator />
            <AuditLog />
          </div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center py-6 text-xs text-zinc-600"
        >
          Built for Razorpay AI Buildathon 2026 · Powered by XGBoost + SHAP · Fully Explainable
        </motion.footer>
      </main>
    </div>
  );
}