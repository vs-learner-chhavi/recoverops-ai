export interface DashboardMetrics {
  total_failed_revenue: number;
  total_recovered_revenue: number;
  recovery_rate: number;
  total_transactions: number;
  active_recoveries: number;
  interventions_executed: number;
  policy_blocks: number;
  avg_recovery_time_minutes: number | null;
  roi_multiplier: number | null;
}

export interface Transaction {
  id: string;
  razorpay_payment_id: string;
  amount: number;
  currency: string;
  payment_method: string | null;
  status: string;
  failure_category: string | null;
  recovery_probability: number | null;
  churn_risk_score: number | null;
  xai_explanation: XAIExplanation | null;
  recommended_intervention: string | null;
  retry_count: number;
  failed_at: string | null;
  recovered_at: string | null;
}

export interface TransactionDetail extends Transaction {
  customer_email: string | null;
  customer_phone: string | null;
  bank: string | null;
  card_network: string | null;
  error_source: string | null;
  error_step: string | null;
  interventions: Intervention[];
  audit_logs: AuditLogEntry[];
}

export interface Intervention {
  id: string;
  intervention_type: string;
  tier: number;
  status: string;
  confidence_score: number | null;
  reasoning: string | null;
  payment_link_url: string | null;
  message_content: string | null;
  channel: string | null;
  policy_approved: boolean;
  policy_rejection_reason: string | null;
  resulted_in_recovery: boolean;
  recovered_amount: number;
  intervention_cost: number;
  created_at: string | null;
  executed_at: string | null;
}

export interface AuditLogEntry {
  id: string;
  event_type: string;
  event_category: string;
  severity: string;
  actor: string;
  action: string;
  description: string | null;
  metadata: Record<string, any> | null;
  created_at: string | null;
}

export interface XAIExplanation {
  base_value: number;
  prediction_shift: number;
  top_positive_factors: FeatureContribution[];
  top_negative_factors: FeatureContribution[];
  all_contributions: FeatureContribution[];
  summary: string;
  diagnosis: Diagnosis;
}

export interface FeatureContribution {
  feature: string;
  value: number;
  shap_value: number;
  impact: string;
  magnitude: number;
}

export interface Diagnosis {
  root_cause: string;
  recommended_action: string;
  urgency: string;
  retry_window: string;
}

export interface FailureBreakdown {
  category: string;
  count: number;
  total_amount: number;
  recovery_rate: number;
}

export interface InterventionEffectiveness {
  intervention_type: string;
  total_executed: number;
  successful: number;
  success_rate: number;
  total_recovered: number;
  avg_cost: number;
}

export interface SimulateRequest {
  amount: number;
  payment_method: string;
  failure_reason: string;
  customer_email?: string;
  customer_phone?: string;
  bank?: string;
  card_network?: string;
}

export interface SimulateResponse {
  transaction_id: string;
  razorpay_payment_id: string;
  status: string;
  diagnosis: Record<string, any>;
  recommended_intervention: string;
  message: string;
}