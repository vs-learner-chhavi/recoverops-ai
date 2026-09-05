"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { DashboardMetrics } from "@/types";

export function useDashboard(refreshInterval = 5000) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      const data = await api.getDashboardMetrics();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch dashboard metrics");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  return { metrics, loading, error, refetch: fetchMetrics };
}