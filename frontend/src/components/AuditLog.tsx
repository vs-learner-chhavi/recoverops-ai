"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AuditLogEntry } from "@/types";
import { formatTime, cn } from "@/lib/utils";
import { FileText, Bot, Shield, Globe, AlertTriangle, CheckCircle2, Activity, Radio } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try { setLogs(await api.getAuditLogs(undefined, 50)); } catch (err) { console.error(err); }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const getIcon = (category: string) => {
    switch (category) {
      case "ai_decision": return <Bot className="h-3.5 w-3.5 text-indigo-300" />;
      case "policy": return <Shield className="h-3.5 w-3.5 text-amber-300" />;
      case "api_call": return <Globe className="h-3.5 w-3.5 text-blue-300" />;
      case "error": return <AlertTriangle className="h-3.5 w-3.5 text-red-300" />;
      case "recovery": return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-300" />;
      default: return <FileText className="h-3.5 w-3.5 text-zinc-400" />;
    }
  };

  const getSeverity = (severity: string) => ({ info: "bg-blue-400", warning: "bg-amber-400", error: "bg-red-400", critical: "bg-red-600" }[severity] || "bg-zinc-500");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-70px" }} transition={{ duration: .5 }} className="glass overflow-hidden rounded-2xl">
      <div className="border-b border-[var(--border)] bg-white/[.015] px-4 py-4 sm:px-5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10"><Activity className="h-4 w-4 text-cyan-300" /></div><div><div className="flex items-center gap-2"><h3 className="text-sm font-semibold text-white">Audit Trail</h3><span className="flex items-center gap-1 text-[9px] uppercase tracking-wider text-emerald-400"><motion.span animate={{ opacity: [1, .3, 1] }} transition={{ duration: 1.8, repeat: Infinity }} className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Live</span></div><p className="mt-0.5 text-[10px] text-zinc-600">Every AI decision, policy check and recovery action</p></div></div>
          <div className="hidden items-center gap-2 rounded-full border border-[var(--border)] bg-white/[.02] px-2.5 py-1.5 text-[10px] text-zinc-500 sm:flex"><Radio className="h-3 w-3" />{logs.length} events</div>
        </div>
      </div>

      <div className="max-h-[440px] overflow-y-auto p-3 sm:p-4">
        {logs.length === 0 ? <div className="flex flex-col items-center justify-center py-14 text-center"><FileText className="mb-3 h-6 w-6 text-zinc-700" /><p className="text-sm text-zinc-400">No audit activity yet</p><p className="mt-1 text-[11px] text-zinc-600">Run a simulation to populate the audit trail.</p></div> : <div className="relative space-y-1">
          <div className="absolute bottom-4 left-[22px] top-4 w-px bg-gradient-to-b from-indigo-500/30 via-white/[.08] to-transparent sm:left-[26px]" />
          <AnimatePresence initial={false}>
            {logs.map((log, idx) => <motion.div key={log.id} layout initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: .22, delay: Math.min(idx * .018, .18) }} className="group relative flex gap-3 rounded-xl px-1 py-2.5 transition-colors hover:bg-white/[.025] sm:gap-4 sm:px-2">
              <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[var(--border)] bg-[#101118] shadow-sm">{getIcon(log.event_category)}</div>
              <div className="min-w-0 flex-1 pt-0.5"><div className="flex flex-wrap items-center gap-x-2 gap-y-1"><span className="text-xs font-medium capitalize text-zinc-300">{log.action.replace(/_/g, " ")}</span><span className={cn("h-1.5 w-1.5 rounded-full", getSeverity(log.severity))} /><span className="text-[9px] uppercase tracking-wider text-zinc-600">{log.actor}</span></div>{log.description && <p className="mt-1 line-clamp-2 text-[11px] leading-relaxed text-zinc-600">{log.description}</p>}</div><span className="shrink-0 pt-1 text-[9px] text-zinc-700">{formatTime(log.created_at)}</span>
            </motion.div>)}
          </AnimatePresence>
        </div>}
      </div>
    </motion.div>
  );
}
