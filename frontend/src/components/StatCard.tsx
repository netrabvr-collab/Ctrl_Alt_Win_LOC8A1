import type { ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  accent?: boolean;
}

const StatCard = ({ label, value, icon, accent }: StatCardProps) => (
  <div className={`rounded-xl p-5 shadow-card border transition-all hover:shadow-elevated ${accent ? "gradient-primary text-primary-foreground border-transparent" : "bg-card text-card-foreground border-border"}`}>
    <div className="flex items-center justify-between mb-3">
      <span className={`text-sm font-medium ${accent ? "text-primary-foreground/80" : "text-muted-foreground"}`}>{label}</span>
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${accent ? "bg-primary-foreground/15" : "bg-accent"}`}>
        {icon}
      </div>
    </div>
    <p className="text-2xl font-bold tracking-tight">{value}</p>
  </div>
);

export default StatCard;
