"use client";

import React from "react";
import { Intervention } from "@/types";
import { formatTime, formatCurrency, cn } from "@/lib/utils";
import {
  RefreshCw, Link2, MessageCircle, Mail, Phone, AlertTriangle,
  CheckCircle2, XCircle, ShieldAlert, Clock,
} from "lucide-react";

interface Props {
  interventions: Intervention[];
}

const ICON_MAP: Record<string, React.ElementType> = {
  smart_retry: RefreshCw,
  payment_link: Link2,
  whatsapp_nudge: MessageCircle,
  email_reminder: Mail,
  voice_call: Phone,
  manual_escalation: AlertTriangle,
};

const STATUS_ICON: Record<string, React.ElementType> = {
  completed: CheckCircle2,
  failed: XCircle,
  blocked_by_policy: ShieldAlert,
  pending: Clock,
  executing: Clock,
};

export default function InterventionTimeline({ interventions }: Props): React.JSX.Element {
  if (interventions.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-zinc-500">
        No interventions yet
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {interventions.map((item, idx) => {
        const Icon = ICON_MAP[item.intervention_type] || RefreshCw;
        const StatusIcon = STATUS_ICON[item.status] || Clock;
        const isLast = idx === interventions.length - 1;

        return (
          <div key={item.id} className="flex gap-3">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full border",
                item.resulted_in_recovery
                  ? "border-emerald-500 bg-emerald-500/10 text-emerald-400"
                  : item.status === "blocked_by_policy"
                  ? "border-amber-500 bg-amber-500/10 text-amber-400"
                  : item.status === "failed"
                  ? "border-red-500 bg-red-500/10 text-red-400"
                  : "border-zinc-600 bg-zinc-800 text-zinc-400"
              )}>
                <Icon className="h-3.5 w-3.5" />
              </div>
              {!isLast && (
                <div className="w-px flex-1 bg-zinc-700 my-1" />
              )}
            </div>

            {/* Content */}
            <div className={cn("flex-1 pb-4", isLast && "pb-0")}>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold capitalize text-zinc-200">
                  {item.intervention_type.replace(/_/g, " ")}
                </span>
                <span className="text-[10px] text-zinc-500">
                  Tier {item.tier}
                </span>
                <StatusIcon className={cn(
                  "h-3 w-3",
                  item.resulted_in_recovery ? "text-emerald-400" : "text-zinc-500"
                )} />
              </div>
              <div className="mt-1 flex items-center gap-3 text-[11px] text-zinc-500">
                <span>{formatTime(item.created_at)}</span>
                {item.confidence_score !== null && (
                  <span>Confidence: {(item.confidence_score * 100).toFixed(0)}%</span>
                )}
                <span>Cost: ₹{item.intervention_cost.toFixed(2)}</span>
              </div>
              {item.resulted_in_recovery && (
                <p className="mt-1 text-xs font-semibold text-emerald-400">
                  ✅ Recovered {formatCurrency(item.recovered_amount)}
                </p>
              )}
              {item.policy_rejection_reason && (
                <p className="mt-1 text-xs text-amber-400">
                  ⚠️ {item.policy_rejection_reason}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}