"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  glowClass?: string;
  index?: number;
  trend?: string;
  trendUp?: boolean;
}

export default function MotionMetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  glowClass,
  index = 0,
  trend,
  trendUp,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: "easeOut" }}
      whileHover={{ y: -4, scale: 1.015, transition: { duration: 0.2 } }}
      className={cn(
        "group relative overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--card)] p-5 transition-colors hover:bg-[var(--card-hover)]",
        glowClass
      )}
    >
      {/* Top gradient beam */}
      <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-indigo-500/60 to-transparent" />

      {/* Hover glow effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
        <div className="absolute -top-24 -right-24 h-48 w-48 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-[11px] font-medium uppercase tracking-widest text-zinc-500">
            {title}
          </p>
          <motion.p
            key={value}
            initial={{ scale: 0.95, opacity: 0.6 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3, type: "spring", stiffness: 200 }}
            className="text-2xl font-bold tracking-tight text-white"
          >
            {value}
          </motion.p>
          {subtitle && (
            <p className="text-xs text-zinc-400">{subtitle}</p>
          )}
          {trend && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className={cn(
                "text-xs font-semibold",
                trendUp ? "text-emerald-400" : "text-red-400"
              )}
            >
              {trend}
            </motion.div>
          )}
        </div>

        <motion.div
          whileHover={{ rotate: 12, scale: 1.15 }}
          transition={{ type: "spring", stiffness: 300 }}
          className="rounded-lg bg-zinc-800/60 p-2.5 text-zinc-400 group-hover:text-indigo-300 group-hover:bg-indigo-500/10 transition-colors"
        >
          <Icon className="h-5 w-5" />
        </motion.div>
      </div>
    </motion.div>
  );
}