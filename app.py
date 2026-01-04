import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Cafe Sales Dashboard", layout="wide")

# ==========================================
# 1. DATA RESCUE (Fix Git Conflict Markers)
# ==========================================
def load_and_clean_csv(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Remove Git conflict markers
        clean_lines = [
            line for line in lines 
            if not (line.startswith('<<<<<<<') or 
                    line.startswith('=======') or 
                    line.startswith('>>>>>>>'))
        ]
        
        # Save to a temporary clean file
        fixed_path = "temp_clean_sales.csv"
        with open(fixed_path, 'w') as f:
            f.writelines(clean_lines)
            
        df = pd.read_csv(fixed_path)
        df.columns = df.columns.str.strip() # Clean headers
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Load the data
df_raw = load_and_clean_csv('dirty_cafe_sales.csv')

if df_raw is not None:
    # Basic Cleaning for visualization
    df = df_raw.copy()
    df.replace(['ERROR', 'UNKNOWN', ''], np.nan, inplace=True)
    df['Total Spent'] = pd.to_numeric(df['Total Spent'], errors='coerce')
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')
    df = df.dropna(subset=['Total Spent']) # Remove rows where we can't show sales

    st.title("☕ Cafe Sales Analytics")

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    location = st.sidebar.multiselect("Select Location", options=df['Location'].unique(), default=df['Location'].unique())
    
    filtered_df = df[df['Location'].isin(location)]

    # --- KEY METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${filtered_df['Total Spent'].sum():,.2f}")
    col2.metric("Avg Transaction", f"${filtered_df['Total Spent'].mean():,.2f}")
    col3.metric("Total Items Sold", int(filtered_df['Quantity'].sum()) if 'Quantity' in filtered_df.columns else "N/A")

    # --- GRAPHS ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Sales by Item")
        fig_items = px.bar(filtered_df.groupby('Item')['Total Spent'].sum().reset_index(), 
                           x='Item', y='Total Spent', color='Item',
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_items, use_container_width=True)

    with row1_col2:
        st.subheader("Payment Method Distribution")
        fig_pay = px.pie(filtered_df, names='Payment Method', values='Total Spent', hole=0.4)
        st.plotly_chart(fig_pay, use_container_width=True)

    st.subheader("Sales Over Time")
    sales_time = filtered_df.groupby('Transaction Date')['Total Spent'].sum().reset_index()
    fig_line = px.line(sales_time, x='Transaction Date', y='Total Spent')
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.warning("Please upload or provide a valid 'dirty_cafe_sales.csv' file.")