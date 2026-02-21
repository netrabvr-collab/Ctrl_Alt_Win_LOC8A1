import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def generate_lead_scores():

    # Load dataset
    df = pd.read_excel("data/trade_data.xlsx")
    df = df.fillna(0)

    # Feature groups
    main_features = [
        "Intent_Score",
        "Shipment_Value_USD",
        "Quantity_Tons",
        "Prompt_Response_Score",
        "SalesNav_ProfileViews"
    ]

    risk_features = [
        "Tariff_Impact",
        "War_Risk",
        "Currency_Shift"
    ]

    scaler = MinMaxScaler()

    # Normalize main features
    df[main_features] = scaler.fit_transform(df[main_features])

    # Normalize risk features
    df[risk_features] = scaler.fit_transform(df[risk_features])

    # Lead scoring formula
    df["lead_score"] = (
        0.30 * df["Intent_Score"] +
        0.25 * df["Shipment_Value_USD"] +
        0.15 * df["Quantity_Tons"] +
        0.15 * df["Prompt_Response_Score"] +
        0.15 * df["SalesNav_ProfileViews"]
    ) - (
        0.20 * df["Tariff_Impact"] +
        0.10 * df["War_Risk"] +
        0.10 * df["Currency_Shift"]
    )

    # Scale final score to 0–100
    df["lead_score"] = MinMaxScaler().fit_transform(df[["lead_score"]]) * 100

    # Categorize leads
    def categorize(score):
        if score >= 75:
            return "High Potential"
        elif score >= 40:
            return "Medium Potential"
        else:
            return "Low Potential"

    df["lead_category"] = df["lead_score"].apply(categorize)

    # Final output
    final_df = df[[
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
        "lead_score",
        "lead_category"
    ]]

    return final_df.sort_values(by="lead_score", ascending=False)