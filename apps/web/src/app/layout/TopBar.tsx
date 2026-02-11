import { Search, Bell, Settings } from "lucide-react";

export default function TopBar() {
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-gray-200 font-semibold">Dashboard</div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
            <input
              className="pl-9 pr-3 py-2 rounded-xl bg-gray-800 border border-gray-700 text-gray-200 placeholder-gray-500 outline-none text-sm w-48 focus:border-amber-500/50"
              placeholder="Search…"
            />
          </div>
          <button
            type="button"
            className="p-2 rounded-xl bg-gray-800 border border-gray-700 text-gray-400 hover:text-amber-400 hover:border-amber-500/30 transition"
            aria-label="알림"
          >
            <Bell size={18} />
          </button>
          <button
            type="button"
            className="p-2 rounded-xl bg-gray-800 border border-gray-700 text-gray-400 hover:text-amber-400 hover:border-amber-500/30 transition"
            aria-label="설정"
          >
            <Settings size={18} />
          </button>
          <div className="w-9 h-9 rounded-xl bg-amber-500 text-gray-950 flex items-center justify-center font-semibold text-sm">
            A
          </div>
        </div>
      </div>
    </header>
  );
}
