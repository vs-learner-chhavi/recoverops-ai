"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Transaction } from "@/types";
import { formatCurrency, formatTime, cn } from "@/lib/utils";
import StatusBadge from "./StatusBadge";
import XAIBreakdown from "./XAIBreakdown";
import {
  ChevronDown, ChevronRight, CreditCard, Smartphone, Globe, Wallet,
} from "lucide-react";
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
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const getMethodIcon = (method: string | null): React.JSX.Element => {
    switch (method) {
      case "card": return <CreditCard className="h-4 w-4" />;
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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="rounded-xl border border-[var(--border)] bg-[var(--card)]"
    >
      <div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4">
        <div className="flex items-center gap-2">
          <motion.span
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="h-2 w-2 rounded-full bg-emerald-400"
          />
          <h3 className="text-sm font-semibold text-white">Live Recovery Feed</h3>
        </div>
        <div className="flex gap-1">
          {filters.map((f) => (
            <motion.button
              key={f.value}
              type="button"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setFilter(f.value)}
              className={cn(
                "rounded-md px-2.5 py-1 text-[11px] font-medium transition-colors",
                filter === f.value
                  ? "bg-indigo-600 text-white"
                  : "text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
              )}
            >
              {f.label}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="max-h-[600px] overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12 text-sm text-zinc-500">
            Loading transactions...
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-sm text-zinc-500">
            <p>No transactions yet</p>
            <p className="text-xs mt-1">Use the Simulator to trigger failures</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {transactions.map((tx, idx) => (
              <motion.div
                key={tx.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.25, delay: Math.min(idx * 0.02, 0.3) }}
                className="border-b border-[var(--border)] last:border-b-0"
              >
                <motion.button
                  type="button"
                  whileHover={{ backgroundColor: "rgba(255,255,255,0.02)" }}
                  onClick={() =>
                    setExpandedId(expandedId === tx.id ? null : tx.id)
                  }
                  className="flex w-full items-center gap-4 px-5 py-3.5 text-left"
                >
                  <motion.div
                    animate={{ rotate: expandedId === tx.id ? 90 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronRight className="h-4 w-4 text-zinc-500 shrink-0" />
                  </motion.div>

                  <div className="flex items-center gap-2 text-zinc-400 shrink-0">
                    {getMethodIcon(tx.payment_method)}
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate text-white">
                        {tx.razorpay_payment_id}
                      </span>
                      <StatusBadge status={tx.status} />
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-xs text-zinc-500 capitalize">
                        {tx.failure_category ? tx.failure_category.replace(/_/g, " ") : "unknown"}
                      </span>
                      {tx.recovery_probability !== null && (
                        <span className="text-xs text-zinc-500">
                          Recovery: <span className={cn(
                            "font-semibold",
                            (tx.recovery_probability || 0) > 0.6 ? "text-emerald-400" :
                            (tx.recovery_probability || 0) > 0.3 ? "text-amber-400" : "text-red-400"
                          )}>
                            {((tx.recovery_probability || 0) * 100).toFixed(0)}%
                          </span>
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <p className="text-sm font-semibold text-white">
                      {formatCurrency(tx.amount)}
                    </p>
                    <p className="text-[11px] text-zinc-500">
                      {formatTime(tx.failed_at)}
                    </p>
                  </div>
                </motion.button>

                <AnimatePresence>
                  {expandedId === tx.id && tx.xai_explanation && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden border-t border-[var(--border)] bg-zinc-900/40"
                    >
                      <div className="px-5 py-4">
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