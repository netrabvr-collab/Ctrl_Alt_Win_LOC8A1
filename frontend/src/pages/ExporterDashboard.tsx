import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { fetchExporterDashboard, fetchSafeExportRegions, type ExporterDashboardData, type SafeRegion } from "@/lib/api";
import DashboardLayout from "@/components/DashboardLayout";
import StatCard from "@/components/StatCard";
import { TrendingUp, Award, BarChart3, Shield, Loader2, Globe, AlertTriangle, CheckCircle } from "lucide-react";

const riskColor = (level: string) => {
  switch (level.toLowerCase()) {
    case "low": return "bg-success/10 text-success";
    case "medium": return "bg-warning/10 text-warning";
    case "high": return "bg-destructive/10 text-destructive";
    default: return "bg-muted text-muted-foreground";
  }
};

const riskIcon = (level: string) => {
  switch (level.toLowerCase()) {
    case "low": return <CheckCircle className="w-4 h-4" />;
    case "medium": return <AlertTriangle className="w-4 h-4" />;
    case "high": return <Shield className="w-4 h-4" />;
    default: return <Globe className="w-4 h-4" />;
  }
};

const ExporterDashboard = () => {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<ExporterDashboardData | null>(null);
  const [regions, setRegions] = useState<SafeRegion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [d, r] = await Promise.all([fetchExporterDashboard(), fetchSafeExportRegions()]);
        setDashboard(d);
        setRegions(r);
      } catch {
        // Demo fallback
        setDashboard({ lead_score: 87, rank: 3, percentile: 92, industry: user!.industry, company_name: user!.username });
        setRegions([
          { region: "Southeast Asia", risk_level: "Low", trade_volume: 245000 },
          { region: "Western Europe", risk_level: "Low", trade_volume: 198000 },
          { region: "North America", risk_level: "Low", trade_volume: 312000 },
          { region: "South America", risk_level: "Medium", trade_volume: 87000 },
          { region: "Central Africa", risk_level: "High", trade_volume: 34000 },
        ]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user]);

  if (loading) {
    return (
      <DashboardLayout requiredRole="exporter">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout requiredRole="exporter">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">Exporter Dashboard</h1>
          <p className="text-muted-foreground mt-1">Your performance metrics and safe trade regions</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Lead Score" value={dashboard?.lead_score ?? "—"} icon={<TrendingUp className="w-4 h-4 text-primary" />} accent />
          <StatCard label="Rank" value={`#${dashboard?.rank ?? "—"}`} icon={<Award className="w-4 h-4 text-primary" />} />
          <StatCard label="Percentile" value={`${dashboard?.percentile ?? "—"}%`} icon={<BarChart3 className="w-4 h-4 text-primary" />} />
          <StatCard label="Industry" value={dashboard?.industry ?? "—"} icon={<Globe className="w-4 h-4 text-primary" />} />
        </div>

        <div className="bg-card rounded-xl border border-border shadow-card overflow-hidden">
          <div className="p-5 border-b border-border">
            <h2 className="text-lg font-semibold text-card-foreground flex items-center gap-2">
              <Shield className="w-5 h-5 text-secondary" />
              Safe Export Regions
            </h2>
          </div>
          <div className="divide-y divide-border">
            {Array.isArray(regions) &&
  regions.map((r, i) => (
    <div
      key={i}
      className="flex items-center justify-between px-5 py-4 hover:bg-accent/50 transition-colors"
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-8 h-8 rounded-lg flex items-center justify-center ${riskColor(
            r.risk_level
          )}`}
        >
          {riskIcon(r.risk_level)}
        </div>
        <div>
          <p className="font-medium text-card-foreground">
            {r.region}
          </p>
          <p className="text-xs text-muted-foreground">
            Trade Vol: ${r.trade_volume?.toLocaleString?.() ?? 0}
          </p>
        </div>
      </div>

      <span
        className={`text-xs font-semibold px-3 py-1 rounded-full ${riskColor(
          r.risk_level
        )}`}
      >
        {r.risk_level} Risk
      </span>
    </div>
  ))}

          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ExporterDashboard;