import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number): string {
  if (num >= 10000000) return `${(num / 10000000).toFixed(1)}Cr`;
  if (num >= 100000) return `${(num / 100000).toFixed(1)}L`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toFixed(0);
}

export function formatTime(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    failed: "bg-red-100 text-red-800 border-red-200",
    at_risk: "bg-amber-100 text-amber-800 border-amber-200",
    recovering: "bg-blue-100 text-blue-800 border-blue-200",
    recovered: "bg-emerald-100 text-emerald-800 border-emerald-200",
    abandoned: "bg-gray-100 text-gray-800 border-gray-200",
    escalated: "bg-purple-100 text-purple-800 border-purple-200",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
}

export function getUrgencyColor(urgency: string): string {
  const colors: Record<string, string> = {
    low: "text-green-600",
    medium: "text-amber-600",
    high: "text-orange-600",
    critical: "text-red-600",
  };
  return colors[urgency] || "text-gray-600";
}