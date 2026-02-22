from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from model import (
    generate_lead_scores,
    get_feature_importance,
    get_exporter_dashboard,
    recommend_safe_regions
)
from matchmaking import generate_matches


# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI()

# Enable CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("trade_data_processed_cleaned.csv")


# -----------------------------
# Request Models
# -----------------------------
class BuyerRequest(BaseModel):
    industry: str
    required_quantity: float
    budget: float              # MUST match frontend
    risk_tolerance: str
    intent_score: float


# -----------------------------
# Basic Route
# -----------------------------
@app.get("/")
def home():
    return {"message": "TradeSwipe AI Running 🚀"}


# -----------------------------
# Industries
# -----------------------------
@app.get("/industries")
def get_industries():
    industries = df["industry"].dropna().unique().tolist()

    return [
        {"id": str(i), "name": industry}
        for i, industry in enumerate(industries)
    ]


# -----------------------------
# Lead Scores
# -----------------------------
@app.get("/lead-scores")
def lead_scores(limit: int = 50):
    data = generate_lead_scores()
    return data.head(limit).to_dict(orient="records")


# -----------------------------
# Feature Importance
# -----------------------------
@app.get("/feature-importance")
def feature_importance():
    return get_feature_importance().to_dict(orient="records")


# -----------------------------
# Exporter Dashboard
# (FIXED 422 by making exporter_id optional)
# -----------------------------
@app.get("/exporter-dashboard")
def exporter_dashboard(exporter_id: str = "EXP001"):
    result = get_exporter_dashboard(exporter_id)
    if result is None:
        return {"message": "Exporter not found."}
    return result


# -----------------------------
# Safe Export Regions
# (FIXED 422 by making exporter_id optional)
# -----------------------------
@app.get("/safe-export-regions")
def safe_export_regions(exporter_id: str = "EXP001"):
    result = recommend_safe_regions(exporter_id)
    if result is None:
        return {"message": "Exporter not found."}
    return result


# -----------------------------
# Live Matchmaking
# -----------------------------
@app.post("/match-live")
def match_live(buyer: BuyerRequest):

    exporters = generate_lead_scores()

    # Filter by industry
    candidates = exporters[
        exporters["Industry"].str.contains(buyer.industry, case=False, na=False)
    ].copy()
    candidates = exporters[
    exporters["Industry"].str.strip().str.lower() ==
    buyer.industry.strip().lower()
].copy()


    if candidates.empty:
        return []

    # Quantity match score
    candidates["quantity_diff"] = abs(
        candidates["Quantity_Tons"] - buyer.required_quantity
    )
    candidates["quantity_score"] = 1 / (1 + candidates["quantity_diff"])

    # Intent alignment
    candidates["intent_alignment"] = buyer.intent_score / 100

    # Risk adjustment
    risk_map = {"Low": 0.05, "Medium": 0.10, "High": 0.20}
    risk_penalty = risk_map.get(buyer.risk_tolerance, 0.10)

    # Final match score
    candidates["match_score"] = (
        0.5 * candidates["lead_score"] +
        0.3 * candidates["quantity_score"] * 100 +
        0.2 * candidates["intent_alignment"] * 100
    ) * (1 - risk_penalty)

    return candidates.sort_values(
        by="match_score", ascending=False
    ).head(5).to_dict(orient="records")


# -----------------------------
# Matchmaking Endpoint (FIXED Flask issue)
# -----------------------------
@app.get("/matchmaking")
def matchmaking():

    exporter = {
        "industry": "Automotive",
        "trade_volume": 200000,
        "lead_score": 87
    }

    buyers = [
        {
            "name": "AutoParts GmbH",
            "region": "Western Europe",
            "industry": "Automotive",
            "risk_level": "Low",
            "trade_volume": 250000,
            "success_rate": 14
        },
        {
            "name": "Nippon Motors Trade",
            "region": "Southeast Asia",
            "industry": "Automotive",
            "risk_level": "Low",
            "trade_volume": 180000,
            "success_rate": 12
        },
        {
            "name": "Central Auto Export",
            "region": "Central Africa",
            "industry": "Automotive",
            "risk_level": "High",
            "trade_volume": 40000,
            "success_rate": 5
        }
    ]

    matches = generate_matches(exporter, buyers)

    return matches
