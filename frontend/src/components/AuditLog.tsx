"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AuditLogEntry } from "@/types";
import { formatTime, cn } from "@/lib/utils";
import { FileText, Bot, Shield, Globe, AlertTriangle, CheckCircle2, Activity, Radio, ChevronRight, Clock3 } from "lucide-react";
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
      case "ai_decision": return <Bot className="h-4 w-4 text-indigo-300" />;
      case "policy": return <Shield className="h-4 w-4 text-amber-300" />;
      case "api_call": return <Globe className="h-4 w-4 text-sky-300" />;
      case "error": return <AlertTriangle className="h-4 w-4 text-rose-300" />;
      case "recovery": return <CheckCircle2 className="h-4 w-4 text-emerald-300" />;
      default: return <FileText className="h-4 w-4 text-zinc-400" />;
    }
  };

  const getSeverity = (severity: string) => ({ info: "bg-sky-400", warning: "bg-amber-400", error: "bg-rose-400", critical: "bg-red-500" }[severity] || "bg-zinc-500");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-70px" }} transition={{ duration: .5 }} className="overflow-hidden rounded-2xl border border-white/[.07] bg-[#0d0f16]/95 shadow-[0_18px_60px_rgba(0,0,0,.22)]">
      <div className="border-b border-white/[.06] bg-gradient-to-r from-cyan-400/[.045] via-transparent to-indigo-400/[.035] px-4 py-4 sm:px-5">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 shadow-lg shadow-cyan-500/5"><Activity className="h-4 w-4 text-cyan-300" /></div>
            <div><div className="flex items-center gap-2"><h3 className="text-sm font-semibold text-white">Audit Trail</h3><span className="flex items-center gap-1 rounded-full border border-emerald-400/15 bg-emerald-400/10 px-1.5 py-0.5 text-[8px] font-semibold uppercase tracking-wider text-emerald-300"><motion.span animate={{ opacity: [1, .3, 1] }} transition={{ duration: 1.8, repeat: Infinity }} className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Live</span></div><p className="mt-0.5 text-[10px] text-zinc-500">Every AI decision, policy check and recovery action</p></div>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-white/[.06] bg-white/[.025] px-2.5 py-2 text-[10px] text-zinc-400"><Radio className="h-3 w-3 text-cyan-300" />{logs.length} events</div>
        </div>
      </div>

      <div className="grid lg:grid-cols-[1fr_240px]">
        <div className="max-h-[500px] overflow-y-auto p-3 sm:p-4">
          {logs.length === 0 ? <div className="flex flex-col items-center justify-center py-16 text-center"><FileText className="mb-3 h-7 w-7 text-zinc-700" /><p className="text-sm text-zinc-400">No audit activity yet</p><p className="mt-1 text-[11px] text-zinc-600">Run a simulation to populate the audit trail.</p></div> : <div className="relative space-y-1">
            <div className="absolute bottom-5 left-[25px] top-5 w-px bg-gradient-to-b from-cyan-400/30 via-indigo-400/15 to-transparent" />
            <AnimatePresence initial={false}>
              {logs.map((log, idx) => <motion.div key={log.id} layout initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: .22, delay: Math.min(idx * .012, .15) }} className="group relative flex gap-3 rounded-xl border border-transparent px-1 py-3 transition-all hover:border-white/[.05] hover:bg-white/[.025] sm:gap-4 sm:px-2">
                <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/[.07] bg-[#151823] shadow-sm transition-transform group-hover:scale-105">{getIcon(log.event_category)}</div>
                <div className="min-w-0 flex-1 pt-0.5"><div className="flex flex-wrap items-center gap-x-2 gap-y-1"><span className="text-xs font-medium capitalize text-zinc-200">{log.action.replace(/_/g, " ")}</span><span className={cn("h-1.5 w-1.5 rounded-full", getSeverity(log.severity))} /><span className="text-[9px] uppercase tracking-wider text-zinc-500">{log.actor}</span></div>{log.description && <p className="mt-1 text-[11px] leading-relaxed text-zinc-500">{log.description}</p>}</div><div className="flex shrink-0 items-start gap-1 pt-1 text-[9px] text-zinc-600"><Clock3 className="mt-0.5 h-3 w-3" />{formatTime(log.created_at)}</div><ChevronRight className="absolute right-2 top-1/2 hidden h-3 w-3 -translate-y-1/2 text-zinc-700 group-hover:block" />
              </motion.div>)}
            </AnimatePresence>
          </div>}
        </div>

        <aside className="border-t border-white/[.06] bg-white/[.012] p-4 lg:border-l lg:border-t-0">
          <p className="text-[9px] font-semibold uppercase tracking-[.18em] text-zinc-500">Operational posture</p>
          <div className="mt-3 rounded-xl border border-emerald-400/10 bg-emerald-400/[.045] p-3"><div className="flex items-center gap-2"><span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" /><span className="text-xs font-medium text-emerald-300">System healthy</span></div><p className="mt-2 text-[10px] leading-relaxed text-zinc-500">Recovery decisions are being logged and policy checks are active.</p></div>
          <div className="mt-3 space-y-2">
            <div className="rounded-xl border border-white/[.05] bg-white/[.018] p-3"><p className="text-[9px] uppercase tracking-wider text-zinc-600">Events tracked</p><p className="mt-1 font-mono text-lg text-white">{logs.length}</p></div>
            <div className="rounded-xl border border-white/[.05] bg-white/[.018] p-3"><p className="text-[9px] uppercase tracking-wider text-zinc-600">Stream</p><p className="mt-1 text-[11px] font-medium text-zinc-300">Real-time · 5s</p></div>
          </div>
        </aside>
      </div>
    </motion.div>
  );
}
