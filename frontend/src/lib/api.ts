const DEFAULT_API_BASE = "/backend-api";

function getApiBase(): string {
  // Keep the backend URL server-side. `Config` is intentionally NOT prefixed
  // with NEXT_PUBLIC_, so the value is never exposed to the browser.
  return DEFAULT_API_BASE;
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const res = await fetch(`${getApiBase()}${endpoint}`, {
      ...options,
      signal: options?.signal ?? controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      let detail = "";
      try {
        const body = await res.json();
        detail = body?.detail ? `: ${body.detail}` : "";
      } catch {
        // Keep the HTTP status as the useful fallback.
      }
      throw new Error(`API Error: ${res.status} ${res.statusText}${detail}`);
    }

    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  getDashboardMetrics: () => fetchAPI<any>("/dashboard/metrics"),
  getTransactions: (status?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status) params.set("status", status);
    return fetchAPI<any[]>(`/dashboard/transactions?${params.toString()}`);
  },
  getTransactionDetail: (id: string) =>
    fetchAPI<any>(`/dashboard/transactions/${encodeURIComponent(id)}`),
  getFailureBreakdown: () => fetchAPI<any[]>("/dashboard/failure-breakdown"),
  getInterventionEffectiveness: () =>
    fetchAPI<any[]>("/dashboard/intervention-effectiveness"),
  simulatePayment: (data: any) =>
    fetchAPI<any>("/simulator/trigger", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  simulateBatch: (count: number) =>
    fetchAPI<any>(`/simulator/batch?count=${encodeURIComponent(count)}`, {
      method: "POST",
    }),
  getAuditLogs: (transactionId?: string, limit = 100) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (transactionId) params.set("transaction_id", transactionId);
    return fetchAPI<any[]>(`/audit/logs?${params.toString()}`);
  },
  getAuditStats: () => fetchAPI<any>("/audit/stats"),
};
