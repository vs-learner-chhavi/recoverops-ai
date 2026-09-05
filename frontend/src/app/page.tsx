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
import { TrendingDown, TrendingUp, Activity, Target, ArrowDown, Zap, ShieldCheck } from "lucide-react";
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
      <div className="pointer-events-none fixed inset-0 -z-10"><div className="grid-bg absolute inset-0" /><div className="absolute -top-56 left-1/2 h-[32rem] w-[32rem] -translate-x-1/2 rounded-full bg-indigo-500/[.07] blur-3xl" /><div className="absolute right-[-12rem] top-[40rem] h-[26rem] w-[26rem] rounded-full bg-cyan-500/[.035] blur-3xl" /></div>
      <Navbar />

      <main className="relative mx-auto max-w-[1480px] px-4 py-7 sm:px-5 lg:px-7 lg:py-10">
        <section id="overview" className="section-shell mb-9">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <motion.div initial={{ opacity:0, y:18 }} animate={{ opacity:1, y:0 }} transition={{ duration:.6 }} className="max-w-3xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-400/15 bg-indigo-400/[.06] px-3 py-1.5 text-[10px] font-semibold tracking-wide text-indigo-300"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-indigo-400" />AI-POWERED REVENUE OPERATIONS</div>
              <h2 className="text-4xl font-bold tracking-[-.035em] sm:text-5xl lg:text-[3.35rem]"><span className="gradient-text">RecoverOps AI</span><br /><span className="text-white">Recovery Command Center</span></h2>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-[15px]">Real-time visibility into failed payments, intelligent recovery interventions, and explainable AI decisions — all in one operational workspace.</p>
              <motion.a href="#recovery" whileHover={{ y:-2 }} className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-black shadow-xl shadow-white/5">Explore recovery activity <ArrowDown className="h-4 w-4" /></motion.a>
            </motion.div>
            <motion.div initial={{ opacity:0, x:15 }} animate={{ opacity:1, x:0 }} transition={{ duration:.6, delay:.15 }} className="hidden items-center gap-2 rounded-2xl border border-white/[.06] bg-[#0d0f16]/70 px-3 py-2.5 backdrop-blur-xl xl:flex"><span className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-400/10 text-emerald-300"><ShieldCheck className="h-4 w-4" /></span><div><p className="text-[9px] uppercase tracking-[.15em] text-zinc-600">Protection layer</p><p className="text-[11px] font-medium text-zinc-300">AI + Policy controls active</p></div><span className="ml-2 h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" /></motion.div>
          </div>
        </section>

        <section className="section-shell" aria-label="Key metrics">
          <div className="mb-4 flex items-end justify-between"><div><div className="flex items-center gap-2"><Zap className="h-3.5 w-3.5 text-indigo-300" /><p className="text-xs font-semibold uppercase tracking-[.18em] text-zinc-500">Live intelligence</p></div><h3 className="mt-1 text-xl font-semibold text-white">Performance overview</h3></div><span className="rounded-full border border-white/[.05] bg-white/[.02] px-2.5 py-1 text-[10px] text-zinc-500">Auto-refresh · 5s</span></div>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
            <MotionMetricCard title="Revenue at Risk" value={metrics ? formatCurrency(metrics.total_failed_revenue) : "—"} subtitle={metrics ? `${metrics.total_transactions} transactions` : ""} icon={TrendingDown} glowClass="glow-red" index={0} />
            <MotionMetricCard title="Revenue Recovered" value={metrics ? formatCurrency(metrics.total_recovered_revenue) : "—"} subtitle={metrics ? `${metrics.recovery_rate.toFixed(1)}% recovery rate` : ""} icon={TrendingUp} trend={metrics ? `↑ ${metrics.recovery_rate.toFixed(1)}%` : undefined} trendUp glowClass="glow-green" index={1} />
            <MotionMetricCard title="Active Pipeline" value={metrics ? String(metrics.active_recoveries) : "—"} subtitle={`${metrics?.interventions_executed || 0} interventions`} icon={Activity} glowClass="glow-blue" index={2} />
            <MotionMetricCard title="ROI Multiplier" value={metrics?.roi_multiplier ? `${metrics.roi_multiplier.toFixed(0)}x` : "—"} subtitle={`${metrics?.policy_blocks || 0} policy blocks`} icon={Target} glowClass="glow-amber" index={3} />
          </div>
        </section>

        <section id="recovery" className="section-shell mt-8 space-y-5">
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1fr)_350px]">
            <RecoveryFeed />
            <div id="simulator" className="section-shell"><Simulator /></div>
          </div>

          <div className="flex items-center justify-between border-t border-white/[.05] pt-6">
            <div><div className="flex items-center gap-2"><Activity className="h-4 w-4 text-violet-300" /><h3 className="text-sm font-semibold text-white">Recovery analytics</h3></div><p className="mt-1 text-[10px] text-zinc-500">Failure patterns and intervention performance at a glance</p></div>
            <span className="hidden rounded-full border border-white/[.05] bg-white/[.02] px-2.5 py-1 text-[9px] uppercase tracking-wider text-zinc-500 sm:block">Live telemetry</span>
          </div>
          <RecoveryChart />

          <div id="audit" className="section-shell pt-2">
            <div className="mb-4 flex items-center justify-between"><div><div className="flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-cyan-300" /><h3 className="text-sm font-semibold text-white">Decision intelligence</h3></div><p className="mt-1 text-[10px] text-zinc-500">Traceable AI decisions, policy gates and recovery actions</p></div><span className="hidden text-[9px] uppercase tracking-[.16em] text-zinc-600 sm:block">Immutable operational trail</span></div>
            <AuditLog />
          </div>
        </section>

        <motion.footer initial={{ opacity:0 }} whileInView={{ opacity:1 }} viewport={{ once:true }} transition={{ duration:.6 }} className="mt-14 py-8 text-center text-xs text-zinc-600"><span>© 2026 RecoverOps AI</span><span className="mx-2 text-zinc-800">·</span><span>Built for the Razorpay AI Buildathon</span></motion.footer>
      </main>
    </div>
  );
}
