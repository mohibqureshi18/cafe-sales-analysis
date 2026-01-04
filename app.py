import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from utils import clean_cafe_data, run_ml_prediction

# -------------------- Streamlit Page Setup --------------------
st.set_page_config(page_title="Cafe Pro Analytics", layout="wide")
st.title("☕ Cafe Sales: Professional Command Center")
st.markdown("---")

# -------------------- File Uploader --------------------
uploaded_file = st.sidebar.file_uploader("Upload Sales Data", type="csv")

if uploaded_file:
    # -------------------- Load and Clean Data --------------------
    raw_df = pd.read_csv(uploaded_file)
    df = clean_cafe_data(raw_df)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # -------------------- Sidebar Filters --------------------
    st.sidebar.header("Filters")
    if 'location' in df.columns:
        loc_filter = st.sidebar.multiselect(
            "Locations", options=df['location'].unique(), default=df['location'].unique()
        )
        df_final = df[df['location'].isin(loc_filter)]
    else:
        df_final = df.copy()

    # -------------------- Metrics --------------------
    c1, c2, c3, c4 = st.columns(4)
    total_revenue = df_final['total_spent'].sum() if 'total_spent' in df_final.columns else 0
    avg_order = df_final['total_spent'].mean() if 'total_spent' in df_final.columns else 0
    total_items = int(df_final['quantity'].sum()) if 'quantity' in df_final.columns else 0
    valid_rows = len(df_final)

    c1.metric("Total Revenue", f"${total_revenue:,.2f}")
    c2.metric("Avg Order", f"${avg_order:,.2f}")
    c3.metric("Items Sold", total_items)
    c4.metric("Valid Rows", valid_rows)

    # -------------------- Tabs --------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Performance Analysis",
        "📈 EDA & Outliers",
        "🔮 ML Predictor",
        "🧹 Data Audit"
    ])

    # -------------------- Tab 1: Performance Analysis --------------------
    with tab1:
        st.subheader("Revenue & Sales Insights")
        col_a, col_b = st.columns(2)

        with col_a:
            if 'transaction_date' in df_final.columns and 'total_spent' in df_final.columns:
                fig1 = px.line(
                    df_final.groupby('transaction_date')['total_spent'].sum().reset_index(),
                    x='transaction_date',
                    y='total_spent',
                    title="Revenue Timeline"
                )
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Transaction Date or Total Spent column missing.")

        with col_b:
            if 'item' in df_final.columns and 'total_spent' in df_final.columns:
                fig2 = px.pie(
                    df_final, names='item', values='total_spent', title="Revenue by Item"
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Item or Total Spent column missing.")

    # -------------------- Tab 2: EDA & Outliers --------------------
    with tab2:
        st.subheader("Exploratory Data Analysis & Outliers")

        # Numeric columns only
        numeric_cols = df_final.select_dtypes(include=['int64', 'float64']).columns.tolist()
        st.markdown("### Numeric Feature Distributions")
        for col in numeric_cols:
            fig = px.histogram(df_final, x=col, nbins=30, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)

        # Correlation Heatmap
        if len(numeric_cols) >= 2:
            st.markdown("### Correlation Heatmap")
            corr = df_final[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(8,6))
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
            st.pyplot(fig)

        # Boxplots for Outlier Detection
        st.markdown("### Boxplots for Outliers")
        for col in numeric_cols:
            fig = px.box(df_final, y=col, points="all", title=f"Outliers in {col}")
            st.plotly_chart(fig, use_container_width=True)

        # Scatter Plots (numeric vs target)
        if 'total_spent' in numeric_cols:
            st.markdown("### Scatter Plots vs Total Spent")
            for col in numeric_cols:
                if col != 'total_spent':
                    fig = px.scatter(df_final, x=col, y='total_spent', trendline="ols",
                                     title=f"{col} vs Total Spent")
                    st.plotly_chart(fig, use_container_width=True)

    # -------------------- Tab 3: ML Predictor --------------------
    with tab3:
        st.subheader("Random Forest Revenue Predictor")
        model = run_ml_prediction(df)
        if model:
            q = st.slider("Quantity", 1, 10, 5)
            p = st.number_input("Price per Unit", value=4.5)
            prediction = model.predict([[q, p]])
            st.success(f"Estimated Transaction Value: **${prediction[0]:.2f}**")
        else:
            st.info("ML model could not be loaded or trained.")

    # -------------------- Tab 4: Data Audit --------------------
    with tab4:
        st.subheader("Data Cleaning Results")
        st.dataframe(df_final, use_container_width=True)
        st.download_button(
            "Export Clean CSV",
            df_final.to_csv(index=False),
            file_name="cleaned_sales.csv"
        )

else:
    st.info("Please upload the CSV to start the analysis.")
