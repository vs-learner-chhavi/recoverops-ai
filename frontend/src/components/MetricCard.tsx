"use client";

import { createElement } from "react";
import { LucideIcon } from "lucide-react";

const cn = (...classes: Array<string | false | null | undefined>) =>
  classes.filter(Boolean).join(" ");

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  glowClass?: string;
}

export default function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendUp,
  glowClass,
}: MetricCardProps) {
  return createElement(
    "div",
    {
      className: cn(
        "rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 transition-all hover:bg-[var(--card-hover)]",
        glowClass
      ),
    },
    createElement(
      "div",
      { className: "flex items-start justify-between" },
      createElement(
        "div",
        { className: "space-y-2" },
        createElement("p", { className: "text-xs font-medium uppercase tracking-wider text-zinc-500" }, title),
        createElement("p", { className: "text-2xl font-bold tracking-tight" }, value),
        subtitle ? createElement("p", { className: "text-xs text-zinc-500" }, subtitle) : null
      ),
      createElement(
        "div",
        { className: "rounded-lg bg-zinc-800/50 p-2.5" },
        createElement(Icon, { className: "h-5 w-5 text-zinc-400" })
      )
    ),
    trend
      ? createElement(
          "div",
          { className: "mt-3 flex items-center gap-1" },
          createElement(
            "span",
            {
              className: cn(
                "text-xs font-medium",
                trendUp ? "text-emerald-400" : "text-red-400"
              ),
            },
            trend
          )
        )
      : null
  );
}