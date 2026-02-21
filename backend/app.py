from fastapi import FastAPI
from pydantic import BaseModel
from model import generate_lead_scores
import pandas as pd
import numpy as np

app = FastAPI(
    title="TradeSwipe API",
    description="AI-driven Export Lead Scoring System",
    version="1.0.0"
)


# -----------------------------
# Buyer Input Model (User Input)
# -----------------------------
class BuyerRequest(BaseModel):
    industry: str
    required_quantity: float
    budget_usd: float
    risk_tolerance: str
    intent_score: float


@app.get("/")
def home():
    return {"message": "TradeSwipe AI Backend Running 🚀"}


# -----------------------------
# Get All Leads
# -----------------------------
@app.get("/lead-scores")
def get_lead_scores():
    df = generate_lead_scores()
    return df.to_dict(orient="records")


# -----------------------------
# Get Top N Leads
# -----------------------------
@app.get("/top-leads")
def get_top_leads(limit: int = 5):
    df = generate_lead_scores()
    return df.head(limit).to_dict(orient="records")


# -----------------------------
# Filter by Industry
# -----------------------------
@app.get("/filter-industry")
def filter_by_industry(industry: str):
    df = generate_lead_scores()
    filtered = df[df["Industry"].str.lower() == industry.lower()]
    return filtered.to_dict(orient="records")


# -----------------------------
# Filter by State
# -----------------------------
@app.get("/filter-state")
def filter_by_state(state: str):
    df = generate_lead_scores()
    filtered = df[df["State"].str.lower() == state.lower()]
    return filtered.to_dict(orient="records")


# -----------------------------
# NEW: AI Matchmaking (Live Input)
# -----------------------------
@app.post("/match-live")
def match_live(buyer: BuyerRequest):

    exporters = generate_lead_scores()

    # Industry filtering (case insensitive)
    candidates = exporters[
        exporters["Industry"].str.contains(buyer.industry, case=False, na=False)
    ].copy()

    if candidates.empty:
        return {"message": "No exporters found for this industry"}

    # Quantity compatibility
    if "Quantity_Tons" in exporters.columns:
        candidates["quantity_diff"] = abs(
            candidates["Quantity_Tons"] - buyer.required_quantity
        )
        candidates["quantity_score"] = 1 / (1 + candidates["quantity_diff"])
    else:
        candidates["quantity_score"] = 0.5

    # Intent alignment
    candidates["intent_alignment"] = buyer.intent_score / 100

    # Risk factor (simple adjustment)
    risk_map = {"Low": 0.2, "Medium": 0.1, "High": 0.0}
    risk_penalty = risk_map.get(buyer.risk_tolerance, 0.1)

    # Final match score
    candidates["match_score"] = (
        0.50 * candidates["lead_score"] +
        0.30 * candidates["quantity_score"] * 100 +
        0.20 * candidates["intent_alignment"] * 100
    ) * (1 - risk_penalty)

    candidates = candidates.sort_values(
        "match_score", ascending=False
    ).head(5)

    return candidates.to_dict(orient="records")
