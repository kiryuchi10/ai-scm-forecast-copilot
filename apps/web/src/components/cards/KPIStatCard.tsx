import type { LucideIcon } from "lucide-react";

type Props = {
  title: string;
  value: string | number;
  delta?: string;
  icon?: LucideIcon;
  trend?: "up" | "down";
};

export default function KPIStatCard({ title, value, delta, icon: Icon, trend }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all">
      <div className="flex items-start justify-between mb-3">
        {Icon && (
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <Icon className="text-amber-400" size={20} />
          </div>
        )}
        {delta != null && (
          <span
            className={
              "text-xs font-medium " +
              (trend === "down" ? "text-red-400" : "text-amber-400")
            }
          >
            {delta}
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{title}</div>
    </div>
  );
}
