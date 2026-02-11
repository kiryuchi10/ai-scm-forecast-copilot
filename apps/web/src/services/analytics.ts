import { apiGet } from "./http";
import type { TrendsResponse, BreakdownResponse } from "@/types/api";

export function fetchTrends(metric: string, days: number) {
  return apiGet<TrendsResponse>("/api/analytics/trends", { metric, days });
}

export function fetchBreakdown(by: string, days: number, metric: string) {
  return apiGet<BreakdownResponse>("/api/analytics/breakdown", { by, days, metric });
}
