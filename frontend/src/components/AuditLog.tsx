"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AuditLogEntry } from "@/types";
import { formatTime, cn } from "@/lib/utils";
import {
  FileText, Bot, Shield, Globe, AlertTriangle, CheckCircle2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await api.getAuditLogs(undefined, 50);
        setLogs(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const getIcon = (category: string) => {
    switch (category) {
      case "ai_decision": return <Bot className="h-3.5 w-3.5 text-indigo-400" />;
      case "policy": return <Shield className="h-3.5 w-3.5 text-amber-400" />;
      case "api_call": return <Globe className="h-3.5 w-3.5 text-blue-400" />;
      case "error": return <AlertTriangle className="h-3.5 w-3.5 text-red-400" />;
      case "recovery": return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />;
      default: return <FileText className="h-3.5 w-3.5 text-zinc-400" />;
    }
  };

  const getSeverityDot = (severity: string) => {
    const colors: Record<string, string> = {
      info: "bg-blue-400",
      warning: "bg-amber-400",
      error: "bg-red-400",
      critical: "bg-red-600",
    };
    return colors[severity] || "bg-zinc-400";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="rounded-xl border border-[var(--border)] bg-[var(--card)]"
    >
      <div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-zinc-400" />
          <h3 className="text-sm font-semibold text-white">Audit Trail</h3>
        </div>
        <motion.span
          key={logs.length}
          initial={{ scale: 1.2, color: "#10b981" }}
          animate={{ scale: 1, color: "#71717a" }}
          transition={{ duration: 0.3 }}
          className="text-[11px]"
        >
          {logs.length} entries
        </motion.span>
      </div>

      <div className="max-h-[400px] overflow-y-auto">
        {logs.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-xs text-zinc-500">
            No audit logs yet
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {logs.map((log, idx) => (
              <motion.div
                key={log.id}
                layout
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2, delay: Math.min(idx * 0.02, 0.2) }}
                className="flex items-start gap-3 border-b border-[var(--border)] px-5 py-3 last:border-b-0 hover:bg-[var(--card-hover)] transition-colors"
              >
                <div className="mt-0.5">{getIcon(log.event_category)}</div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-zinc-300 capitalize">
                      {log.action.replace(/_/g, " ")}
                    </span>
                    <motion.span
                      animate={{ opacity: [1, 0.4, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className={cn(
                        "h-1.5 w-1.5 rounded-full",
                        getSeverityDot(log.severity)
                      )}
                    />
                    <span className="text-[10px] text-zinc-600 capitalize">
                      {log.actor}
                    </span>
                  </div>
                  {log.description && (
                    <p className="text-[11px] text-zinc-500 mt-0.5 line-clamp-2">
                      {log.description}
                    </p>
                  )}
                </div>
                <span className="text-[10px] text-zinc-600 whitespace-nowrap">
                  {formatTime(log.created_at)}
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  );
}