import { useQuery } from "@tanstack/react-query";
import { Package, ListChecks, TrendingUp } from "lucide-react";
import { fetchProjectsRuns } from "@/services/projects";
import PageHeader from "@/components/common/PageHeader";
import SectionCard from "@/components/cards/SectionCard";
import DataTable from "@/components/tables/DataTable";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import ErrorPanel from "@/components/common/ErrorPanel";

export default function ProjectsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["projects", "runs"],
    queryFn: () => fetchProjectsRuns(50),
  });

  if (isLoading) return <LoadingSkeleton />;
  if (error) {
    const err = error as Error & { errorType?: string };
    return (
      <ErrorPanel
        message={err instanceof Error ? err.message : "실행 목록을 불러올 수 없습니다."}
        errorType={err.errorType}
        onRetry={() => refetch()}
      />
    );
  }

  const runs = data!;

  const stats = [
    { icon: ListChecks, label: "ETL Runs", value: runs.etl.length },
    { icon: TrendingUp, label: "Forecast Runs", value: runs.forecast.length },
    { icon: Package, label: "Policy Results", value: runs.policy.length },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Project Dashboard"
        subtitle="ETL·Forecast·Policy 운영 상태 (실데이터)"
      />

      {/* Stats row - project-dashboard style */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all animate-fade-in-up"
            style={{ animationDelay: `${idx * 80}ms` }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <stat.icon className="text-amber-400" size={20} />
              </div>
              <span className="text-xs text-gray-400 uppercase tracking-wide">{stat.label}</span>
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      <SectionCard title="ETL Runs" subtitle="최근 ETL 작업 로그">
        <DataTable
          columns={[
            { key: "job_name", label: "Job" },
            { key: "status", label: "상태" },
            { key: "started_at", label: "시작" },
            { key: "ended_at", label: "종료" },
            { key: "message", label: "메시지" },
          ]}
          rows={runs.etl}
          emptyMessage="ETL 실행 이력 없음"
        />
      </SectionCard>

      <SectionCard title="Forecast Runs" subtitle="예측 모델 실행 이력">
        <DataTable
          columns={[
            { key: "run_id", label: "Run" },
            { key: "model_name", label: "모델" },
            { key: "status", label: "상태" },
            { key: "started_at", label: "시작" },
            { key: "ended_at", label: "종료" },
          ]}
          rows={runs.forecast.map((f) => ({
            run_id: f.run_id,
            model_name: f.model_name,
            status: f.status,
            started_at: f.started_at,
            ended_at: f.ended_at,
          }))}
          emptyMessage="Forecast 실행 이력 없음"
        />
      </SectionCard>

      <SectionCard title="Policy Runs" subtitle="재고 정책 실행 결과">
        <DataTable
          columns={[
            { key: "run_id", label: "Run" },
            { key: "product_key", label: "상품" },
            { key: "as_of", label: "기준일" },
            { key: "reorder_point", label: "ROP" },
            { key: "safety_stock", label: "SS" },
            { key: "recommended_qty", label: "추천수량" },
          ]}
          rows={runs.policy.map((p) => ({
            ...p,
            reorder_point: p.reorder_point != null ? p.reorder_point.toFixed(0) : null,
            safety_stock: p.safety_stock != null ? p.safety_stock.toFixed(0) : null,
            recommended_qty: p.recommended_qty != null ? p.recommended_qty.toFixed(0) : null,
          }))}
          emptyMessage="Policy 실행 이력 없음"
        />
      </SectionCard>
    </div>
  );
}
