import pandas as pd
import joblib
from pathlib import Path

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "trade_data.xlsx"
MODEL_PATH = BASE_DIR / "lead_model.pkl"

# -------------------------
# Load Model Once
# -------------------------
if not MODEL_PATH.exists():
    raise FileNotFoundError("Trained model not found. Run train_model.py first.")

model = joblib.load(MODEL_PATH)


# -------------------------
# Generate AI Lead Scores
# -------------------------
def generate_lead_scores() -> pd.DataFrame:

    if not DATA_PATH.exists():
        raise FileNotFoundError("Dataset not found.")

    df = pd.read_excel(DATA_PATH)

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

    # Predict probability of Converted = 1
    probabilities = model.predict_proba(X)[:, 1]

    # Convert to 0–100 score
    df["lead_score"] = probabilities * 100

    # Categorize
    def categorize(score):
        if score >= 75:
            return "High Potential"
        elif score >= 40:
            return "Medium Potential"
        else:
            return "Low Potential"

    df["lead_category"] = df["lead_score"].apply(categorize)

    final_df = df[[
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
        "lead_score",
        "lead_category"
    ]].sort_values(by="lead_score", ascending=False)

    return final_df
def match_buyers_to_exporters(buyer_id: str) -> pd.DataFrame:

    buyers_path = BASE_DIR / "buyers.xlsx"

    if not buyers_path.exists():
        raise FileNotFoundError("buyers.xlsx not found.")

    buyers_df = pd.read_excel(buyers_path)

    if buyer_id not in buyers_df["Buyer_ID"].values:
        raise ValueError("Buyer ID not found.")

    buyer = buyers_df[buyers_df["Buyer_ID"] == buyer_id].iloc[0]

    # Get AI-scored exporters
    exporters = generate_lead_scores()

    # Merge with full dataset for additional fields
    full_df = pd.read_excel(DATA_PATH)
    exporters = exporters.merge(
        full_df[["Exporter_ID", "Industry", "State", "Revenue_Size_USD"]],
        on="Exporter_ID",
        how="left"
    )

    # Industry match score
    exporters["industry_match"] = (
        exporters["Industry"].str.lower() == buyer["Preferred_Industry"].lower()
    ).astype(int)

    # Revenue similarity score
    exporters["revenue_diff"] = abs(
        exporters["Revenue_Size_USD"] - buyer["Preferred_Revenue"]
    )

    max_diff = exporters["revenue_diff"].max()
    exporters["revenue_score"] = 1 - (exporters["revenue_diff"] / max_diff)

    # Final matchmaking score
    exporters["match_score"] = (
        0.5 * (exporters["lead_score"] / 100) +
        0.3 * exporters["industry_match"] +
        0.2 * exporters["revenue_score"]
    )

    result = exporters.sort_values(by="match_score", ascending=False)

    return result[[
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
        "lead_score",
        "match_score"
    ]].head(10)
