import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/lib/auth-context";

import Login from "./pages/Login";
import MatchHistory from "./pages/MatchHistory";
import Matchmaking from "./pages/Matchmaking";
import SafeRegions from "./pages/SafeRegions";
import ExporterDashboard from "./pages/ExporterDashboard";
import NotFound from "./pages/NotFound";
import ImporterDashboard from "./pages/ImporterDashboard";



const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/exporter" element={<ExporterDashboard />} />
            
            <Route path="/safe-regions" element={<SafeRegions />} />
            <Route path="/match-history" element={<MatchHistory />} />
            <Route path="/importer" element={<ImporterDashboard />} />
            <Route path="/matchmaking" element={<Matchmaking />} />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
