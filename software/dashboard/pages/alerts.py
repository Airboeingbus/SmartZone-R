import streamlit as st
import pandas as pd
import sys
sys.path.append("..")
from utils import load_data

def app():
    st.title("Alerts")
    df = load_data()

    st.subheader("Anomalies Detected in Runway Zones")

    # Original anomaly detection
    anomalies = df[df["anomaly"] == 1].copy()

    # Threshold-based checks
    df["severity"] = "Normal"
    df.loc[df["stress"] > 80, "severity"] = "High Stress"
    df.loc[(df["stress"] > 50) & (df["stress"] <= 80), "severity"] = "Medium Stress"
    df.loc[df["rubber_mm"] > 8, "severity"] = "Excessive Rubber"
    df.loc[df["fod_weight_g"] > 100, "severity"] = "High FOD"

    threshold_alerts = df[df["severity"] != "Normal"]

    if anomalies.empty and threshold_alerts.empty:
        st.success("✅ No anomalies or threshold violations detected.")
    else:
        if not anomalies.empty:
            st.error(f"⚠️ {len(anomalies)} anomalies detected!")
            st.dataframe(anomalies)

        if not threshold_alerts.empty:
            st.warning(f"⚠️ {len(threshold_alerts)} threshold-based alerts detected!")
            st.dataframe(threshold_alerts)

            # Download option
            csv = threshold_alerts.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Alerts as CSV",
                data=csv,
                file_name="runway_alerts.csv",
                mime="text/csv"
            )