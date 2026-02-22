import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# -------------------------
# Load Clean Dataset
# -------------------------
df = pd.read_csv("trade_data_processed_cleaned.csv")

# -------------------------
# Ensure Converted Column Exists
# -------------------------
if "Converted" not in df.columns:
    print("Converted column not found. Generating automatically...")

    df["Converted"] = (
        (df["Intent_Score"] > df["Intent_Score"].quantile(0.65)) &
        (df["Shipment_Value_USD"] > df["Shipment_Value_USD"].median()) &
        (df["Prompt_Response_Score"] > df["Prompt_Response_Score"].median())
    ).astype(int)

    # Add 10% noise
    noise = np.random.rand(len(df)) < 0.1
    df.loc[noise, "Converted"] = 1 - df.loc[noise, "Converted"]

    df.to_csv("trade_data_processed_cleaned.csv", index=False)
    print("Converted column created.")

print("\nConverted distribution:")
print(df["Converted"].value_counts())

# -------------------------
# Features
# -------------------------
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
y = df["Converted"]

# -------------------------
# Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------
# Train Model
# -------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# Evaluate
# -------------------------
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------
# Save Model
# -------------------------
joblib.dump(model, "lead_model.pkl")
print("\nModel saved as lead_model.pkl")