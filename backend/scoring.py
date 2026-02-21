# Improve cleaning on the already-loaded dataframe `df` if present; otherwise try loading from the processed CSV.
# Adds robust ID cleanup, deduping, outlier handling, better rolling features by region, and saves a cleaner version.

import os
import numpy as np
import pandas as pd
from tqdm import tqdm

if 'df' not in globals():
   DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

processed_path = os.path.join(DATA_DIR, 'trade_data_processed.csv')
excel_path = os.path.join(DATA_DIR, 'trade_data.xlsx')

if os.path.exists(processed_path):
    df = pd.read_csv(processed_path)
elif os.path.exists(excel_path):
    df = pd.read_excel(excel_path, sheet_name=0)
else:
    raise FileNotFoundError(
        'No df in memory and cannot find trade_data_processed.csv or trade_data.xlsx'
    )


print(df.head())
print(df.shape)

# Standardize key columns
for col_name in ['News_ID', 'Region', 'Event_Type']:
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.strip()

# Date parse
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=False)

# Clean News_ID: keep alphanumerics, remove trailing .0, pad not here yet
if 'News_ID' in df.columns:
    news_id_vals = df['News_ID'].astype(str)
    news_id_vals = news_id_vals.str.replace(r'\.0$', '', regex=True)
    news_id_vals = news_id_vals.str.replace(r'[^0-9A-Za-z_-]+', '', regex=True)
    df['News_ID'] = news_id_vals.replace({'': np.nan})

# Normalize text fields with consistent missing token
missing_token = 'unknown'
for col_name in ['Region', 'Event_Type']:
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.strip().str.lower()
        df.loc[df[col_name].isin(['nan', 'none', 'null', '']), col_name] = missing_token

# Drop bad required rows
required_cols = [c for c in ['News_ID', 'Date', 'Region', 'Event_Type'] if c in df.columns]
df = df.dropna(subset=required_cols).copy()
if 'Date' in df.columns:
    df = df.dropna(subset=['Date']).copy()

# Deduplicate: keep latest by Date for same News_ID (and region/type if present)
dedupe_keys = [c for c in ['News_ID', 'Region', 'Event_Type'] if c in df.columns]
if len(dedupe_keys) > 0 and 'Date' in df.columns:
    df = df.sort_values('Date').copy()
    df = df.drop_duplicates(subset=dedupe_keys, keep='last').copy()

# Numeric coercion and winsorize outliers
numeric_cols = []
for col_name in ['Impact_Level', 'Tariff_Change', 'StockMarket_Shock', 'Currency_Shift', 'Shipment_Value_USD', 'Quantity_Tons', 'Impact_Score', 'import_growth_pct', 'import_volume', 'frequency', 'country_demand', 'price_avg']:
    if col_name in df.columns:
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        numeric_cols.append(col_name)

# Impute numeric missing with median (or 0)
for col_name in numeric_cols:
    med_val = df[col_name].median()
    if pd.isna(med_val):
        med_val = 0.0
    df[col_name] = df[col_name].fillna(med_val)

# Winsorize heavy-tailed measures
winsor_cols = [c for c in ['Shipment_Value_USD', 'Quantity_Tons', 'Tariff_Change', 'StockMarket_Shock', 'Currency_Shift', 'Impact_Level'] if c in df.columns]
for col_name in winsor_cols:
    low_q = df[col_name].quantile(0.01)
    high_q = df[col_name].quantile(0.99)
    if pd.notna(low_q) and pd.notna(high_q) and high_q > low_q:
        df[col_name] = df[col_name].clip(lower=low_q, upper=high_q)

# Ensure flags are 0/1
flag_candidates = [c for c in ['War_Flag', 'Natural_Calamity_Flag'] if c in df.columns]
for col_name in flag_candidates:
    df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0.0)
    df[col_name] = (df[col_name] > 0).astype(int)

# Recompute Impact_Score consistently if components exist
score_parts = [c for c in ['Impact_Level', 'Tariff_Change', 'StockMarket_Shock', 'Currency_Shift', 'War_Flag', 'Natural_Calamity_Flag'] if c in df.columns]
if len(score_parts) > 0:
    df['Impact_Score'] = 0.0
    for c in score_parts:
        df['Impact_Score'] = df['Impact_Score'] + pd.to_numeric(df[c], errors='coerce').fillna(0.0)

# Better features: do rolling calculations within Region
if 'Region' in df.columns and 'Date' in df.columns:
    df = df.sort_values(['Region', 'Date']).copy()

    if 'Shipment_Value_USD' in df.columns:
        def pct_change_region(g):
            g = g.sort_values('Date').copy()
            g['import_growth_pct'] = g['Shipment_Value_USD'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0) * 100.0
            return g
        df = df.groupby('Region', group_keys=False).apply(pct_change_region)

    # rolling 365D event count by region
    if 'News_ID' in df.columns:
        def roll_count_region(g):
            g2 = g.set_index('Date').sort_index().copy()
            g2['frequency'] = g2['News_ID'].rolling('365D').count().values
            return g2.reset_index()
        df = df.groupby('Region', group_keys=False).apply(roll_count_region)

    # price_avg: 7D rolling mean of Shipment_Value_USD by region using a time window if possible
    if 'Shipment_Value_USD' in df.columns:
        def roll_price_region(g):
            g2 = g.set_index('Date').sort_index().copy()
            g2['price_avg'] = g2['Shipment_Value_USD'].rolling('7D', min_periods=1).mean().values
            return g2.reset_index()
        df = df.groupby('Region', group_keys=False).apply(roll_price_region)

# Recompute country_demand
if 'Region' in df.columns and 'import_volume' in df.columns:
    df['country_demand'] = df.groupby('Region')['import_volume'].transform('sum')

# Light category compression for text fields
for col_name in ['Region', 'Event_Type']:
    if col_name in df.columns:
        df[col_name] = df[col_name].astype('category')

# Save a cleaner processed CSV
cleaned_csv = 'trade_data_processed_cleaned.csv'
df.to_csv(cleaned_csv, index=False)
print(cleaned_csv)
print(df.head())

# Quick quality summary
summary_dict = {
    'rows': [df.shape[0]],
    'cols': [df.shape[1]],
    'missing_any_pct': [float(df.isna().mean().mean() * 100.0)]
}
print(pd.DataFrame(summary_dict))