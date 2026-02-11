import { apiGet } from "./http";
import type { KpiSummary } from "@/types/api";

export function fetchKpiSummary() {
  return apiGet<KpiSummary>("/api/kpi/summary");
}
