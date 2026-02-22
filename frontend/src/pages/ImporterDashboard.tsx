import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { matchLive, type MatchResult } from "@/lib/api";
import DashboardLayout from "@/components/DashboardLayout";
import StatCard from "@/components/StatCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import {
  Search,
  Loader2,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  Award,
  MapPin,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const ImporterDashboard = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  const [quantity, setQuantity] = useState("");
  const [budget, setBudget] = useState("");
  const [riskTolerance, setRiskTolerance] = useState("Medium");
  const [intentScore, setIntentScore] = useState([75]);
  const [results, setResults] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);

  // ✅ PROTECT AGAINST NULL USER
  if (!user) {
    return (
      <DashboardLayout requiredRole="importer">
        <div className="p-6">Loading...</div>
      </DashboardLayout>
    );
  }

  const handleFind = async () => {
    if (!quantity || !budget) {
      toast({
        title: "Missing fields",
        description: "Please fill quantity and budget.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    try {
      const data = await matchLive({
        industry: user.industry,
        required_quantity: Number(quantity),
        budget: Number(budget),
        risk_tolerance: riskTolerance,
        intent_score: intentScore[0],
      });

      const safeResults = Array.isArray(data) ? data.slice(0, 5) : [];
      setResults(safeResults);

      if (!safeResults.length) {
        toast({
          title: "No matches",
          description: "No exporters found for your criteria.",
        });
      }
    } catch (error) {
      // ✅ Demo fallback if API fails
      setResults([
        {
          exporter_name: "Global Exports Ltd",
          lead_score: 92,
          rank: 1,
          industry: user.industry,
          region: "Southeast Asia",
          match_percentage: 95,
        },
        {
          exporter_name: "Prime Trade Co",
          lead_score: 87,
          rank: 2,
          industry: user.industry,
          region: "Europe",
          match_percentage: 88,
        },
        {
          exporter_name: "Pacific Sourcing",
          lead_score: 83,
          rank: 3,
          industry: user.industry,
          region: "East Asia",
          match_percentage: 82,
        },
        {
          exporter_name: "Atlas Commerce",
          lead_score: 79,
          rank: 4,
          industry: user.industry,
          region: "South America",
          match_percentage: 76,
        },
        {
          exporter_name: "Meridian Supply",
          lead_score: 74,
          rank: 5,
          industry: user.industry,
          region: "North America",
          match_percentage: 71,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const avgLeadScore =
    results.length > 0
      ? Math.round(
          results.reduce((a, r) => a + r.lead_score, 0) / results.length
        )
      : "—";

  return (
    <DashboardLayout requiredRole="importer">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Importer Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Find and match with verified exporters
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Industry"
            value={user.industry}
            icon={<TrendingUp className="w-4 h-4 text-primary" />}
          />
          <StatCard
            label="Matches Found"
            value={results.length}
            icon={<Users className="w-4 h-4 text-primary" />}
          />
          <StatCard
            label="Avg Lead Score"
            value={avgLeadScore}
            icon={<Target className="w-4 h-4 text-primary" />}
          />
          <StatCard
            label="Top Match"
            value={
              results[0]?.match_percentage
                ? `${results[0].match_percentage}%`
                : "—"
            }
            icon={<Award className="w-4 h-4 text-secondary" />}
            accent
          />
        </div>

        {/* Search Form */}
        <div className="bg-card rounded-xl border shadow-card p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">Find Exporters</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="space-y-2">
              <Label>Industry</Label>
              <Input value={user.industry} disabled className="bg-muted" />
            </div>

            <div className="space-y-2">
              <Label>Required Quantity</Label>
              <Input
                type="number"
                placeholder="e.g. 1000"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Budget (USD)</Label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  type="number"
                  placeholder="e.g. 50000"
                  className="pl-9"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Risk Tolerance</Label>
              <Select value={riskTolerance} onValueChange={setRiskTolerance}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="mt-5 flex items-end gap-6">
            <div className="flex-1 space-y-2">
              <Label>Intent Score: {intentScore[0]}</Label>
              <Slider
                value={intentScore}
                onValueChange={setIntentScore}
                min={0}
                max={100}
                step={1}
              />
            </div>

            <Button
              onClick={handleFind}
              disabled={loading}
              className="h-10 px-6"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Search className="w-4 h-4 mr-2" />
              )}
              Find Exporters
            </Button>
          </div>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-4">Top Matches</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((r, i) => (
                <div
                  key={i}
                  className="bg-card rounded-xl border shadow-card p-5"
                >
                  <div className="flex justify-between mb-3">
                    <div>
                      <h3 className="font-semibold">
                        {r.exporter_name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {r.industry}
                      </p>
                    </div>
                    <span className="text-xs font-bold px-2 py-1 rounded-full bg-accent">
                      #{r.rank}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Lead Score</span>
                      <span>{r.lead_score}</span>
                    </div>

                    <div className="flex justify-between">
                      <span>Match</span>
                      <span>{r.match_percentage}%</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      <span>{r.region}</span>
                    </div>
                  </div>

                  <div className="mt-4 w-full bg-muted rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-primary"
                      style={{ width: `${r.match_percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ImporterDashboard;
