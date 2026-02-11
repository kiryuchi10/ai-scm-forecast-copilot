import { createBrowserRouter } from "react-router-dom";
import AppShell from "./layout/AppShell";
import HomePage from "@/pages/Home";
import AnalyticsPage from "@/pages/Analytics";
import ProjectsPage from "@/pages/Projects";
import AdminPage from "@/pages/Admin";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "projects", element: <ProjectsPage /> },
      { path: "admin", element: <AdminPage /> },
    ],
  },
]);
