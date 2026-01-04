import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(page_title="Cafe Sales Dashboard", layout="wide")

# ==========================================
# 1. DATA RESCUE (Handles Git Merge Conflicts)
# ==========================================
def load_and_fix_data(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Filter out Git conflict markers
        clean_lines = [
            line for line in lines 
            if not (line.startswith('<<<<<<<') or 
                    line.startswith('=======') or 
                    line.startswith('>>>>>>>'))
        ]
        
        fixed_path = "temp_clean_data.csv"
        with open(fixed_path, 'w') as f:
            f.writelines(clean_lines)
            
        df = pd.read_csv(fixed_path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None

# ==========================================
# 2. DATA CLEANING (Fixes the TypeError)
# ==========================================
raw_df = load_and_fix_data('dirty_cafe_sales.csv')

if raw_df is not None:
    df = raw_df.copy()
    
    # 1. Replace text-based errors with NaN
    df.replace(['ERROR', 'UNKNOWN', ''], np.nan, inplace=True)
    
    # 2. FORCE conversion to numeric (CRITICAL FIX)
    # errors='coerce' turns strings into NaN so the .sum() doesn't crash
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['Total Spent'] = pd.to_numeric(df['Total Spent'], errors='coerce')
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')

    # 3. Drop rows where we can't visualize anything
    df = df.dropna(subset=['Total Spent', 'Item'])

    # --- Metrics Logic ---
    st.title("☕ Cafe Sales Analytics")
    
    # Sidebar filter
    locations = sorted(df['Location'].dropna().unique())
    selected_loc = st.sidebar.multiselect("Location", locations, default=locations)
    filtered_df = df[df['Location'].isin(selected_loc)]

    # --- Metrics Display ---
    col1, col2, col3 = st.columns(3)
    
    # Use skipna=True (default) to ensure we sum only the valid numbers
    revenue = filtered_df['Total Spent'].sum()
    avg_txn = filtered_df['Total Spent'].mean()
    
    # The fix for line 59: Sum first, check for NaN, then format
    total_qty = filtered_df['Quantity'].sum()
    qty_display = f"{int(total_qty):,}" if not np.isnan(total_qty) else "0"

    col1.metric("Total Revenue", f"${revenue:,.2f}")
    col2.metric("Avg Transaction", f"${avg_txn:,.2f}")
    col3.metric("Total Items Sold", qty_display)

    # --- Graphs ---
    c1, c2 = st.columns(2)
    with c1:
        fig_bar = px.bar(filtered_df.groupby('Item')['Total Spent'].sum().reset_index(), 
                         x='Item', y='Total Spent', title="Revenue by Item")
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        fig_pie = px.pie(filtered_df, names='Payment Method', values='Total Spent', title="Payment Methods")
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("Please ensure 'dirty_cafe_sales.csv' is present.")