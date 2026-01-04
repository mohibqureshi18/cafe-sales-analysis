import streamlit as st
import pandas as pd
import plotly.express as px
from utils import clean_cafe_data, run_ml_prediction

st.set_page_config(page_title="Cafe Pro Analytics", layout="wide")

st.title("☕ Cafe Sales: Professional Command Center")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("Upload Sales Data", type="csv")

if uploaded_file:
    # Processing
    raw_df = pd.read_csv(uploaded_file)
    df = clean_cafe_data(raw_df)
    
    # Sidebar Filters
    st.sidebar.header("Filters")
    loc_filter = st.sidebar.multiselect("Locations", options=df['Location'].unique(), default=df['Location'].unique())
    df_final = df[df['Location'].isin(loc_filter)]

    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${df_final['Total Spent'].sum():,.2f}")
    c2.metric("Avg Order", f"${df_final['Total Spent'].mean():,.2f}")
    c3.metric("Items Sold", int(df_final['Quantity'].sum()))
    c4.metric("Valid Rows", len(df_final))

    # Single Space Hub
    tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "🔮 ML Predictor", "🧹 Data Audit"])

    with tab1:
        st.subheader("Interactive Sales Insights")
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.line(df_final.groupby('Transaction Date')['Total Spent'].sum().reset_index(), 
                           x='Transaction Date', y='Total Spent', title="Revenue Timeline")
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            fig2 = px.pie(df_final, names='Item', values='Total Spent', title="Revenue by Item")
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Random Forest Revenue Predictor")
        model = run_ml_prediction(df)
        if model:
            q = st.slider("Quantity", 1, 10, 5)
            p = st.number_input("Price per Unit", value=4.5)
            prediction = model.predict([[q, p]])
            st.success(f"Estimated Transaction Value: **${prediction[0]:.2f}**")

    with tab3:
        st.subheader("Data Cleaning Results")
        st.dataframe(df_final, use_container_width=True)
        st.download_button("Export Clean CSV", df_final.to_csv(index=False), "cleaned_sales.csv")
else:
    st.info("Please upload the CSV to start the analysis.")