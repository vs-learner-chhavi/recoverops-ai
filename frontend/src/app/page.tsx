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
import { TrendingDown, TrendingUp, Activity, Target, ArrowDown } from "lucide-react";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetricsType | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try { setMetrics(await api.getDashboardMetrics()); } catch (err) { console.error(err); }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="pointer-events-none fixed inset-0 -z-10"><div className="grid-bg absolute inset-0" /><div className="absolute -top-56 left-1/2 h-[32rem] w-[32rem] -translate-x-1/2 rounded-full bg-indigo-500/[.07] blur-3xl" /></div>
      <Navbar />

      <main className="relative mx-auto max-w-[1440px] px-5 py-8 lg:px-7 lg:py-12">
        <section id="overview" className="section-shell mb-10">
          <motion.div initial={{ opacity:0, y:18 }} animate={{ opacity:1, y:0 }} transition={{ duration:.6 }} className="max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-400/15 bg-indigo-400/[.06] px-3 py-1.5 text-[11px] font-medium text-indigo-300"><span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />AI-POWERED REVENUE OPERATIONS</div>
            <h2 className="text-4xl font-bold tracking-tight sm:text-5xl"><span className="gradient-text">RecoverOps AI</span><br /><span className="text-white">Recovery Command Center</span></h2>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base">Real-time visibility into failed payments, intelligent recovery interventions, and explainable AI decisions — all in one operational workspace.</p>
            <motion.a href="#recovery" whileHover={{ y:-2 }} className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-black shadow-xl shadow-white/5">Explore recovery activity <ArrowDown className="h-4 w-4" /></motion.a>
          </motion.div>
        </section>

        <section className="section-shell" aria-label="Key metrics">
          <div className="mb-4 flex items-end justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.18em] text-zinc-500">Live intelligence</p><h3 className="mt-1 text-xl font-semibold">Performance overview</h3></div><span className="text-[11px] text-zinc-600">Auto-refresh · 5s</span></div>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
            <MotionMetricCard title="Revenue at Risk" value={metrics ? formatCurrency(metrics.total_failed_revenue) : "—"} subtitle={metrics ? `${metrics.total_transactions} transactions` : ""} icon={TrendingDown} glowClass="glow-red" index={0} />
            <MotionMetricCard title="Revenue Recovered" value={metrics ? formatCurrency(metrics.total_recovered_revenue) : "—"} subtitle={metrics ? `${metrics.recovery_rate.toFixed(1)}% recovery rate` : ""} icon={TrendingUp} trend={metrics ? `↑ ${metrics.recovery_rate.toFixed(1)}%` : undefined} trendUp glowClass="glow-green" index={1} />
            <MotionMetricCard title="Active Pipeline" value={metrics ? String(metrics.active_recoveries) : "—"} subtitle={`${metrics?.interventions_executed || 0} interventions`} icon={Activity} glowClass="glow-blue" index={2} />
            <MotionMetricCard title="ROI Multiplier" value={metrics?.roi_multiplier ? `${metrics.roi_multiplier.toFixed(0)}x` : "—"} subtitle={`${metrics?.policy_blocks || 0} policy blocks`} icon={Target} glowClass="glow-amber" index={3} />
          </div>
        </section>

        <section id="recovery" className="section-shell mt-10 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2"><RecoveryFeed /><RecoveryChart /></div>
          <div className="space-y-6"><div id="simulator" className="section-shell"><Simulator /></div><div id="audit" className="section-shell"><AuditLog /></div></div>
        </section>

        <motion.footer initial={{ opacity:0 }} whileInView={{ opacity:1 }} viewport={{ once:true }} transition={{ duration:.6 }} className="mt-16 border-t border-white/[.06] py-8 text-center text-xs text-zinc-600">Built for Razorpay AI Buildathon 2026 · Powered by XGBoost + SHAP · Fully Explainable</motion.footer>
      </main>
    </div>
  );
}
