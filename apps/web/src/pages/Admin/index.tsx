import { useQuery } from "@tanstack/react-query";
import { Users, Server, Database, Activity, Shield } from "lucide-react";
import PageHeader from "@/components/common/PageHeader";
import SectionCard from "@/components/cards/SectionCard";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import ErrorPanel from "@/components/common/ErrorPanel";
import { fetchAdminSummary } from "@/services/admin";

export default function AdminPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["admin", "summary"],
    queryFn: fetchAdminSummary,
  });

  const dbDisplay =
    data?.db_status === "connected"
      ? "연결됨"
      : data?.db_status?.includes("Unknown database")
        ? "DB 'scmcore' 없음"
        : data?.db_status?.includes("Can't connect")
          ? "MySQL 미실행"
          : data?.db_status ?? "—";

  const stats = data
    ? [
        { icon: Users, label: "총 사용자", value: String(data.user_count), sub: "GET /api/admin/summary" },
        { icon: Server, label: "서버 상태", value: data.server_status, sub: "API" },
        { icon: Database, label: "DB", value: dbDisplay, sub: data.db_status === "connected" ? "API" : "아래 조치 참고" },
        { icon: Activity, label: "감사 이벤트", value: String(data.audit_events), sub: "API" },
      ]
    : [
        { icon: Users, label: "총 사용자", value: "—", sub: "로딩 중" },
        { icon: Server, label: "서버 상태", value: "—", sub: "로딩 중" },
        { icon: Database, label: "DB", value: "—", sub: "로딩 중" },
        { icon: Activity, label: "감사 이벤트", value: "—", sub: "로딩 중" },
      ];

  if (isLoading) return <LoadingSkeleton />;
  if (error) {
    const err = error as Error & { errorType?: string };
    return (
      <ErrorPanel
        message={err instanceof Error ? err.message : "Admin 요약을 불러올 수 없습니다."}
        errorType={err.errorType}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Admin Dashboard"
        subtitle="시스템 관리·모니터링 (API 연동 실데이터)"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="bg-gray-900 border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-all animate-fade-in-up"
            style={{ animationDelay: `${idx * 80}ms` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <stat.icon className="text-amber-400" size={24} />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-white mb-1">{stat.value}</h3>
            <p className="text-sm text-gray-400 mb-1">{stat.label}</p>
            <span className="text-xs text-amber-400/80">{stat.sub}</span>
          </div>
        ))}
      </div>

      <SectionCard title="Admin Summary" subtitle="사용자·역할·감사 로그">
        <div className="flex items-center gap-3 p-4 bg-gray-800/50 rounded-xl border border-gray-700">
          <Shield className="text-amber-400 flex-shrink-0" size={24} />
          <div className="space-y-2">
            <p className="text-gray-200">
              사용자 수·서버/DB 상태는 <strong>GET /api/admin/summary</strong> 실데이터입니다.
              users 테이블이 있으면 사용자 수가 표시되고, 없으면 0입니다.
            </p>
            {data?.db_status !== "connected" && (
              <p className="text-amber-400/90 text-sm">
                DB가 없거나 연결 실패 시: MySQL 기동 후 <code className="bg-gray-800 px-1 rounded">db/01_init.sql</code> → <code className="bg-gray-800 px-1 rounded">db/02_schema.sql</code> 실행.
              </p>
            )}
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
