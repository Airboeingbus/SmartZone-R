import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append("..")
from utils import load_data

def app():
    st.title("Runway Maps")
    df = load_data()

    # Sidebar filters
    st.sidebar.subheader("Filters")
    if "timestamp" in df.columns:
        min_date, max_date = df["timestamp"].min(), df["timestamp"].max()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        if len(date_range) == 2:
            start, end = date_range
            df = df[(df["timestamp"] >= str(start)) & (df["timestamp"] <= str(end))]

    if "weather" in df.columns:
        weather_options = st.sidebar.multiselect("Weather Conditions", df["weather"].unique(), default=df["weather"].unique())
        df = df[df["weather"].isin(weather_options)]

    st.subheader("Average Stress per Zone")
    zone_stress = df.groupby("zone")["stress"].mean().reset_index()
    fig = px.bar(zone_stress, x="zone", y="stress", color="stress", title="Average Stress by Zone")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("FOD Weight Heatmap (by Zone)")
    fod_map = df.groupby("zone")["fod_weight_g"].mean().reset_index()
    fig2 = px.density_heatmap(fod_map, x="zone", y="fod_weight_g", 
                              nbinsx=len(fod_map["zone"].unique()), 
                              title="FOD Concentration by Zone",
                              color_continuous_scale="Reds")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Stress vs FOD Overlay")
    overlay = df.groupby("zone")[["stress", "fod_weight_g"]].mean().reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=overlay["zone"], y=overlay["stress"], name="Stress", marker_color="blue"))
    fig3.add_trace(go.Bar(x=overlay["zone"], y=overlay["fod_weight_g"], name="FOD Weight", marker_color="red"))
    fig3.update_layout(barmode="group", title="Stress vs FOD per Zone")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Trend Over Time (Stress & FOD)")
    if "timestamp" in df.columns:
        trend = df.groupby("timestamp")[["stress", "fod_weight_g"]].mean().reset_index()
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=trend["timestamp"], y=trend["stress"], mode="lines", name="Stress", line=dict(color="blue")))
        fig4.add_trace(go.Scatter(x=trend["timestamp"], y=trend["fod_weight_g"], mode="lines", name="FOD Weight", line=dict(color="red")))
        fig4.update_layout(title="Stress & FOD Trends Over Time", xaxis_title="Time", yaxis_title="Value")
        st.plotly_chart(fig4, use_container_width=True)