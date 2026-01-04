import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def clean_cafe_data(df):
    """Professional cleaning: Recovers columns and repairs 'ERROR' values."""
    df_cleaned = df.copy()

    # Step 1: Force find headers if CSV is messy
    if 'Location' not in df_cleaned.columns:
        for i, row in df_cleaned.iterrows():
            if 'Location' in [str(x) for x in row.values]:
                df_cleaned.columns = row.values
                df_cleaned = df_cleaned.iloc[i+1:].reset_index(drop=True)
                break
    
    # Step 2: Replace all variations of bad data
    bad_list = ['ERROR', 'UNKNOWN', 'nan', '<<<<<<< HEAD', '=======', '>>>>>>>']
    df_cleaned.replace(bad_list, np.nan, inplace=True)
    
    # Step 3: Fix Numeric Columns & Recalculate 'Total Spent' errors
    cols = ['Quantity', 'Price Per Unit', 'Total Spent']
    for c in cols:
        if c in df_cleaned.columns:
            df_cleaned[c] = pd.to_numeric(df_cleaned[c], errors='coerce')
            
    # Logic Repair: If Total Spent is missing, calculate it
    mask = df_cleaned['Total Spent'].isna() & df_cleaned['Quantity'].notna() & df_cleaned['Price Per Unit'].notna()
    df_cleaned.loc[mask, 'Total Spent'] = df_cleaned['Quantity'] * df_cleaned['Price Per Unit']

    # Step 4: Fix Dates
    if 'Transaction Date' in df_cleaned.columns:
        df_cleaned['Transaction Date'] = pd.to_datetime(df_cleaned['Transaction Date'], errors='coerce')
    
    # Step 5: Categorical fill
    for c in ['Item', 'Location', 'Payment Method']:
        if c in df_cleaned.columns:
            df_cleaned[c] = df_cleaned[c].fillna("Uncategorized")
            
    return df_cleaned

def run_ml_prediction(df):
    """Utility based on your PythonProject.ipynb logic."""
    try:
        train_data = df.dropna(subset=['Total Spent', 'Quantity', 'Price Per Unit'])
        X = train_data[['Quantity', 'Price Per Unit']]
        y = train_data['Total Spent']
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model
    except:
        return None