const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export const api = {
  getDashboardMetrics: () => fetchAPI<any>("/dashboard/metrics"),
  getTransactions: (status?: string, limit = 50) =>
    fetchAPI<any[]>(`/dashboard/transactions?limit=${limit}${status ? `&status=${status}` : ""}`),
  getTransactionDetail: (id: string) =>
    fetchAPI<any>(`/dashboard/transactions/${id}`),
  getFailureBreakdown: () => fetchAPI<any[]>("/dashboard/failure-breakdown"),
  getInterventionEffectiveness: () =>
    fetchAPI<any[]>("/dashboard/intervention-effectiveness"),
  simulatePayment: (data: any) =>
    fetchAPI<any>("/simulator/trigger", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  simulateBatch: (count: number) =>
    fetchAPI<any>(`/simulator/batch?count=${count}`, { method: "POST" }),
  getAuditLogs: (transactionId?: string, limit = 100) =>
    fetchAPI<any[]>(
      `/audit/logs?limit=${limit}${transactionId ? `&transaction_id=${transactionId}` : ""}`
    ),
  getAuditStats: () => fetchAPI<any>("/audit/stats"),
};