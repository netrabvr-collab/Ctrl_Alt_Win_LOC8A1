import pandas as pd
import os
import numpy as np
from tqdm import tqdm

# --------------------------
# Load file
# --------------------------
file_path = "data/trade_data.xlsx"
df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
print("Original head:")
print(df.head())

# --------------------------
# Map columns to target schema
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

# Rename columns if they exist
for old, new in col_map.items():
    if old in df.columns:
        df = df.rename(columns={old: new})

# Ensure required columns exist
required = ['News_ID','Date','Region','Event_Type']
for req in required:
    if req not in df.columns:
        df[req] = "Unknown"

# Drop rows missing critical info
df = df.dropna(subset=['News_ID','Date','Region','Event_Type'])

# --------------------------
# Normalize text fields
# --------------------------
for col in ['Region','Event_Type']:
    df[col] = df[col].astype(str).str.strip().str.lower().fillna('unknown').astype('category')

# --------------------------
# Date to datetime
# --------------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

# --------------------------
# Numeric optional fields
# --------------------------
numeric_fields = ['Impact_Level','Tariff_Change','StockMarket_Shock','Currency_Shift']
for col in numeric_fields:
    if col not in df.columns:
        df[col] = 0.0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)

# --------------------------
# Binary flags
# --------------------------
for col in ['War_Flag','Natural_Calamity_Flag']:
    if col not in df.columns:
        df[col] = 0
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# --------------------------
# Compute Impact Score
# --------------------------
df['Impact_Score'] = df['Impact_Level'] + df['Tariff_Change'] + df['StockMarket_Shock'] + df['Currency_Shift'] + df['War_Flag'] + df['Natural_Calamity_Flag']

# --------------------------
# Additional features
# --------------------------
if 'Shipment_Value_USD' in df.columns:
    df = df.sort_values('Date')
    df['import_growth_pct'] = df['Shipment_Value_USD'].pct_change().fillna(0)*100
    df['price_avg'] = df['Shipment_Value_USD'].rolling(7, min_periods=1).mean()
else:
    df['import_growth_pct'] = 0.0
    df['price_avg'] = 0.0

if 'Quantity_Tons' in df.columns:
    df['import_volume'] = pd.to_numeric(df['Quantity_Tons'], errors='coerce').fillna(0.0)
else:
    df['import_volume'] = 0.0

# Frequency of events per region in last 365 days
def freq_group(g):
    g = g.set_index('Date')
    g = g.sort_index()
    g['frequency'] = g['News_ID'].rolling('365D').count().values
    return g.reset_index()

df = df.groupby('Region', group_keys=False).apply(freq_group)

# Country demand
df['country_demand'] = df.groupby('Region')['import_volume'].transform('sum')

# --------------------------
# Show summaries
# --------------------------
print("Processed head:")
print(df.head())

print(df[['Impact_Score','import_growth_pct','import_volume','frequency','country_demand','price_avg']].describe())

# --------------------------
# Save output
# --------------------------
out_file = 'trade_data_processed.csv'
df.to_csv(out_file, index=False)
print(f"Saved processed data to {out_file}")