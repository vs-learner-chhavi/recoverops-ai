"use client";

import { XAIExplanation } from "@/types";
import { cn, getUrgencyColor } from "@/lib/utils";
import { Brain, TrendingUp, TrendingDown, AlertTriangle, Clock, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

interface XAIBreakdownProps { explanation: XAIExplanation; }

export default function XAIBreakdown({ explanation }: XAIBreakdownProps) {
  const { summary, diagnosis, top_positive_factors, top_negative_factors } = explanation;
  const maxMagnitude = Math.max(...[...top_positive_factors, ...top_negative_factors].map(f => f.magnitude || 0), 0.1);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
      <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/[0.08] via-purple-500/[0.03] to-transparent p-4">
        <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-indigo-500/10 blur-2xl" />
        <div className="relative flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-indigo-400/20 bg-indigo-500/10">
            <Brain className="h-4 w-4 text-indigo-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <p className="text-xs font-semibold text-indigo-200">AI Diagnosis</p>
              <Sparkles className="h-3 w-3 text-indigo-400" />
            </div>
            <p className="mt-1.5 text-xs leading-relaxed text-zinc-300">{summary}</p>
          </div>
        </div>
      </div>

      {diagnosis && (
        <div className="grid grid-cols-2 gap-2.5 lg:grid-cols-4">
          {[
            { label: "Root Cause", value: diagnosis.root_cause },
            { label: "Action", value: diagnosis.recommended_action },
            { label: "Urgency", value: diagnosis.urgency, icon: <AlertTriangle className={cn("h-3 w-3", getUrgencyColor(diagnosis.urgency))} /> },
            { label: "Retry Window", value: diagnosis.retry_window, icon: <Clock className="h-3 w-3 text-zinc-500" /> },
          ].map((item, i) => (
            <motion.div key={item.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="rounded-xl border border-[var(--border)] bg-white/[0.02] p-3">
              <div className="flex items-center gap-1.5">{item.icon}<p className="text-[9px] font-semibold uppercase tracking-wider text-zinc-600">{item.label}</p></div>
              <p className={cn("mt-1.5 truncate text-[11px] capitalize", item.label === "Urgency" ? getUrgencyColor(diagnosis.urgency) : "text-zinc-300")}>{item.value}</p>
            </motion.div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {top_positive_factors.length > 0 && (
          <div className="rounded-xl border border-emerald-500/10 bg-emerald-500/[0.025] p-3">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-1.5"><TrendingUp className="h-3.5 w-3.5 text-emerald-400" /><p className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Recovery Factors</p></div>
              <span className="text-[9px] text-zinc-600">SHAP</span>
            </div>
            <div className="space-y-2">
              {top_positive_factors.map((f, i) => {
                const widthPercent = (f.magnitude / maxMagnitude) * 100;
                return <motion.div key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 + i * 0.06 }} className="relative overflow-hidden rounded-lg border border-emerald-500/10 bg-black/10 px-2.5 py-2">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${widthPercent}%` }} transition={{ duration: 0.7, delay: 0.2 + i * 0.06 }} className="absolute inset-y-0 left-0 bg-emerald-500/[0.09]" />
                  <div className="relative flex items-center justify-between gap-2"><span className="truncate text-[11px] capitalize text-zinc-300">{f.feature.replace(/_/g, " ")}</span><span className="font-mono text-[10px] font-semibold text-emerald-400">+{f.shap_value.toFixed(3)}</span></div>
                </motion.div>;
              })}
            </div>
          </div>
        )}

        {top_negative_factors.length > 0 && (
          <div className="rounded-xl border border-red-500/10 bg-red-500/[0.025] p-3">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-1.5"><TrendingDown className="h-3.5 w-3.5 text-red-400" /><p className="text-[10px] font-bold uppercase tracking-wider text-red-400">Risk Factors</p></div>
              <span className="text-[9px] text-zinc-600">SHAP</span>
            </div>
            <div className="space-y-2">
              {top_negative_factors.map((f, i) => {
                const widthPercent = (f.magnitude / maxMagnitude) * 100;
                return <motion.div key={i} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 + i * 0.06 }} className="relative overflow-hidden rounded-lg border border-red-500/10 bg-black/10 px-2.5 py-2">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${widthPercent}%` }} transition={{ duration: 0.7, delay: 0.2 + i * 0.06 }} className="absolute inset-y-0 left-0 bg-red-500/[0.09]" />
                  <div className="relative flex items-center justify-between gap-2"><span className="truncate text-[11px] capitalize text-zinc-300">{f.feature.replace(/_/g, " ")}</span><span className="font-mono text-[10px] font-semibold text-red-400">{f.shap_value.toFixed(3)}</span></div>
                </motion.div>;
              })}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
