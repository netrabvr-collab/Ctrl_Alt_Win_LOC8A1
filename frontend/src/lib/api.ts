import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

export interface Industry {
  id: string;
  name: string;
}

export interface MatchResult {
  exporter_name: string;
  lead_score: number;
  rank: number;
  industry: string;
  region: string;
  match_percentage: number;
}

export interface ExporterDashboardData {
  lead_score: number;
  rank: number;
  percentile: number;
  industry: string;
  company_name: string;
}

export interface SafeRegion {
  region: string;
  risk_level: string;
  trade_volume: number;
}

export const fetchIndustries = async (): Promise<Industry[]> => {
  const { data } = await api.get("/industries");
  return data;
};

export const matchLive = async (payload: {
  industry: string;
  required_quantity: number;
  budget: number;
  risk_tolerance: string;
  intent_score: number;
}): Promise<MatchResult[]> => {
  const { data } = await api.post("/match-live", payload);
  return data;
};

export const fetchExporterDashboard = async (): Promise<ExporterDashboardData> => {
  const { data } = await api.get("/exporter-dashboard");
  return data;
};

export const fetchSafeExportRegions = async (): Promise<SafeRegion[]> => {
  const { data } = await api.get("/safe-export-regions");
  return data;
};

export default api;