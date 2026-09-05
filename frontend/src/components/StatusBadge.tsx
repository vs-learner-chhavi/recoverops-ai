"use client";

import { createElement } from "react";
import { getStatusColor } from "@/lib/utils";
import { cn } from "@/lib/utils";

export default function StatusBadge({ status }: { status: string }) {
  return createElement(
    "span",
    {
      className: cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold capitalize",
        getStatusColor(status)
      ),
    },
    createElement("span", {
      className: cn("h-1.5 w-1.5 rounded-full", {
        "bg-red-500": status === "failed",
        "bg-amber-500": status === "at_risk",
        "bg-blue-500 animate-pulse": status === "recovering",
        "bg-emerald-500": status === "recovered",
        "bg-gray-500": status === "abandoned",
        "bg-purple-500": status === "escalated",
      }),
    }),
    status.replace("_", " ")
  );
}