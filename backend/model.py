import pandas as pd
import joblib
from pathlib import Path

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "trade_data_processed_cleaned.csv"
MODEL_PATH = BASE_DIR / "lead_model.pkl"

# -------------------------
# Load Model
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

    # Predict probability of Converted = 1
    probabilities = model.predict_proba(X)[:, 1]

    # Convert to 0–100 score
    df["lead_score"] = probabilities * 100

    # -------------------------
    # Categorize Leads
    # -------------------------
    def categorize(score):
        if score >= 75:
            return "High Potential"
        elif score >= 40:
            return "Medium Potential"
        else:
            return "Low Potential"

    df["lead_category"] = df["lead_score"].apply(categorize)

    # -------------------------
    # AI Explanation Generator
    # -------------------------
    def generate_reason(row):
        reasons = []

        if row["Intent_Score"] > df["Intent_Score"].quantile(0.65):
            reasons.append("High Buyer Intent")

        if row["Prompt_Response_Score"] > df["Prompt_Response_Score"].median():
            reasons.append("Strong Responsiveness")

        if row["SalesNav_ProfileViews"] > df["SalesNav_ProfileViews"].median():
            reasons.append("High Engagement Activity")

        if row["Quantity_Tons"] > df["Quantity_Tons"].median():
            reasons.append("Strong Production Capacity")

        if row["Tariff_Impact"] < df["Tariff_Impact"].median():
            reasons.append("Low Tariff Risk")

        return ", ".join(reasons[:3]) if reasons else "Balanced Performance"

    df["ai_reason"] = df.apply(generate_reason, axis=1)

    # -------------------------
    # Final Output Columns
    # -------------------------
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

    feature_names = [
        "Intent_Score",
        "Shipment_Value_USD",
        "Quantity_Tons",
        "Prompt_Response_Score",
        "SalesNav_ProfileViews",
        "Tariff_Impact",
        "War_Risk",
        "Currency_Shift"
    ]

    importances = model.feature_importances_

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    return importance_df
