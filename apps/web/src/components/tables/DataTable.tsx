type Col = { key: string; label: string };
type Props = {
  columns: Col[];
  rows: Record<string, string | number | null | undefined>[];
  emptyMessage?: string;
};

export default function DataTable({ columns, rows, emptyMessage = "데이터 없음" }: Props) {
  if (rows.length === 0) {
    return <p className="text-sm text-gray-400 py-4">{emptyMessage}</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            {columns.map((c) => (
              <th
                key={c.key}
                className="text-left py-3 px-2 font-medium text-gray-400 uppercase tracking-wider text-xs"
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
              {columns.map((c) => (
                <td key={c.key} className="py-3 px-2 text-gray-200">
                  {row[c.key] ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
