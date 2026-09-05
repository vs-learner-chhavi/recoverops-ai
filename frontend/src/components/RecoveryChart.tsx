"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FailureBreakdown, InterventionEffectiveness } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { BarChart3, PieChart as PieIcon } from "lucide-react";
import { motion } from "framer-motion";

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6", "#ef4444", "#14b8a6"];

const tooltipStyle = { background: "#101118", border: "1px solid #282a36", borderRadius: "12px", fontSize: "11px", color: "#fff" };

export default function RecoveryChart() {
  const [failureData, setFailureData] = useState<FailureBreakdown[]>([]);
  const [interventionData, setInterventionData] = useState<InterventionEffectiveness[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [fd, id] = await Promise.all([api.getFailureBreakdown(), api.getInterventionEffectiveness()]);
        setFailureData(fd); setInterventionData(id);
      } catch (err) { console.error(err); }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <motion.div initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.5 }} className="glass rounded-2xl p-4 sm:p-5">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl border border-indigo-500/20 bg-indigo-500/10"><PieIcon className="h-4 w-4 text-indigo-300" /></div><div><h3 className="text-sm font-semibold text-white">Failure Distribution</h3><p className="text-[10px] text-zinc-600">Where recovery pressure is coming from</p></div></div>
          <span className="rounded-full border border-[var(--border)] bg-white/[0.02] px-2 py-1 text-[9px] text-zinc-600">LIVE</span>
        </div>
        {failureData.length > 0 ? <ResponsiveContainer width="100%" height={220}><PieChart><Pie data={failureData} cx="50%" cy="50%" innerRadius={58} outerRadius={84} paddingAngle={3} dataKey="count" nameKey="category" stroke="none">{failureData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><Tooltip contentStyle={tooltipStyle} formatter={(value: any, name: string) => [`${value} transactions`, name.replace(/_/g, " ")]} /></PieChart></ResponsiveContainer> : <div className="flex h-[220px] items-center justify-center text-xs text-zinc-600">No data yet</div>}
        <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2">
          {failureData.slice(0, 6).map((f, i) => <div key={f.category} className="flex min-w-0 items-center gap-2 text-[10px]"><span className="h-2 w-2 shrink-0 rounded-full" style={{ background: COLORS[i % COLORS.length] }} /><span className="truncate capitalize text-zinc-500">{f.category.replace(/_/g, " ")}</span><span className="ml-auto font-mono text-zinc-600">{f.count}</span></div>)}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-60px" }} transition={{ duration: 0.5, delay: 0.08 }} className="glass rounded-2xl p-4 sm:p-5">
        <div className="mb-2 flex items-center justify-between"><div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl border border-purple-500/20 bg-purple-500/10"><BarChart3 className="h-4 w-4 text-purple-300" /></div><div><h3 className="text-sm font-semibold text-white">Intervention Effectiveness</h3><p className="text-[10px] text-zinc-600">Which actions recover the most value</p></div></div><span className="rounded-full border border-[var(--border)] bg-white/[0.02] px-2 py-1 text-[9px] text-zinc-600">10s REFRESH</span></div>
        {interventionData.length > 0 ? <ResponsiveContainer width="100%" height={220}><BarChart data={interventionData} layout="vertical" margin={{ left: 0, right: 8 }}><XAxis type="number" tick={{ fontSize: 10, fill: "#71717a" }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="intervention_type" tick={{ fontSize: 9, fill: "#71717a" }} width={100} axisLine={false} tickLine={false} tickFormatter={(v) => v.replace(/_/g, " ")} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="success_rate" fill="#818cf8" radius={[0, 6, 6, 0]} name="Success %" /></BarChart></ResponsiveContainer> : <div className="flex h-[220px] items-center justify-center text-xs text-zinc-600">No data yet</div>}
        <div className="mt-2 space-y-2">
          {interventionData.map((item) => <div key={item.intervention_type} className="flex items-center justify-between gap-3 rounded-lg border border-[var(--border)] bg-white/[0.015] px-2.5 py-2 text-[10px]"><span className="truncate capitalize text-zinc-500">{item.intervention_type.replace(/_/g, " ")}</span><div className="flex shrink-0 items-center gap-3"><span className="text-emerald-400">{formatCurrency(item.total_recovered)}</span><span className="font-mono text-zinc-600">{item.successful}/{item.total_executed}</span></div></div>)}
        </div>
      </motion.div>
    </div>
  );
}
