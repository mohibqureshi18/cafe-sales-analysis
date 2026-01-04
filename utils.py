import pandas as pd
import numpy as np

def clean_cafe_data(df):
    """Professional cleaning logic with auto-calculation and type casting."""
    df_cleaned = df.copy()
    
    # Standardize invalid markers
    invalid_values = ['ERROR', 'UNKNOWN', '', 'nan']
    df_cleaned.replace(invalid_values, np.nan, inplace=True)
    
    # Type Conversion
    numerical_cols = ['Quantity', 'Price Per Unit', 'Total Spent']
    for col in numerical_cols:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
    
    df_cleaned['Transaction Date'] = pd.to_datetime(df_cleaned['Transaction Date'], errors='coerce')
    
    # Logic Correction: If Total Spent is missing but Price/Qty exist 
    valid_calc = df_cleaned['Quantity'].notna() & df_cleaned['Price Per Unit'].notna()
    df_cleaned.loc[df_cleaned['Total Spent'].isna() & valid_calc, 'Total Spent'] = \
        df_cleaned['Quantity'] * df_cleaned['Price Per Unit']
        
    # Impute missing categories with Mode
    for col in ['Item', 'Payment Method', 'Location']:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
        
    return df_cleaned

def get_performance_metrics(df):
    """New Utility: Returns dictionary of key performance indicators."""
    metrics = {
        "total_revenue": df['Total Spent'].sum(),
        "avg_ticket": df['Total Spent'].mean(),
        "total_items": df['Quantity'].sum(),
        "top_item": df.groupby('Item')['Quantity'].sum().idxmax()
    }
    return metrics