import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_excel("trade_data.xlsx")

# -------------------------
# Features & Target
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
# Train-Test Split
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
# Evaluate Model
# -------------------------

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------
# Save Model
# -------------------------

joblib.dump(model, "lead_model.pkl")

print("\nModel saved as lead_model.pkl")
