# utils.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def clean_cafe_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans cafe sales data:
    - Normalizes column names
    - Fills missing Total Spent where possible
    - Handles missing columns safely
    """
    # Normalize columns: strip, lowercase, replace spaces with underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Ensure necessary columns exist
    for col in ['quantity', 'price_per_unit', 'total_spent']:
        if col not in df.columns:
            if col == 'total_spent':
                df['total_spent'] = pd.NA
            else:
                df[col] = 0  # default 0 if missing

    # Fill missing total_spent where quantity and price_per_unit exist
    mask = df['total_spent'].isna() & df['quantity'].notna() & df['price_per_unit'].notna()
    df.loc[mask, 'total_spent'] = df.loc[mask, 'quantity'] * df.loc[mask, 'price_per_unit']

    # Optional: fill missing values with 0 for numeric columns
    numeric_cols = ['quantity', 'price_per_unit', 'total_spent']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


def run_ml_prediction(df: pd.DataFrame):
    """
    Trains a simple RandomForest model to predict total transaction value
    based on quantity and price_per_unit
    """
    # Check if required columns exist
    if not all(col in df.columns for col in ['quantity', 'price_per_unit', 'total_spent']):
        return None

    X = df[['quantity', 'price_per_unit']]
    y = df['total_spent']

    # Train model only if we have data
    if len(X) < 5:
        return None

    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    return model
