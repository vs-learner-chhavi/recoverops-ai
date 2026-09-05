"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Transaction } from "@/types";
import { formatCurrency, formatTime, cn } from "@/lib/utils";
import StatusBadge from "./StatusBadge";
import XAIBreakdown from "./XAIBreakdown";
import { ChevronRight, CreditCard, Smartphone, Globe, Wallet, Activity, Filter } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function RecoveryFeed(): React.JSX.Element {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async (): Promise<void> => {
    try {
      const data = await api.getTransactions(filter || undefined, 50);
      setTransactions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const getMethodIcon = (method: string | null): React.JSX.Element => {
    switch (method) {
      case "upi": return <Smartphone className="h-4 w-4" />;
      case "netbanking": return <Globe className="h-4 w-4" />;
      case "wallet": return <Wallet className="h-4 w-4" />;
      default: return <CreditCard className="h-4 w-4" />;
    }
  };

  const filters = [
    { label: "All", value: "" },
    { label: "Failed", value: "failed" },
    { label: "Recovering", value: "recovering" },
    { label: "Recovered", value: "recovered" },
    { label: "Escalated", value: "escalated" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.55 }}
      className="glass overflow-hidden rounded-2xl"
    >
      <div className="border-b border-[var(--border)] bg-white/[0.015] px-4 py-4 sm:px-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-emerald-500/20 bg-emerald-500/10">
              <Activity className="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Live Recovery Feed</h3>
                <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/15 bg-emerald-500/5 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-emerald-400">
                  <motion.span animate={{ scale: [1, 1.5, 1] }} transition={{ duration: 1.8, repeat: Infinity }} className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  Live
                </span>
              </div>
              <p className="mt-0.5 text-[11px] text-zinc-500">AI decisions and payment recovery activity</p>
            </div>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-0.5">
            <Filter className="h-3.5 w-3.5 shrink-0 text-zinc-600" />
            {filters.map((f) => (
              <motion.button
                key={f.value}
                type="button"
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => setFilter(f.value)}
                className={cn(
                  "shrink-0 rounded-full border px-3 py-1.5 text-[10px] font-medium transition-all",
                  filter === f.value
                    ? "border-indigo-400/30 bg-indigo-500/15 text-indigo-200 shadow-sm shadow-indigo-500/10"
                    : "border-transparent text-zinc-500 hover:border-[var(--border)] hover:bg-white/[0.03] hover:text-zinc-300"
                )}
              >
                {f.label}
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-h-[600px] overflow-y-auto">
        {loading ? (
          <div className="space-y-2 p-4">
            {[1, 2, 3, 4].map((i) => <div key={i} className="h-16 animate-pulse rounded-xl bg-white/[0.025]" />)}
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl border border-[var(--border)] bg-white/[0.025]">
              <Activity className="h-5 w-5 text-zinc-600" />
            </div>
            <p className="text-sm font-medium text-zinc-300">No transactions yet</p>
            <p className="mt-1 max-w-xs text-xs text-zinc-600">Use the simulator to trigger a payment failure and watch the AI recovery pipeline.</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {transactions.map((tx, idx) => (
              <motion.div
                key={tx.id}
                layout
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.25, delay: Math.min(idx * 0.018, 0.25) }}
                className="border-b border-[var(--border)] last:border-b-0"
              >
                <motion.button
                  type="button"
                  whileHover={{ backgroundColor: "rgba(255,255,255,0.025)" }}
                  onClick={() => setExpandedId(expandedId === tx.id ? null : tx.id)}
                  className="group flex w-full items-center gap-3 px-4 py-4 text-left sm:gap-4 sm:px-5"
                >
                  <div className={cn(
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border transition-colors",
                    expandedId === tx.id ? "border-indigo-500/30 bg-indigo-500/10 text-indigo-300" : "border-[var(--border)] bg-white/[0.02] text-zinc-500 group-hover:text-zinc-300"
                  )}>
                    <motion.div animate={{ rotate: expandedId === tx.id ? 90 : 0 }} transition={{ duration: 0.2 }}>
                      <ChevronRight className="h-4 w-4" />
                    </motion.div>
                  </div>

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white/[0.025] text-zinc-500">
                    {getMethodIcon(tx.payment_method)}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex min-w-0 items-center gap-2">
                      <span className="truncate text-sm font-medium text-white">{tx.razorpay_payment_id}</span>
                      <StatusBadge status={tx.status} />
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
                      <span className="text-[11px] capitalize text-zinc-500">{tx.failure_category ? tx.failure_category.replace(/_/g, " ") : "unknown"}</span>
                      {tx.recovery_probability !== null && (
                        <span className="text-[11px] text-zinc-600">
                          Recovery <span className={cn("font-semibold", (tx.recovery_probability || 0) > 0.6 ? "text-emerald-400" : (tx.recovery_probability || 0) > 0.3 ? "text-amber-400" : "text-red-400")}>{((tx.recovery_probability || 0) * 100).toFixed(0)}%</span>
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="hidden text-right sm:block">
                    <p className="text-sm font-semibold text-white">{formatCurrency(tx.amount)}</p>
                    <p className="mt-1 text-[10px] text-zinc-600">{formatTime(tx.failed_at)}</p>
                  </div>
                </motion.button>

                <AnimatePresence initial={false}>
                  {expandedId === tx.id && tx.xai_explanation && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden border-t border-[var(--border)] bg-black/10"
                    >
                      <div className="px-4 py-4 sm:px-6 sm:py-5">
                        <XAIBreakdown explanation={tx.xai_explanation} />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  );
}
