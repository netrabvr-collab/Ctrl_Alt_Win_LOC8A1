from fastapi import FastAPI
from pydantic import BaseModel
from model import (
    generate_lead_scores,
    get_feature_importance,
    get_exporter_dashboard,
    recommend_safe_regions
)

app = FastAPI(
    title="TradeSwipe AI Platform",
    version="2.0"
)

# -----------------------------
# Buyer Model
# -----------------------------
class BuyerRequest(BaseModel):
    industry: str
    required_quantity: float
    budget_usd: float
    risk_tolerance: str
    intent_score: float


@app.get("/")
def home():
    return {"message": "TradeSwipe AI Running 🚀"}


@app.get("/lead-scores")
def lead_scores(limit: int = 50):
    df = generate_lead_scores()
    return df.head(limit).to_dict(orient="records")


@app.get("/feature-importance")
def feature_importance():
    return get_feature_importance().to_dict(orient="records")


@app.get("/exporter-dashboard")
def exporter_dashboard(exporter_id: str):
    result = get_exporter_dashboard(exporter_id)
    if result is None:
        return {"message": "Exporter not found."}
    return result


@app.get("/safe-export-regions")
def safe_export_regions(exporter_id: str):
    result = recommend_safe_regions(exporter_id)
    if result is None:
        return {"message": "Exporter not found."}
    return result


@app.post("/match-live")
def match_live(buyer: BuyerRequest):

    exporters = generate_lead_scores()

    candidates = exporters[
        exporters["Industry"].str.contains(buyer.industry, case=False, na=False)
    ].copy()

    if candidates.empty:
        return {"message": "No exporters found."}

    candidates["quantity_diff"] = abs(
        candidates["Quantity_Tons"] - buyer.required_quantity
    )
    candidates["quantity_score"] = 1 / (1 + candidates["quantity_diff"])

    candidates["intent_alignment"] = buyer.intent_score / 100

    risk_map = {"Low": 0.05, "Medium": 0.10, "High": 0.20}
    risk_penalty = risk_map.get(buyer.risk_tolerance, 0.10)

    candidates["match_score"] = (
        0.5 * candidates["lead_score"] +
        0.3 * candidates["quantity_score"] * 100 +
        0.2 * candidates["intent_alignment"] * 100
    ) * (1 - risk_penalty)

    return candidates.sort_values(
        by="match_score", ascending=False
    ).head(5).to_dict(orient="records")