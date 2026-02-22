import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("trade_data_processed_cleaned.csv")

features = [
    "Intent_Score",
    "Prompt_Response_Score",
    "Shipment_Value_USD",
    "War_Risk",
    "Tariff_Impact"
]

# Normalize features to 0–1
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])
scaled_df = pd.DataFrame(scaled, columns=features)

# Build softer linear score
linear_score = (
    1.2 * scaled_df["Intent_Score"] +
    1.0 * scaled_df["Prompt_Response_Score"] +
    0.8 * scaled_df["Shipment_Value_USD"] -
    1.0 * scaled_df["War_Risk"] -
    0.8 * scaled_df["Tariff_Impact"]
)

# Add stronger randomness
linear_score += np.random.normal(0, 0.8, len(df))

# Convert to probability using sigmoid
probability = 1 / (1 + np.exp(-linear_score))

df["Converted"] = np.random.binomial(1, probability)

df.to_csv("trade_data_processed_cleaned.csv", index=False)

print("Realistic Converted regenerated.")
