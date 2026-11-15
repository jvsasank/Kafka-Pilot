export type Summary = {
  total_transactions: number;
  high_risk_transactions: number;
  unacknowledged_alerts: number;
  processed_volume: number;
  risk_distribution: Record<string, number>;
};

export type Transaction = {
  id: string;
  event_id: string;
  account_id: string;
  merchant: string;
  amount: number;
  currency: string;
  country: string;
  channel: string;
  status: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  reasons: string[];
  occurred_at: string;
  created_at: string;
};

export type Alert = {
  id: string;
  transaction_id: string;
  severity: "high" | "critical";
  title: string;
  description: string;
  acknowledged: boolean;
  created_at: string;
  transaction: Transaction;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  summary: () => request<Summary>("/api/summary"),
  transactions: (riskLevel = "") =>
    request<Transaction[]>(`/api/transactions?limit=80${riskLevel ? `&risk_level=${riskLevel}` : ""}`),
  alerts: () => request<Alert[]>("/api/alerts?limit=20"),
  acknowledge: (id: string) => request<Alert>(`/api/alerts/${id}/ack`, { method: "PATCH" }),
  createTransaction: (payload: Record<string, unknown>) =>
    request<Transaction>("/api/transactions", { method: "POST", body: JSON.stringify(payload) })
};
