import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import sys
sys.path.append("..")
from utils import load_data


def app():
    st.title("Analytics")
    df = load_data()

    # -----------------------------
    # 1. Data Preview
    # -----------------------------
    st.subheader("Runway Sensor Overview")
    st.dataframe(df.head(20))

    # -----------------------------
    # 2. KPI Summary Cards
    # -----------------------------
    st.subheader("Key Metrics Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Detected Anomalies", int(df["anomaly"].sum()) if "anomaly" in df else 0)
    col3.metric("Min Rubber Thickness (mm)", round(df["rubber_mm"].min(), 2) if "rubber_mm" in df else "N/A")

    # -----------------------------
    # 3. Correlation Heatmap
    # -----------------------------
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    if not numeric_df.empty:
        st.subheader("Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No numeric columns available for correlation analysis")

    # -----------------------------
    # 4. Rubber Thickness Distribution
    # -----------------------------
    st.subheader("Rubber Thickness Distribution by Zone")
    if 'rubber_mm' in df.columns and 'zone' in df.columns:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.boxplot(x="zone", y="rubber_mm", data=df, ax=ax2)
        st.pyplot(fig2)
    else:
        st.warning("Required columns 'rubber_mm' or 'zone' not found in the dataset")

    # -----------------------------
    # 5. Time-Series Trends
    # -----------------------------
    if "timestamp" in df.columns:
        st.subheader("Time-Series Trends")
        fig3 = px.line(df, x="timestamp", y="stress", color="zone", title="Stress over Time by Zone")
        st.plotly_chart(fig3, use_container_width=True)

        if "rubber_mm" in df.columns:
            fig4 = px.line(df, x="timestamp", y="rubber_mm", color="zone", title="Rubber Thickness over Time by Zone")
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No 'timestamp' column found for time-series analysis.")

    # -----------------------------
    # 6. Anomaly Correlation
    # -----------------------------
    if "anomaly" in df.columns and "stress" in df.columns and "rubber_mm" in df.columns:
        st.subheader("Anomalies in Stress vs Rubber Thickness")
        fig5 = px.scatter(
            df, x="stress", y="rubber_mm",
            color=df["anomaly"].map({0: "Normal", 1: "Anomaly"}),
            title="Stress vs Rubber Thickness (Anomalies Highlighted)",
            labels={"color": "Condition"}
        )
        st.plotly_chart(fig5, use_container_width=True)