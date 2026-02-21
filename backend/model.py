import pandas as pd
import joblib
from pathlib import Path

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "trade_data_processed_cleaned.csv"
NEWS_PATH = BASE_DIR / "news_data.csv"
MODEL_PATH = BASE_DIR / "lead_model.pkl"

# -------------------------
# Load Model
# -------------------------
if not MODEL_PATH.exists():
    raise FileNotFoundError("Run train_model.py first.")

model = joblib.load(MODEL_PATH)

# -------------------------
# Generate Lead Scores
# -------------------------
def generate_lead_scores():

    df = pd.read_csv(DATA_PATH)

    features = [
        "Intent_Score",
        "Shipment_Value_USD",
        "Quantity_Tons",
        "Prompt_Response_Score",
        "SalesNav_ProfileViews",
        "Tariff_Impact",
        "War_Risk",
        "Currency_Shift"
    ]

    X = df[features]
    probabilities = model.predict_proba(X)[:, 1]
    df["lead_score"] = probabilities * 100

    # Categorization
    def categorize(score):
        if score >= 75:
            return "High Potential"
        elif score >= 40:
            return "Medium Potential"
        else:
            return "Low Potential"

    df["lead_category"] = df["lead_score"].apply(categorize)

    # AI Reason (vectorized basic logic)
    df["ai_reason"] = "Balanced Performance"

    df.loc[df["Intent_Score"] > df["Intent_Score"].quantile(0.65),
           "ai_reason"] = "High Buyer Intent"

    df.loc[df["Prompt_Response_Score"] > df["Prompt_Response_Score"].median(),
           "ai_reason"] += ", Strong Responsiveness"

    df.loc[df["SalesNav_ProfileViews"] > df["SalesNav_ProfileViews"].median(),
           "ai_reason"] += ", High Engagement"

    final_df = df[[
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
        "Quantity_Tons",
        "lead_score",
        "lead_category",
        "ai_reason"
    ]].sort_values(by="lead_score", ascending=False)

    return final_df


# -------------------------
# Feature Importance
# -------------------------
def get_feature_importance():

    features = [
        "Intent_Score",
        "Shipment_Value_USD",
        "Quantity_Tons",
        "Prompt_Response_Score",
        "SalesNav_ProfileViews",
        "Tariff_Impact",
        "War_Risk",
        "Currency_Shift"
    ]

    return pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_
    }).sort_values(by="importance", ascending=False)


# -------------------------
# Exporter Dashboard
# -------------------------
def get_exporter_dashboard(exporter_id):

    df = generate_lead_scores()

    if exporter_id not in df["Exporter_ID"].values:
        return None

    df = df.sort_values(by="lead_score", ascending=False).reset_index(drop=True)

    row_index = df.index[df["Exporter_ID"] == exporter_id]

    if len(row_index) == 0:
        return None

    idx = int(row_index[0])  # convert to Python int
    rank = int(idx + 1)
    total = int(len(df))
    percentile = float(round((1 - (rank / total)) * 100, 2))

    row = df.iloc[idx]

    return {
        "Exporter_ID": str(exporter_id),
        "lead_score": float(round(row["lead_score"], 2)),
        "lead_category": str(row["lead_category"]),
        "ai_reason": str(row["ai_reason"]),
        "rank": rank,
        "total_exporters": total,
        "percentile": percentile
    }


# -------------------------
# Safe Export Regions
# -------------------------
def recommend_safe_regions(exporter_id):

    trade_df = pd.read_csv(DATA_PATH)

    if exporter_id not in trade_df["Exporter_ID"].values:
        return None

    exporter = trade_df[trade_df["Exporter_ID"] == exporter_id].iloc[0]
    industry = exporter["Industry"]

    news_df = pd.read_csv(NEWS_PATH)

    industry_news = news_df[
        news_df["Affected_Industry"].str.lower() == industry.lower()
    ].copy()

    if industry_news.empty:
        return {"message": "No regional risk data available."}

    industry_news["risk_score"] = (
        0.35 * abs(industry_news["Tariff_Change"]) +
        0.30 * industry_news["War_Flag"] +
        0.20 * industry_news["Natural_Calamity_Flag"] +
        0.15 * abs(industry_news["Currency_Shift"])
    )

    recommendations = industry_news.groupby("Region").mean(numeric_only=True).reset_index()
    recommendations = recommendations.sort_values(by="risk_score").head(5)

    return recommendations[[
        "Region",
        "risk_score",
        "Tariff_Change",
        "War_Flag",
        "Currency_Shift"
    ]].to_dict(orient="records")
