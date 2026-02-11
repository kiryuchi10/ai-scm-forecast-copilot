import { AlertCircle } from "lucide-react";

const ERROR_LABELS: Record<string, string> = {
  database_connection: "DB 연결 실패",
  table_not_found: "테이블 없음",
  schema_error: "스키마 오류",
  data_error: "데이터 오류",
  server_error: "서버 오류",
};

type Props = {
  message: string;
  errorType?: string;
  onRetry?: () => void;
};

export default function ErrorPanel({ message, errorType, onRetry }: Props) {
  const label = errorType ? ERROR_LABELS[errorType] ?? errorType : "오류";
  return (
    <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-sm text-red-200">
      <div className="flex items-center gap-2 mb-2">
        <AlertCircle size={20} className="text-red-400" />
        <span className="font-medium">{label}</span>
      </div>
      <p>{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 px-4 py-2 rounded-xl bg-amber-500/20 text-amber-400 hover:bg-amber-500/30 font-medium border border-amber-500/30 transition"
        >
          다시 시도
        </button>
      )}
    </div>
  );
}
