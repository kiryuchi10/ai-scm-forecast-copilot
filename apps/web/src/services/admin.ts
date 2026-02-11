import { apiGet } from "./http";
import type { AdminSummaryResponse } from "@/types/api";

export function fetchAdminSummary() {
  return apiGet<AdminSummaryResponse>("/api/admin/summary");
}
