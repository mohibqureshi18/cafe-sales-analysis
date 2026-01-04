import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils import clean_cafe_data, get_performance_metrics

st.set_page_config(page_title="Cafe Pro Analytics", layout="wide", page_icon="☕")

# Custom CSS for professional look
st.markdown("""<style> .main { background-color: #f5f5f5; } </style>""", unsafe_allow_html=True)

st.title("☕ Cafe Sales Intelligence Suite")
st.sidebar.header("Data Management")

uploaded_file = st.sidebar.file_uploader("Upload Sales CSV", type="csv")

if uploaded_file:
    # Load and Clean
    raw_df = pd.read_csv(uploaded_file)
    df = clean_cafe_data(raw_df)
    metrics = get_performance_metrics(df)

    # Top Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Revenue", f"${metrics['total_revenue']:,.2f}")
    m2.metric("Avg Order", f"${metrics['avg_ticket']:,.2f}")
    m3.metric("Items Sold", int(metrics['total_items']))
    m4.metric("Best Seller", metrics['top_item'])

    # Single Space Navigation Hub
    tab1, tab2, tab3 = st.tabs(["📊 Sales Overview", "📍 Location Analysis", "🧹 Data Health"])

    with tab1:
        st.subheader("Sales Performance Analysis")
        fig, ax = plt.subplots(figsize=(10, 4))
        # Logic from your notebook: Month-based analysis 
        df['Month'] = df['Transaction Date'].dt.strftime('%b')
        sns.lineplot(data=df.groupby('Month')['Total Spent'].sum().reset_index(), 
                     x='Month', y='Total Spent', marker='o', ax=ax)
        st.pyplot(fig)

    with tab2:
        st.subheader("Regional Performance")
        col_left, col_right = st.columns(2)
        with col_left:
            # Bar chart by location 
            st.bar_chart(df.groupby('Location')['Total Spent'].sum())
        with col_right:
            # Payment method breakdown
            st.write("Payment Distribution")
            fig2, ax2 = plt.subplots()
            df['Payment Method'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2)
            st.pyplot(fig2)

    with tab3:
        st.subheader("Cleaning Audit Trail")
        st.write("Rows with corrected values:")
        # Show logic derived from your notebook cleaning steps 
        st.dataframe(df.head(10))
        st.download_button("Export Cleaned Data", df.to_csv(index=False), "cleaned_sales.csv")

else:
    st.info("Please upload a CSV file in the sidebar to begin analysis.")