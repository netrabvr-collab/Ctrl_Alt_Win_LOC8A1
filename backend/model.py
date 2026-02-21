import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "trade_data.xlsx"


def generate_lead_scores() -> pd.DataFrame:
    """
    Generate lead scores from trade dataset.
    Returns sorted DataFrame.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df = df.fillna(0)

    # -------------------------
    # Required Columns
    # -------------------------
    required_columns = [
        "Intent_Score",
        "Shipment_Value_USD",
        "Quantity_Tons",
        "Prompt_Response_Score",
        "SalesNav_ProfileViews",
        "Tariff_Impact",
        "War_Risk",
        "Currency_Shift",
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # -------------------------
    # Feature Scaling
    # -------------------------
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

    scaler_main = MinMaxScaler()
    scaler_risk = MinMaxScaler()

    df[main_features] = scaler_main.fit_transform(df[main_features])
    df[risk_features] = scaler_risk.fit_transform(df[risk_features])

    # -------------------------
    # Lead Score Formula
    # -------------------------
    positive_score = (
        0.30 * df["Intent_Score"] +
        0.25 * df["Shipment_Value_USD"] +
        0.15 * df["Quantity_Tons"] +
        0.15 * df["Prompt_Response_Score"] +
        0.15 * df["SalesNav_ProfileViews"]
    )

    risk_penalty = (
        0.20 * df["Tariff_Impact"] +
        0.10 * df["War_Risk"] +
        0.10 * df["Currency_Shift"]
    )

    df["lead_score_raw"] = positive_score - risk_penalty

    # Scale final score 0–100
    df["lead_score"] = (
        MinMaxScaler()
        .fit_transform(df[["lead_score_raw"]])
        * 100
    )

    # -------------------------
    # Categorization
    # -------------------------
    df["lead_category"] = pd.cut(
        df["lead_score"],
        bins=[-1, 40, 75, 100],
        labels=["Low Potential", "Medium Potential", "High Potential"]
    )

    # -------------------------
    # Final Output
    # -------------------------
    final_df = df[[
        "Exporter_ID",
        "Industry",
        "State",
        "Revenue_Size_USD",
        "lead_score",
        "lead_category"
    ]].sort_values(by="lead_score", ascending=False)

    return final_df
