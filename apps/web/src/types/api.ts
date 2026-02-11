// API 응답 타입 (실데이터만, mock 없음)

export interface KpiSummary {
  total_revenue: number;
  total_orders: number;
  late_rate: number;
  top_products: { product_key: string; product_name: string; revenue: number; qty: number }[];
  top_late_orders: { order_key: string; delay_days: number; shipping_mode: string; delivery_status: string }[];
  last_updated: string;
}

export interface TrendsResponse {
  metric: string;
  days: number;
  series: { dt: string; value: number }[];
}

export interface BreakdownResponse {
  by: string;
  metric: string;
  days: number;
  items: { key: string; value: number }[];
}

export interface AdminSummaryResponse {
  user_count: number;
  server_status: string;
  db_status: string;
  audit_events: number;
}

export interface ProjectsRunsResponse {
  etl: {
    job_name: string;
    status: string;
    started_at: string | null;
    ended_at: string | null;
    row_count: number | null;
    message: string | null;
  }[];
  forecast: {
    run_id: string;
    model_name: string;
    status: string;
    started_at: string | null;
    ended_at: string | null;
    metrics_json: unknown;
  }[];
  policy: {
    run_id: string;
    product_key: string;
    as_of: string | null;
    reorder_point: number | null;
    safety_stock: number | null;
    recommended_qty: number | null;
    created_at: string | null;
  }[];
}
