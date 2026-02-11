import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Point = { dt: string; value: number };

type Props = {
  series: Point[];
  metric: string;
  height?: number;
};

export default function TrendChart({ series, metric, height = 220 }: Props) {
  if (series.length === 0) {
    return (
      <div
        className="text-sm text-gray-400 flex items-center justify-center"
        style={{ height }}
      >
        데이터 없음
      </div>
    );
  }

  const data = series.map((p) => ({ ...p, name: p.dt }));

  return (
    <div style={{ height }}>
      <div className="text-xs text-gray-400 mb-2">{metric}</div>
      <ResponsiveContainer width="100%" height={height - 28}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="dt"
            stroke="#6b7280"
            style={{ fontSize: 11 }}
            tickFormatter={(v) => (v && String(v).slice(0, 10)) || v}
          />
          <YAxis stroke="#6b7280" style={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#111827",
              border: "1px solid #374151",
              borderRadius: "12px",
              color: "#f3f4f6",
            }}
            labelFormatter={(v) => String(v).slice(0, 10)}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#f59e0b"
            strokeWidth={2}
            fill="url(#colorValue)"
            name="값"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
