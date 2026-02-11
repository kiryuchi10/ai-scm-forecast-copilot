import { Outlet } from "react-router-dom";
import SideNav from "./SideNav";
import TopBar from "./TopBar";

export default function AppShell() {
  return (
    <div className="min-h-screen bg-gray-950 flex">
      <SideNav />
      <div className="flex-1 min-w-0">
        <TopBar />
        <main className="px-6 py-6 max-w-[1400px] mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
