import axios from "axios";

/**
 * Base Axios Instance
 * Make sure FastAPI is running on port 8000
 */
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/* ============================
   Interfaces
============================ */

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

/* ============================
   API CALLS
============================ */

/**
 * GET /industries
 */
export const fetchIndustries = async (): Promise<Industry[]> => {
  const { data } = await api.get("/industries");
  return data;
};

/**
 * POST /match-live
 */
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

/**
 * GET /exporter-dashboard?industry=XYZ
 * Fixes 422 error by sending required query param
 */
export const fetchExporterDashboard = async (
  industry: string
): Promise<ExporterDashboardData> => {
  const { data } = await api.get("/exporter-dashboard", {
    params: { industry },
  });
  return data;
};

/**
 * GET /safe-export-regions?industry=XYZ
 * Fixes 422 error by sending required query param
 */
export const fetchSafeExportRegions = async (
  industry: string
): Promise<SafeRegion[]> => {
  const { data } = await api.get("/safe-export-regions", {
    params: { industry },
  });
  return data;
};

/**
 * GET /matchmaking
 * IMPORTANT:
 * Use same backend (port 8000)
 * Remove localhost:5000 to avoid mixed backend
 */
export const getMatchmaking = async () => {
  const { data } = await api.get("/matchmaking");
  return data;
};

export default api;
