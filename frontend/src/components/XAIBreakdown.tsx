"use client";

import { XAIExplanation } from "@/types";
import { cn, getUrgencyColor } from "@/lib/utils";
import {
  Brain, TrendingUp, TrendingDown, AlertTriangle, Clock,
} from "lucide-react";
import { motion } from "framer-motion";

interface XAIBreakdownProps {
  explanation: XAIExplanation;
}

export default function XAIBreakdown({ explanation }: XAIBreakdownProps) {
  const { summary, diagnosis, top_positive_factors, top_negative_factors } = explanation;

  const maxMagnitude = Math.max(
    ...[...top_positive_factors, ...top_negative_factors].map(f => f.magnitude || 0),
    0.1
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      {/* AI Summary */}
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex items-start gap-3 rounded-lg bg-indigo-500/5 border border-indigo-500/20 p-3"
      >
        <motion.div
          animate={{ rotate: [0, 10, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <Brain className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
        </motion.div>
        <div>
          <p className="text-xs font-semibold text-indigo-300 mb-1">
            AI Diagnosis
          </p>
          <p className="text-xs text-zinc-300 leading-relaxed">{summary}</p>
        </div>
      </motion.div>

      {/* Diagnosis Details */}
      {diagnosis && (
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Root Cause", value: diagnosis.root_cause, icon: null },
            { label: "Recommended Action", value: diagnosis.recommended_action, icon: null },
            {
              label: "Urgency",
              value: diagnosis.urgency,
              icon: <AlertTriangle className={cn("h-3 w-3", getUrgencyColor(diagnosis.urgency))} />,
              highlight: getUrgencyColor(diagnosis.urgency),
            },
            {
              label: "Retry Window",
              value: diagnosis.retry_window,
              icon: <Clock className="h-3 w-3 text-zinc-500" />,
            },
          ].map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.05 }}
              className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-3"
            >
              <div className="flex items-center gap-1.5">
                {item.icon}
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">
                  {item.label}
                </p>
              </div>
              <p className={cn(
                "text-xs mt-1 capitalize",
                item.highlight || "text-zinc-300"
              )}>
                {item.value}
              </p>
            </motion.div>
          ))}
        </div>
      )}

      {/* SHAP Feature Contributions */}
      <div className="grid grid-cols-2 gap-3">
        {top_positive_factors.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1.5">
              <TrendingUp className="h-3 w-3 text-emerald-400" />
              <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
                Recovery Factors
              </p>
            </div>
            {top_positive_factors.map((f, i) => {
              const widthPercent = (f.magnitude / maxMagnitude) * 100;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.08 }}
                  className="relative rounded-md bg-emerald-500/5 border border-emerald-500/10 px-2.5 py-1.5 overflow-hidden"
                >
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${widthPercent}%` }}
                    transition={{ duration: 0.7, delay: 0.4 + i * 0.08, ease: "easeOut" }}
                    className="absolute inset-y-0 left-0 bg-emerald-500/10"
                  />
                  <div className="relative flex items-center justify-between">
                    <span className="text-[11px] text-zinc-300 capitalize">
                      {f.feature.replace(/_/g, " ")}
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400 font-semibold">
                      +{f.shap_value.toFixed(3)}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {top_negative_factors.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1.5">
              <TrendingDown className="h-3 w-3 text-red-400" />
              <p className="text-[10px] font-semibold uppercase tracking-wider text-red-400">
                Risk Factors
              </p>
            </div>
            {top_negative_factors.map((f, i) => {
              const widthPercent = (f.magnitude / maxMagnitude) * 100;
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.08 }}
                  className="relative rounded-md bg-red-500/5 border border-red-500/10 px-2.5 py-1.5 overflow-hidden"
                >
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${widthPercent}%` }}
                    transition={{ duration: 0.7, delay: 0.4 + i * 0.08, ease: "easeOut" }}
                    className="absolute inset-y-0 left-0 bg-red-500/10"
                  />
                  <div className="relative flex items-center justify-between">
                    <span className="text-[11px] text-zinc-300 capitalize">
                      {f.feature.replace(/_/g, " ")}
                    </span>
                    <span className="text-[11px] font-mono text-red-400 font-semibold">
                      {f.shap_value.toFixed(3)}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}