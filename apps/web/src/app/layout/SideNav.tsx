import { NavLink, Link } from "react-router-dom";
import { LayoutDashboard, BarChart3, FolderKanban, Shield } from "lucide-react";

const nav = [
  { to: "/", label: "Home", icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/admin", label: "Admin", icon: Shield },
];

export default function SideNav() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800 sticky top-0 h-screen">
      <div className="p-5 border-b border-gray-800">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500 text-gray-950 flex items-center justify-center font-bold">
            SCM
          </div>
          <div className="leading-tight">
            <div className="font-bold text-white">SCM Copilot</div>
            <div className="text-xs text-gray-400">Forecast · Policy · AI</div>
          </div>
        </Link>
      </div>
      <nav className="p-3 space-y-1">
        {nav.map((x) => (
          <NavLink
            key={x.to}
            to={x.to}
            end={x.to === "/"}
            className={({ isActive }) =>
              "flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition " +
              (isActive
                ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                : "text-gray-400 hover:bg-gray-800 hover:text-gray-200 border border-transparent")
            }
          >
            <x.icon size={18} />
            {x.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
