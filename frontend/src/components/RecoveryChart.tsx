"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FailureBreakdown, InterventionEffectiveness } from "@/types";
import { formatCurrency } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";

const COLORS = [
  "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
  "#10b981", "#3b82f6", "#ef4444", "#14b8a6",
];

export default function RecoveryChart() {
  const [failureData, setFailureData] = useState<FailureBreakdown[]>([]);
  const [interventionData, setInterventionData] = useState<InterventionEffectiveness[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [fd, id] = await Promise.all([
          api.getFailureBreakdown(),
          api.getInterventionEffectiveness(),
        ]);
        setFailureData(fd);
        setInterventionData(id);
      } catch (err) {
        console.error(err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Failure Category Distribution */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
        <h3 className="text-sm font-semibold mb-4">Failure Distribution</h3>
        {failureData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={failureData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
                dataKey="count"
                nameKey="category"
              >
                {failureData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#111118",
                  border: "1px solid #1e1e2e",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value: any, name: string) => [
                  `${value} transactions`,
                  name.replace(/_/g, " "),
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[220px] text-xs text-zinc-500">
            No data yet
          </div>
        )}
        <div className="mt-3 grid grid-cols-2 gap-2">
          {failureData.slice(0, 6).map((f, i) => (
            <div key={f.category} className="flex items-center gap-2 text-[11px]">
              <span
                className="h-2.5 w-2.5 rounded-full shrink-0"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              <span className="text-zinc-400 truncate capitalize">
                {f.category.replace(/_/g, " ")}
              </span>
              <span className="text-zinc-500 ml-auto">{f.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Intervention Effectiveness */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
        <h3 className="text-sm font-semibold mb-4">Intervention Effectiveness</h3>
        {interventionData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={interventionData} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 11, fill: "#71717a" }} />
              <YAxis
                type="category"
                dataKey="intervention_type"
                tick={{ fontSize: 10, fill: "#71717a" }}
                width={100}
                tickFormatter={(v) => v.replace(/_/g, " ")}
              />
              <Tooltip
                contentStyle={{
                  background: "#111118",
                  border: "1px solid #1e1e2e",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="success_rate" fill="#6366f1" radius={[0, 4, 4, 0]} name="Success %" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[220px] text-xs text-zinc-500">
            No data yet
          </div>
        )}
        <div className="mt-3 space-y-2">
          {interventionData.map((item) => (
            <div key={item.intervention_type} className="flex items-center justify-between text-[11px]">
              <span className="text-zinc-400 capitalize">
                {item.intervention_type.replace(/_/g, " ")}
              </span>
              <div className="flex items-center gap-3">
                <span className="text-emerald-400">
                  {formatCurrency(item.total_recovered)}
                </span>
                <span className="text-zinc-500">
                  {item.successful}/{item.total_executed}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}