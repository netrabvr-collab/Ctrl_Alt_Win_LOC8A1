import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "trade_data.xlsx"
OUTPUT_PATH = BASE_DIR / "outputs" / "trade_data_processed.csv"


def process_trade_data(save: bool = True) -> pd.DataFrame:
    """
    Clean and engineer features from raw trade data.
    """

    df = pd.read_excel(DATA_PATH, engine="openpyxl")

    # --------------------------
    # Column Mapping
    # --------------------------
    col_map = {
        'Record_ID': 'News_ID',
        'Date': 'Date',
        'State': 'Region',
        'Industry': 'Event_Type',
        'Tariff_Impact': 'Tariff_Change',
        'StockMarket_Impact': 'StockMarket_Shock',
        'Currency_Shift': 'Currency_Shift',
        'War_Risk': 'War_Flag',
        'Natural_Calamity_Risk': 'Natural_Calamity_Flag',
        'Impact_Level': 'Impact_Level'
    }

    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # --------------------------
    # Required Columns
    # --------------------------
    required = ['News_ID', 'Date', 'Region', 'Event_Type']
    for col in required:
        if col not in df.columns:
            df[col] = "Unknown"

    df = df.dropna(subset=required)

    # --------------------------
    # Text Normalization
    # --------------------------
    for col in ['Region', 'Event_Type']:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .fillna('unknown')
            .astype('category')
        )

    # --------------------------
    # Date Handling
    # --------------------------
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # --------------------------
    # Numeric Fields
    # --------------------------
    numeric_fields = [
        'Impact_Level',
        'Tariff_Change',
        'StockMarket_Shock',
        'Currency_Shift'
    ]

    for col in numeric_fields:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0.0)

    # Binary flags
    for col in ['War_Flag', 'Natural_Calamity_Flag']:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0).astype(int)

    # --------------------------
    # Impact Score
    # --------------------------
    df['Impact_Score'] = (
        df['Impact_Level']
        + df['Tariff_Change']
        + df['StockMarket_Shock']
        + df['Currency_Shift']
        + df['War_Flag']
        + df['Natural_Calamity_Flag']
    )

    # --------------------------
    # Shipment Features
    # --------------------------
    df = df.sort_values("Date")

    if 'Shipment_Value_USD' in df.columns:
        df['Shipment_Value_USD'] = pd.to_numeric(df['Shipment_Value_USD'], errors='coerce').fillna(0)
        df['import_growth_pct'] = df['Shipment_Value_USD'].pct_change().fillna(0) * 100
        df['price_avg'] = df['Shipment_Value_USD'].rolling(7, min_periods=1).mean()
    else:
        df['import_growth_pct'] = 0.0
        df['price_avg'] = 0.0

    if 'Quantity_Tons' in df.columns:
        df['import_volume'] = pd.to_numeric(df['Quantity_Tons'], errors='coerce').fillna(0.0)
    else:
        df['import_volume'] = 0.0

    # --------------------------
    # Rolling Frequency (Optimized)
    # --------------------------
    df = df.sort_values(['Region', 'Date'])
    df['frequency'] = (
        df.groupby('Region')
        .rolling('365D', on='Date')['News_ID']
        .count()
        .reset_index(level=0, drop=True)
    )

    # --------------------------
    # Country Demand
    # --------------------------
    df['country_demand'] = df.groupby('Region')['import_volume'].transform('sum')

    # --------------------------
    # Save if needed
    # --------------------------
    if save:
        OUTPUT_PATH.parent.mkdir(exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)

    return df
