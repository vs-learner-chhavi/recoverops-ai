"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import { FailureBreakdown, InterventionEffectiveness } from "@/types";
import { formatCurrency } from "@/lib/utils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { BarChart3, PieChart as PieIcon, RefreshCw, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const COLORS = ["#818cf8", "#a78bfa", "#f472b6", "#f59e0b", "#34d399", "#38bdf8", "#fb7185", "#2dd4bf"];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="min-w-[150px] rounded-xl border border-white/10 bg-[#11131d]/95 px-3 py-2.5 shadow-2xl backdrop-blur-xl">
      {label && <p className="mb-1.5 text-[10px] font-medium capitalize text-zinc-400">{String(label).replace(/_/g, " ")}</p>}
      {payload.map((item: any, index: number) => (
        <div key={`${item.dataKey}-${index}`} className="flex items-center justify-between gap-5 text-[11px]">
          <span className="text-zinc-400">{item.name || "Value"}</span>
          <span className="font-mono font-semibold text-white">
            {typeof item.value === "number" ? `${item.value.toFixed(1)}%` : item.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function PieTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="rounded-xl border border-white/10 bg-[#11131d]/95 px-3 py-2.5 shadow-2xl backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 rounded-full" style={{ background: item.payload?.fill || "#818cf8" }} />
        <span className="text-[11px] capitalize text-zinc-300">{String(item.name || "unknown").replace(/_/g, " ")}</span>
      </div>
      <p className="mt-1 font-mono text-sm font-semibold text-white">{item.value} <span className="text-[10px] font-normal text-zinc-500">transactions</span></p>
    </div>
  );
}

export default function RecoveryChart() {
  const [failureData, setFailureData] = useState<FailureBreakdown[]>([]);
  const [interventionData, setInterventionData] = useState<InterventionEffectiveness[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    setRefreshing(true);
    try {
      const [fd, id] = await Promise.all([api.getFailureBreakdown(), api.getInterventionEffectiveness()]);
      setFailureData(fd);
      setInterventionData(id);
    } catch (err) {
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const totalFailures = useMemo(() => failureData.reduce((sum, item) => sum + item.count, 0), [failureData]);
  const bestIntervention = useMemo(
    () => interventionData.reduce<InterventionEffectiveness | null>((best, item) => !best || item.success_rate > best.success_rate ? item : best, null),
    [interventionData],
  );

  return (
    <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.5 }}
        className="group overflow-hidden rounded-2xl border border-white/[.07] bg-[#0d0f16]/90 p-4 shadow-[0_18px_50px_rgba(0,0,0,.18)] sm:p-5"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-indigo-400/20 bg-indigo-400/10 shadow-lg shadow-indigo-500/5">
              <PieIcon className="h-4 w-4 text-indigo-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Failure Distribution</h3>
                <span className="rounded-full border border-emerald-400/15 bg-emerald-400/10 px-1.5 py-0.5 text-[8px] font-semibold uppercase tracking-wider text-emerald-300">Live</span>
              </div>
              <p className="mt-0.5 text-[10px] text-zinc-500">Where recovery pressure is coming from</p>
            </div>
          </div>
          <span className="hidden rounded-lg border border-white/[.06] bg-white/[.025] px-2 py-1 text-[9px] text-zinc-500 sm:block">10s refresh</span>
        </div>

        <div className="relative mt-1">
          {failureData.length > 0 ? (
            <ResponsiveContainer width="100%" height={230}>
              <PieChart>
                <Pie data={failureData} cx="50%" cy="50%" innerRadius={63} outerRadius={87} paddingAngle={3} dataKey="count" nameKey="category" stroke="none" cornerRadius={4}>
                  {failureData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip content={<PieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-[230px] items-center justify-center text-xs text-zinc-600">No data yet</div>
          )}
          {failureData.length > 0 && (
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-2xl font-semibold tracking-tight text-white">{totalFailures}</span>
              <span className="text-[9px] uppercase tracking-[.16em] text-zinc-500">failed payments</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2 border-t border-white/[.05] pt-3 sm:grid-cols-3">
          {failureData.slice(0, 6).map((f, i) => (
            <div key={f.category} className="flex min-w-0 items-center gap-2 rounded-lg bg-white/[.018] px-2 py-2">
              <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
              <span className="truncate capitalize text-[10px] text-zinc-400">{f.category.replace(/_/g, " ")}</span>
              <span className="ml-auto font-mono text-[10px] font-semibold text-zinc-300">{f.count}</span>
            </div>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.5, delay: 0.08 }}
        className="group overflow-hidden rounded-2xl border border-white/[.07] bg-[#0d0f16]/90 p-4 shadow-[0_18px_50px_rgba(0,0,0,.18)] sm:p-5"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-violet-400/20 bg-violet-400/10 shadow-lg shadow-violet-500/5">
              <BarChart3 className="h-4 w-4 text-violet-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Intervention Effectiveness</h3>
                <Sparkles className="h-3 w-3 text-violet-300" />
              </div>
              <p className="mt-0.5 text-[10px] text-zinc-500">Which actions recover the most value</p>
            </div>
          </div>
          <button onClick={fetchData} aria-label="Refresh analytics" className="rounded-lg border border-white/[.06] bg-white/[.025] p-2 text-zinc-500 transition hover:border-white/10 hover:text-white">
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>

        <div className="mt-2">
          {interventionData.length > 0 ? (
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={interventionData} layout="vertical" margin={{ top: 8, right: 12, bottom: 4, left: 4 }} barCategoryGap="24%">
                <defs>
                  <linearGradient id="recoveryBarGradient" x1="0" x2="1" y1="0" y2="0">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#a78bfa" />
                  </linearGradient>
                </defs>
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9, fill: "#71717a" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="intervention_type" tick={{ fontSize: 9, fill: "#a1a1aa" }} width={94} axisLine={false} tickLine={false} tickFormatter={(v) => String(v).replace(/_/g, " ")} />
                <Tooltip cursor={{ fill: "rgba(255,255,255,.025)" }} content={<ChartTooltip />} />
                <Bar dataKey="success_rate" fill="url(#recoveryBarGradient)" radius={[0, 8, 8, 0]} name="Success rate" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-[230px] items-center justify-center text-xs text-zinc-600">No data yet</div>
          )}
        </div>

        {bestIntervention && (
          <div className="mb-3 flex items-center justify-between rounded-xl border border-emerald-400/10 bg-emerald-400/[.045] px-3 py-2.5">
            <div>
              <p className="text-[9px] uppercase tracking-[.14em] text-zinc-500">Top performer</p>
              <p className="mt-0.5 text-[11px] font-medium capitalize text-zinc-200">{bestIntervention.intervention_type.replace(/_/g, " ")}</p>
            </div>
            <span className="font-mono text-sm font-semibold text-emerald-300">{bestIntervention.success_rate.toFixed(1)}%</span>
          </div>
        )}

        <div className="space-y-2 border-t border-white/[.05] pt-3">
          {interventionData.map((item) => (
            <div key={item.intervention_type} className="flex items-center justify-between gap-3 rounded-lg border border-white/[.045] bg-white/[.018] px-3 py-2">
              <span className="truncate capitalize text-[10px] text-zinc-400">{item.intervention_type.replace(/_/g, " ")}</span>
              <div className="flex shrink-0 items-center gap-3"><span className="text-[10px] font-medium text-emerald-300">{formatCurrency(item.total_recovered)}</span><span className="font-mono text-[9px] text-zinc-500">{item.successful}/{item.total_executed}</span></div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
