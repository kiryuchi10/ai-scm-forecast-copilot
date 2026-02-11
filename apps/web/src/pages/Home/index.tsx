import { useQuery } from "@tanstack/react-query";
import { DollarSign, ShoppingCart, AlertTriangle, Clock } from "lucide-react";
import { fetchKpiSummary } from "@/services/kpi";
import KPIStatCard from "@/components/cards/KPIStatCard";
import SectionCard from "@/components/cards/SectionCard";
import PageHeader from "@/components/common/PageHeader";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import ErrorPanel from "@/components/common/ErrorPanel";
import DataTable from "@/components/tables/DataTable";

function formatRevenue(n: number) {
  if (n >= 1e6) return `₩${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `₩${(n / 1e3).toFixed(0)}K`;
  return `₩${n.toFixed(0)}`;
}

export default function HomePage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["kpi", "summary"],
    queryFn: fetchKpiSummary,
  });

  if (isLoading) return <LoadingSkeleton />;
  if (error) {
    const err = error as Error & { errorType?: string };
    return (
      <ErrorPanel
        message={err instanceof Error ? err.message : "KPI를 불러올 수 없습니다."}
        errorType={err.errorType}
        onRetry={() => refetch()}
      />
    );
  }

  if (!data || typeof data.total_revenue !== "number") {
    return (
      <ErrorPanel
        message="KPI 데이터를 불러오지 못했습니다. (응답 형식 오류 또는 데이터 없음)"
        onRetry={() => refetch()}
      />
    );
  }

  const kpi = data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Home (Unified)"
        subtitle="KPI·Top 상품·지연 주문 요약 (실데이터)"
      />

      {/* KPI Cards - portfolio/analytics style */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="animate-fade-in-up" style={{ animationDelay: "0ms" }}>
          <KPIStatCard
            title="Total Revenue"
            value={formatRevenue(kpi.total_revenue)}
            icon={DollarSign}
          />
        </div>
        <div className="animate-fade-in-up" style={{ animationDelay: "80ms" }}>
          <KPIStatCard
            title="Orders"
            value={kpi.total_orders.toLocaleString()}
            icon={ShoppingCart}
          />
        </div>
        <div className="animate-fade-in-up" style={{ animationDelay: "160ms" }}>
          <KPIStatCard
            title="Late Rate"
            value={`${(kpi.late_rate * 100).toFixed(1)}%`}
            icon={AlertTriangle}
          />
        </div>
        <div className="animate-fade-in-up" style={{ animationDelay: "240ms" }}>
          <KPIStatCard
            title="Last Updated"
            value={kpi.last_updated?.slice(0, 10) ?? "—"}
            icon={Clock}
          />
        </div>
      </div>

      {/* Two columns: Top Products / Top Late Orders - portfolio style */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard
          title="Top Products"
          subtitle="매출 상위 상품"
        >
          <DataTable
            columns={[
              { key: "product_name", label: "상품" },
              { key: "revenue", label: "매출" },
              { key: "qty", label: "수량" },
            ]}
            rows={(kpi.top_products ?? []).map((p) => ({
              product_name: (p.product_name ?? "").slice(0, 40),
              revenue: formatRevenue(Number(p.revenue) || 0),
              qty: Number(p.qty) || 0,
            }))}
            emptyMessage="상품 데이터 없음"
          />
        </SectionCard>

        <SectionCard
          title="Top Late Orders"
          subtitle="지연 일수 상위 주문"
        >
          <DataTable
            columns={[
              { key: "order_key", label: "주문" },
              { key: "delay_days", label: "지연(일)" },
              { key: "shipping_mode", label: "배송" },
              { key: "delivery_status", label: "상태" },
            ]}
            rows={kpi.top_late_orders ?? []}
            emptyMessage="지연 주문 없음"
          />
        </SectionCard>
      </div>

      {/* Summary hints - analytics/project placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SectionCard title="Analytics Summary" subtitle="트렌드·세그먼트">
          <p className="text-sm text-gray-400">
            트렌드·세그먼트 요약은 Analytics 페이지에서 확인하세요.
          </p>
        </SectionCard>
        <SectionCard title="Project Summary" subtitle="ETL·Forecast·Policy">
          <p className="text-sm text-gray-400">
            ETL / Forecast / Policy 최근 실행은 Projects 페이지에서 확인하세요.
          </p>
        </SectionCard>
      </div>
    </div>
  );
}
