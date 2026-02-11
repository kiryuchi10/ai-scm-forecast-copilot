import { apiGet } from "./http";
import type { ProjectsRunsResponse } from "@/types/api";

export function fetchProjectsRuns(limit: number = 50) {
  return apiGet<ProjectsRunsResponse>("/api/projects/runs", { limit });
}
