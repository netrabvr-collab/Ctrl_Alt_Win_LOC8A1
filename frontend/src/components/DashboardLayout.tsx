import { useAuth } from "@/lib/auth-context";
import { Navigate } from "react-router-dom";
import AppSidebar from "./AppSidebar";
import type { ReactNode } from "react";

const DashboardLayout = ({ children, requiredRole }: { children: ReactNode; requiredRole: "importer" | "exporter" }) => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/" replace />;
  if (user.role !== requiredRole) return <Navigate to={`/${user.role}`} replace />;

  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  );
};

export default DashboardLayout;