"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { SimulateResponse } from "@/types";
import {
  Play, Zap, Loader2, CheckCircle2, XCircle,
  AlertTriangle, Clock, Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";

export default function Simulator() {
  const [amount, setAmount] = useState(2500);
  const [method, setMethod] = useState("upi");
  const [failure, setFailure] = useState("bank_technical");
  const [bank, setBank] = useState("HDFC");
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [result, setResult] = useState<SimulateResponse | null>(null);
  const [batchResult, setBatchResult] = useState<any>(null);

  const failureTypes = [
    { value: "bank_technical", label: "Bank Technical" },
    { value: "network_error", label: "Network Error" },
    { value: "insufficient_funds", label: "Insufficient Funds" },
    { value: "authentication_failed", label: "Auth Failed" },
    { value: "card_expired", label: "Card Expired" },
    { value: "user_cancelled", label: "User Cancelled" },
    { value: "gateway_error", label: "Gateway Error" },
    { value: "fraud_suspected", label: "Fraud Suspected" },
  ];

  const fireConfetti = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.7, x: 0.85 },
      colors: ["#10b981", "#6366f1", "#3b82f6", "#a78bfa"],
      startVelocity: 30,
      ticks: 60,
    });
    setTimeout(() => {
      confetti({
        particleCount: 50,
        spread: 100,
        origin: { y: 0.7, x: 0.85 },
        colors: ["#10b981", "#34d399"],
      });
    }, 200);
  };

  const simulate = async () => {
    setLoading(true);
    setResult(null);
    setBatchResult(null);
    try {
      const res = await api.simulatePayment({
        amount,
        payment_method: method,
        failure_reason: failure,
        bank,
        customer_email: "demo@recoverops.ai",
        customer_phone: "9876543210",
      });
      setResult(res);

      if (res.status === "recovered") {
        fireConfetti();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const simulateBatch = async () => {
    setBatchLoading(true);
    setBatchResult(null);
    setResult(null);
    try {
      const res = await api.simulateBatch(20);
      setBatchResult(res);
      if (res.recovered > 0) fireConfetti();
    } catch (err) {
      console.error(err);
    } finally {
      setBatchLoading(false);
    }
  };

  const statusStyle = (status: string) => {
    if (status === "recovered")
      return "border-emerald-500/40 bg-emerald-500/10 text-emerald-200";
    if (status === "escalated")
      return "border-amber-500/40 bg-amber-500/10 text-amber-200";
    if (status === "abandoned")
      return "border-zinc-500/40 bg-zinc-500/10 text-zinc-300";
    if (status === "recovering")
      return "border-blue-500/40 bg-blue-500/10 text-blue-200";
    return "border-red-500/40 bg-red-500/10 text-red-200";
  };

  const StatusIcon = ({ status }: { status: string }) => {
    const props = { className: "h-6 w-6" };
    if (status === "recovered") return <CheckCircle2 {...props} className="h-6 w-6 text-emerald-400" />;
    if (status === "escalated") return <AlertTriangle {...props} className="h-6 w-6 text-amber-400" />;
    if (status === "abandoned") return <XCircle {...props} className="h-6 w-6 text-zinc-400" />;
    if (status === "recovering") return <Clock {...props} className="h-6 w-6 text-blue-400" />;
    return <XCircle {...props} className="h-6 w-6 text-red-400" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="rounded-xl border border-[var(--border)] bg-[var(--card)]"
    >
      <div className="border-b border-[var(--border)] px-5 py-4">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ rotate: [0, 15, -15, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            <Sparkles className="h-4 w-4 text-indigo-400" />
          </motion.div>
          <h3 className="text-sm font-semibold text-white">Payment Failure Simulator</h3>
        </div>
        <p className="text-[11px] text-zinc-500 mt-1">
          Trigger a failure → AI diagnoses → policy gate → action
        </p>
      </div>

      <div className="p-5 space-y-4">
        {/* Amount */}
        <div>
          <label className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
            Amount (₹)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="mt-1.5 w-full rounded-lg border border-[var(--border)] bg-zinc-900 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-all"
          />
        </div>

        {/* Payment Method */}
        <div>
          <label className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
            Payment Method
          </label>
          <div className="mt-1.5 grid grid-cols-4 gap-2">
            {["card", "upi", "netbanking", "wallet"].map((m) => (
              <motion.button
                key={m}
                type="button"
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => setMethod(m)}
                className={cn(
                  "rounded-lg border px-2 py-2 text-xs font-medium capitalize transition-colors",
                  method === m
                    ? "border-indigo-500 bg-indigo-500/15 text-indigo-200"
                    : "border-[var(--border)] text-zinc-500 hover:text-zinc-300"
                )}
              >
                {m}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Failure Reason */}
        <div>
          <label className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
            Failure Reason
          </label>
          <div className="mt-1.5 grid grid-cols-2 gap-2">
            {failureTypes.map((f) => (
              <motion.button
                key={f.value}
                type="button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setFailure(f.value)}
                className={cn(
                  "rounded-lg border px-3 py-2 text-[11px] font-medium text-left transition-colors",
                  failure === f.value
                    ? "border-indigo-500 bg-indigo-500/15 text-indigo-200"
                    : "border-[var(--border)] text-zinc-500 hover:text-zinc-300"
                )}
              >
                {f.label}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Bank */}
        <div>
          <label className="text-[11px] font-medium uppercase tracking-wider text-zinc-500">
            Bank
          </label>
          <select
            value={bank}
            onChange={(e) => setBank(e.target.value)}
            className="mt-1.5 w-full rounded-lg border border-[var(--border)] bg-zinc-900 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
          >
            {["HDFC", "ICICI", "SBI", "Axis", "Kotak", "Yes Bank", "PNB", "RBL"].map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>

        {/* Buttons */}
        <div className="flex gap-3 pt-1">
          <motion.button
            type="button"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={simulate}
            disabled={loading}
            className="relative flex flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 disabled:opacity-50 transition-shadow overflow-hidden"
          >
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
            />
            {loading ? <Loader2 className="h-4 w-4 animate-spin relative" /> : <Play className="h-4 w-4 relative" />}
            <span className="relative">{loading ? "Running AI..." : "Simulate Failure"}</span>
          </motion.button>
          <motion.button
            type="button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={simulateBatch}
            disabled={batchLoading}
            className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm font-medium text-zinc-400 hover:bg-zinc-800 hover:text-white disabled:opacity-50"
          >
            {batchLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
            Batch
          </motion.button>
        </div>

        {/* Single result */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              key={result.transaction_id}
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -10 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className={cn(
                "rounded-xl border p-4 space-y-3",
                statusStyle(result.status)
              )}
            >
              <div className="flex items-start gap-3">
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                >
                  <StatusIcon status={result.status} />
                </motion.div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold capitalize">
                    {result.status.replace(/_/g, " ")}
                  </p>
                  <p className="text-xs mt-1 opacity-90 leading-relaxed">
                    {result.message}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="rounded-lg bg-black/30 p-2.5">
                  <p className="text-zinc-400 mb-1">Intervention</p>
                  <p className="font-medium capitalize">
                    {(result.recommended_intervention || "none").replace(/_/g, " ")}
                  </p>
                </div>
                <div className="rounded-lg bg-black/30 p-2.5">
                  <p className="text-zinc-400 mb-1">Transaction ID</p>
                  <p className="font-mono truncate text-[10px]">
                    {result.transaction_id.slice(0, 16)}...
                  </p>
                </div>
              </div>

              <p className="text-[11px] opacity-70 pt-1 border-t border-white/10">
                💡 Scroll to <b>Live Recovery Feed</b> to inspect SHAP explanation
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Batch result */}
        <AnimatePresence>
          {batchResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ type: "spring", stiffness: 300 }}
              className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-3"
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <p className="text-sm font-semibold text-emerald-300">Batch Complete</p>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                {[
                  { label: "Processed", value: batchResult.total_simulated, color: "text-white" },
                  { label: "Recovered", value: batchResult.recovered, color: "text-emerald-300" },
                  { label: "Rate", value: batchResult.recovery_rate, color: "text-emerald-300" },
                ].map((s, i) => (
                  <motion.div
                    key={s.label}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <p className="text-zinc-500 text-[10px] uppercase tracking-wider">{s.label}</p>
                    <p className={cn("font-bold text-lg", s.color)}>{s.value}</p>
                  </motion.div>
                ))}
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-emerald-500/20">
                <div>
                  <p className="text-zinc-500 text-[10px]">Failed Volume</p>
                  <p className="text-red-300 font-semibold">{batchResult.total_amount}</p>
                </div>
                <div>
                  <p className="text-zinc-500 text-[10px]">Recovered Volume</p>
                  <p className="text-emerald-300 font-semibold">{batchResult.recovered_amount}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Quick recipes */}
        <div className="rounded-lg border border-[var(--border)] bg-zinc-950/50 p-3">
          <p className="text-[11px] font-semibold text-zinc-400 mb-2">⚡ Quick Demos</p>
          <div className="space-y-1.5 text-[11px] text-zinc-500">
            <p>• <span className="text-zinc-300">Bank Technical + UPI</span> → auto retry, often recovers</p>
            <p>• <span className="text-zinc-300">Insufficient Funds + Card</span> → payment link sent</p>
            <p>• <span className="text-zinc-300">Fraud Suspected</span> → escalated, blocked by policy</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}