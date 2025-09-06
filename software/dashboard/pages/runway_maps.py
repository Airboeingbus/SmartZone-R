import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import io
import os
import pandas as pd
sys.path.append("..")
from utils import load_data

st.set_page_config(layout="wide")


def app():
    st.title("Runway Maps")
    df = load_data()

    if df is None or df.empty:
        st.info("No runway data available. Run the simulator or check your data source.")
        return

    # -----------------------------
    # Enhanced Sidebar Filters
    # -----------------------------
    st.sidebar.subheader("Filters")

    # Multi-zone filter with select all option
    if "zone" in df.columns:
        zones = sorted(df["zone"].unique().tolist())
        select_all_zones = st.sidebar.checkbox("Select All Zones", True)
        
        if select_all_zones:
            selected_zones = st.sidebar.multiselect(
                "Select Zones",
                zones,
                default=zones
            )
        else:
            selected_zones = st.sidebar.multiselect(
                "Select Zones",
                zones
            )
        
        if selected_zones:
            df = df[df["zone"].isin(selected_zones)]
        else:
            st.warning("⚠️ No zones selected. Please select at least one zone.")
            return

    # Enhanced Weather filter with multiple conditions
    weather_filters = {}
    
    if "temperature_C" in df.columns:
        temp_range = st.sidebar.slider(
            "Temperature (°C)",
            float(df["temperature_C"].min()),
            float(df["temperature_C"].max()),
            (float(df["temperature_C"].min()), float(df["temperature_C"].max()))
        )
        df = df[
            (df["temperature_C"] >= temp_range[0]) & 
            (df["temperature_C"] <= temp_range[1])
        ]

    if "humidity_pct" in df.columns:
        humidity_range = st.sidebar.slider(
            "Humidity (%)",
            float(df["humidity_pct"].min()),
            float(df["humidity_pct"].max()),
            (float(df["humidity_pct"].min()), float(df["humidity_pct"].max()))
        )
        df = df[
            (df["humidity_pct"] >= humidity_range[0]) & 
            (df["humidity_pct"] <= humidity_range[1])
        ]

    if "rain_mm" in df.columns:
        rain_conditions = st.sidebar.multiselect(
            "Rain Conditions",
            ["No Rain", "Light Rain", "Heavy Rain"],
            default=["No Rain", "Light Rain", "Heavy Rain"]
        )
        
        rain_filters = []
        if "No Rain" in rain_conditions:
            rain_filters.append(df["rain_mm"] == 0)
        if "Light Rain" in rain_conditions:
            rain_filters.append((df["rain_mm"] > 0) & (df["rain_mm"] <= 5))
        if "Heavy Rain" in rain_conditions:
            rain_filters.append(df["rain_mm"] > 5)
            
        if rain_filters:
            df = df[pd.concat(rain_filters, axis=1).any(axis=1)]

    # Date range filter (keep existing code)
    if "timestamp" in df.columns:
        min_date, max_date = df["timestamp"].min(), df["timestamp"].max()
        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start, end = date_range
            df = df[
                (df["timestamp"].dt.date >= start) & 
                (df["timestamp"].dt.date <= end)
            ]

    # Add filter summary
    with st.sidebar.expander("Current Filters", expanded=False):
        st.write("Selected Zones:", ", ".join(map(str, selected_zones)))
        if "temperature_C" in df.columns:
            st.write(f"Temperature: {temp_range[0]:.1f}°C to {temp_range[1]:.1f}°C")
        if "humidity_pct" in df.columns:
            st.write(f"Humidity: {humidity_range[0]:.1f}% to {humidity_range[1]:.1f}%")
        if "rain_mm" in df.columns:
            st.write("Rain Conditions:", ", ".join(rain_conditions))
        if len(date_range) == 2:
            st.write(f"Date Range: {date_range[0]} to {date_range[1]}")

    # Reset filters button
    if st.sidebar.button("Reset All Filters"):
        st.rerun()

    # -----------------------------
    # 1. Interactive Zone Map
    # -----------------------------
    if {"x_coord", "y_coord", "zone"}.issubset(df.columns):
        st.subheader("Runway Zone Map (Interactive)")
        fig_map = px.scatter(
            df,
            x="x_coord",
            y="y_coord",
            color="stress",
            size="fod_weight_g",
            hover_data=["zone", "stress", "fod_weight_g", "rubber_mm"],
            title="Runway Layout with Stress & FOD",
        )
        st.plotly_chart(fig_map, use_container_width=True)
        export_button(fig_map, "runway_zone_map.png")

    # -----------------------------
    # 2. Drill-Down by Zone
    # -----------------------------
    if "zone" in df.columns:
        st.sidebar.subheader("Drill-Down")
        selected_zone = st.sidebar.selectbox("Select Zone for Drill-Down", ["All"] + list(df["zone"].unique()))
        if selected_zone != "All":
            df = df[df["zone"] == selected_zone]

    # -----------------------------
    # 3. Average Stress per Zone
    # -----------------------------
    st.subheader("Average Stress per Zone")
    zone_stress = df.groupby("zone")["stress"].mean().reset_index()
    fig1 = px.bar(zone_stress, x="zone", y="stress", color="stress", title="Average Stress by Zone")
    st.plotly_chart(fig1, use_container_width=True)
    export_button(fig1, "avg_stress_per_zone.png")

    # -----------------------------
    # 4. FOD Weight Heatmap
    # -----------------------------
    st.subheader("FOD Weight Heatmap (by Zone)")
    fod_map = df.groupby("zone")["fod_weight_g"].mean().reset_index()
    fig2 = px.density_heatmap(
        fod_map,
        x="zone",
        y="fod_weight_g",
        nbinsx=len(fod_map["zone"].unique()),
        title="FOD Concentration by Zone",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig2, use_container_width=True)
    export_button(fig2, "fod_heatmap.png")

    # -----------------------------
    # 5. Stress vs FOD Overlay
    # -----------------------------
    st.subheader("Stress vs FOD Overlay")
    overlay = df.groupby("zone")[["stress", "fod_weight_g"]].mean().reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=overlay["zone"], y=overlay["stress"], name="Stress", marker_color="blue"))
    fig3.add_trace(go.Bar(x=overlay["zone"], y=overlay["fod_weight_g"], name="FOD Weight", marker_color="red"))
    fig3.update_layout(barmode="group", title="Stress vs FOD per Zone")
    st.plotly_chart(fig3, use_container_width=True)
    export_button(fig3, "stress_vs_fod.png")

    # -----------------------------
    # 6. Rubber Depth Visualization
    # -----------------------------
    if "rubber_mm" in df.columns:
        st.subheader("Rubber Depth by Zone")
        rubber_map = df.groupby("zone")["rubber_mm"].mean().reset_index()
        fig4 = px.bar(rubber_map, x="zone", y="rubber_mm", color="rubber_mm", title="Rubber Depth by Zone")
        st.plotly_chart(fig4, use_container_width=True)
        export_button(fig4, "rubber_depth.png")

    # -----------------------------
    # 7. Comparative Trends
    # -----------------------------
    st.subheader("Trend Over Time (Stress, FOD, Rubber Depth)")
    if "timestamp" in df.columns:
        metrics = ["stress", "fod_weight_g"]
        if "rubber_mm" in df.columns:
            metrics.append("rubber_mm")

        trend = df.groupby("timestamp")[metrics].mean().reset_index()
        fig5 = go.Figure()
        for metric in metrics:
            fig5.add_trace(go.Scatter(
                x=trend["timestamp"],
                y=trend[metric],
                mode="lines",
                name=metric.replace("_", " ").title(),
            ))
        fig5.update_layout(title="Metric Trends Over Time", xaxis_title="Time", yaxis_title="Value")
        st.plotly_chart(fig5, use_container_width=True)
        export_button(fig5, "trends_over_time.png")


# -----------------------------
# Export Button using Plotly HTML
# -----------------------------
def export_button(fig, filename):
    """Export Plotly figure as HTML for interactive download."""
    html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
    html_filename = filename.replace(".png", ".html")
    st.download_button(
        label=f"Download {html_filename}",
        data=html_str,
        file_name=html_filename,
        mime="text/html",
    )

    with st.expander("How to save as image"):
        st.markdown("""
        1. Click the download button above to get the interactive plot
        2. Open the downloaded file in your browser
        3. Click the camera icon in the plot's toolbar
        4. Save as PNG/JPG/SVG
        """)