import pandas as pd
import joblib

# Load trained model
model = joblib.load("lead_model.pkl")

# Load dataset
df = pd.read_csv("trade_data_processed_cleaned.csv")

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

# Get prediction probabilities
df["Conversion_Probability"] = model.predict_proba(df[features])[:, 1]

# Sort by highest probability
recommended = df.sort_values("Conversion_Probability", ascending=False)

print(recommended[["Conversion_Probability"]].head(10))
