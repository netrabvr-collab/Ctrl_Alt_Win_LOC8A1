from fastapi import FastAPI
from model import generate_lead_scores

app = FastAPI(
    title="TradeSwipe API",
    description="AI-driven Export Lead Scoring System",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "TradeSwipe AI Backend Running 🚀"}


# Get all ranked leads
@app.get("/lead-scores")
def get_lead_scores():
    df = generate_lead_scores()
    return df.to_dict(orient="records")


# Get top N leads
@app.get("/top-leads")
def get_top_leads(limit: int = 5):
    df = generate_lead_scores()
    top_df = df.head(limit)
    return top_df.to_dict(orient="records")


# Filter by Industry
@app.get("/filter-industry")
def filter_by_industry(industry: str):
    df = generate_lead_scores()
    filtered = df[df["Industry"] == industry]
    return filtered.to_dict(orient="records")


# Filter by State
@app.get("/filter-state")
def filter_by_state(state: str):
    df = generate_lead_scores()
    filtered = df[df["State"] == state]
    return filtered.to_dict(orient="records")