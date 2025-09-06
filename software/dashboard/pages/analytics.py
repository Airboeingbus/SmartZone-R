import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append("..")
from utils import load_data

st.set_page_config(layout="wide")


def app():
    st.title("Analytics")

    df = load_data()
    if df is None or df.empty:
        st.info("No runway data available. Run the simulator or check your data source.")
        return

    filtered_df = df.copy()  # copy for filtering

    # -----------------------------
    # Sidebar Filters
    # -----------------------------
    st.sidebar.subheader("Filters")

    # Zone filter
    if "zone" in df.columns:
        zones = df["zone"].unique().tolist()
        selected_zones = st.sidebar.multiselect("Select Zones", zones, default=zones)
        if selected_zones:
            filtered_df = filtered_df[filtered_df["zone"].isin(selected_zones)]
        else:
            st.warning("⚠️ No zones selected. Displaying all zones.")
            selected_zones = zones

    # Aircraft filter
    if "aircraft" in df.columns:
        aircraft_types = df["aircraft"].unique().tolist()
        selected_aircraft = st.sidebar.multiselect("Select Aircraft Types", aircraft_types, default=aircraft_types)
        if selected_aircraft:
            filtered_df = filtered_df[filtered_df["aircraft"].isin(selected_aircraft)]
        else:
            st.warning("⚠️ No aircraft types selected. Displaying all aircraft types.")
            selected_aircraft = aircraft_types

    # Date range filter
    if "timestamp" in df.columns:
        min_date, max_date = df["timestamp"].min(), df["timestamp"].max()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        if len(date_range) == 2:
            start, end = date_range
            filtered_df = filtered_df[(filtered_df["timestamp"] >= pd.to_datetime(start)) &
                                      (filtered_df["timestamp"] <= pd.to_datetime(end))]

    # Reset filters
    if st.sidebar.button("Reset Filters"):
        st.experimental_rerun()

    if filtered_df.empty:
        st.error("No data available for the selected filters. Please adjust your selection.")
        return

    df = filtered_df  # use filtered dataset

    # -----------------------------
    # 1. Data Preview
    # -----------------------------
    st.subheader("Runway Sensor Overview")
    st.dataframe(df.head(20))

    # -----------------------------
    # 2. Key Metrics
    # -----------------------------
    st.subheader("Key Metrics Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", len(df))
    col2.metric("Detected Anomalies", int(df["anomaly"].sum()) if "anomaly" in df else 0)
    col3.metric("Min Rubber Thickness (mm)", round(df["rubber_mm"].min(), 2) if "rubber_mm" in df else "N/A")
    col4.metric("Average Stress", round(df["stress"].mean(), 2) if "stress" in df else "N/A")

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
        export_button(fig3, "stress_over_time.html")

        if "rubber_mm" in df.columns:
            fig4 = px.line(df, x="timestamp", y="rubber_mm", color="zone", title="Rubber Thickness over Time by Zone")
            st.plotly_chart(fig4, use_container_width=True)
            export_button(fig4, "rubber_over_time.html")
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
            labels={"color": "Condition"},
            hover_data=["zone", "aircraft", "timestamp"]
        )
        st.plotly_chart(fig5, use_container_width=True)
        export_button(fig5, "anomaly_scatter.html")

    # -----------------------------
    # 7. Aircraft Type Impact
    # -----------------------------
    if "aircraft" in df.columns and "stress" in df.columns:
        st.subheader("Aircraft Type Impact on Stress")
        aircraft_avg = df.groupby("aircraft")["stress"].mean().reset_index().sort_values(by="stress", ascending=False)
        fig6 = px.bar(aircraft_avg, x="aircraft", y="stress", color="stress", title="Average Stress by Aircraft Type")
        st.plotly_chart(fig6, use_container_width=True)
        export_button(fig6, "aircraft_stress.html")


# -----------------------------
# Export Button for Plotly Figures
# -----------------------------
def export_button(fig, filename):
    """Export Plotly figure as interactive HTML."""
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
    st.download_button(
        label=f"Download {filename}",
        data=html_str,
        file_name=filename,
        mime="text/html"
    )