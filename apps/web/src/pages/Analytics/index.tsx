import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { fetchTrends, fetchBreakdown } from "@/services/analytics";
import PageHeader from "@/components/common/PageHeader";
import SectionCard from "@/components/cards/SectionCard";
import TrendChart from "@/components/charts/TrendChart";
import DataTable from "@/components/tables/DataTable";
import LoadingSkeleton from "@/components/common/LoadingSkeleton";
import ErrorPanel from "@/components/common/ErrorPanel";

const METRIC_OPTIONS = [
  { value: "revenue", label: "매출" },
  { value: "orders", label: "주문수" },
  { value: "late_rate", label: "지연율" },
];
const BY_OPTIONS = [
  { value: "region", label: "지역" },
  { value: "category", label: "카테고리" },
  { value: "department", label: "부서" },
  { value: "shipping_mode", label: "배송방식" },
];
const DAYS_OPTIONS = [
  { value: 7, label: "7d" },
  { value: 90, label: "90d" },
  { value: 180, label: "180d" },
  { value: 365, label: "365d" },
];

export default function AnalyticsPage() {
  const [metric, setMetric] = useState("revenue");
  const [days, setDays] = useState(180);
  const [by, setBy] = useState("region");

  const trendsQuery = useQuery({
    queryKey: ["analytics", "trends", metric, days],
    queryFn: () => fetchTrends(metric, days),
  });
  const breakdownQuery = useQuery({
    queryKey: ["analytics", "breakdown", by, days, metric],
    queryFn: () => fetchBreakdown(by, days, metric),
  });

  const loading = trendsQuery.isLoading || breakdownQuery.isLoading;
  const error = trendsQuery.error || breakdownQuery.error;

  if (loading) return <LoadingSkeleton />;
  if (error) {
    const err = error as Error & { errorType?: string };
    return (
      <ErrorPanel
        message={err instanceof Error ? err.message : "데이터를 불러올 수 없습니다."}
        errorType={err.errorType}
        onRetry={() => {
          trendsQuery.refetch();
          breakdownQuery.refetch();
        }}
      />
    );
  }

  const trends = trendsQuery.data!;
  const breakdown = breakdownQuery.data!;

  const breakdownChartData = breakdown.items.slice(0, 12).map((i) => ({
    name: i.key || "—",
    value: i.value,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics Dashboard"
        subtitle="트렌드·세그먼트 분석 (실데이터)"
      />

      {/* Time range + metric - analytics-dashboard style */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-gray-400">기간</span>
        {DAYS_OPTIONS.map((o) => (
          <button
            key={o.value}
            onClick={() => setDays(o.value)}
            className={
              "px-4 py-2 text-sm font-medium rounded-xl transition " +
              (days === o.value
                ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                : "bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600 hover:text-gray-200")
            }
          >
            {o.label}
          </button>
        ))}
        <span className="text-sm text-gray-400 ml-2">지표</span>
        <select
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm text-gray-200 focus:border-amber-500/50 outline-none"
        >
          {METRIC_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <SectionCard title="Trend" subtitle={`일별 ${METRIC_OPTIONS.find((m) => m.value === metric)?.label ?? metric}`}>
        <TrendChart series={trends.series} metric={trends.metric} height={280} />
      </SectionCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="Breakdown" subtitle={`${BY_OPTIONS.find((b) => b.value === by)?.label ?? by}별`}>
          <div className="mb-4">
            <select
              value={by}
              onChange={(e) => setBy(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm text-gray-200 focus:border-amber-500/50 outline-none"
            >
              {BY_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          {breakdownChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={breakdownChartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: 11 }} />
                <YAxis stroke="#6b7280" style={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111827",
                    border: "1px solid #374151",
                    borderRadius: "12px",
                    color: "#f3f4f6",
                  }}
                />
                <Bar dataKey="value" fill="#f59e0b" radius={[6, 6, 0, 0]} name="값" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 py-4">데이터 없음</p>
          )}
        </SectionCard>

        <SectionCard title="Breakdown 테이블" subtitle="상세 목록">
          <DataTable
            columns={[{ key: "key", label: by }, { key: "value", label: "값" }]}
            rows={breakdown.items.map((i) => ({
              key: i.key || "—",
              value: typeof i.value === "number" && i.value % 1 !== 0 ? i.value.toFixed(2) : String(i.value),
            }))}
            emptyMessage="데이터 없음"
          />
        </SectionCard>
      </div>
    </div>
  );
}
