# software/dashboard/pages/alerts.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sys

sys.path.append("..")
from utils import load_data

st.set_page_config(layout="wide", page_title="Alerts - SmartZone-R")


# -----------------------------
# Helper functions
# -----------------------------
def categorize_thresholds(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Classify each row into a severity level based on thresholds.
    Returns a copy of df with a new 'severity' column.
    """
    df = df.copy()
    df["severity"] = "Normal"

    # Critical: very severe cases
    df.loc[
        (df["stress"] >= thresholds["stress"] * 1.5) |
        (df["fod_weight_g"] >= thresholds["fod_weight_g"] * 3),
        "severity"
    ] = "Critical"

    df.loc[
        (df["rubber_mm"] <= thresholds["rubber_mm"] * 0.2) &
        (df["cracks_mm"] >= thresholds["cracks_mm"] * 2),
        "severity"
    ] = "Critical"

    # High
    df.loc[(df["severity"] == "Normal") & (df["stress"] >= thresholds["stress"]), "severity"] = "High"
    df.loc[(df["severity"] == "Normal") & (df["rubber_mm"] <= thresholds["rubber_mm"]), "severity"] = "High"
    df.loc[(df["severity"] == "Normal") & (df["fod_weight_g"] >= thresholds["fod_weight_g"]), "severity"] = "High"
    df.loc[(df["severity"] == "Normal") & (df["cracks_mm"] >= thresholds["cracks_mm"]), "severity"] = "High"
    df.loc[(df["severity"] == "Normal") & (df["water_mm"] >= thresholds["water_mm"]), "severity"] = "High"

    # Medium (warning)
    df.loc[
        (df["severity"] == "Normal") & (df["stress"] >= thresholds["stress"] * 0.6),
        "severity"
    ] = "Medium"
    df.loc[
        (df["severity"] == "Normal") & (df["rubber_mm"] <= thresholds["rubber_mm"] * 1.5),
        "severity"
    ] = "Medium"
    df.loc[
        (df["severity"] == "Normal") & (df["fod_weight_g"] >= thresholds["fod_weight_g"] * 0.5),
        "severity"
    ] = "Medium"

    # ensure severity is categorical with order
    df["severity"] = pd.Categorical(df["severity"], categories=["Critical", "High", "Medium", "Normal"], ordered=True)
    return df


def create_csv_bytes(df: pd.DataFrame) -> bytes:
    """Return CSV bytes for use with st.download_button."""
    return df.to_csv(index=False).encode("utf-8")


def format_and_fill_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure expected columns exist and are typed sensibly.
    Adds defaults for missing columns to avoid runtime errors.
    """
    expected_cols = [
        "timestamp", "flight_id", "aircraft", "zone", "rubber_mm",
        "cracks_mm", "water_mm", "stress", "fod_weight_g",
        "temperature_C", "humidity_pct", "rain_mm", "anomaly"
    ]
    df = df.copy()

    for c in expected_cols:
        if c not in df.columns:
            if c == "timestamp":
                df[c] = pd.NaT
            elif c == "zone":
                df[c] = 0
            elif c == "flight_id":
                df[c] = ""
            elif c == "aircraft":
                df[c] = ""
            else:
                df[c] = 0

    # parse timestamp to datetime where possible
    try:
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    except Exception:
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(str), errors="coerce")

    # Cast numeric columns
    numeric_cols = ["rubber_mm", "cracks_mm", "water_mm", "stress", "fod_weight_g", "temperature_C", "humidity_pct", "rain_mm", "anomaly"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Cast zone to integer
    try:
        df["zone"] = pd.to_numeric(df["zone"], errors="coerce").fillna(0).astype(int)
    except Exception:
        df["zone"] = df["zone"].astype(int, errors="ignore")

    return df


# -----------------------------
# Main page
# -----------------------------
def app():
    st.title("Alerts")

    # Load data (from utils: SQLite / CSV fallback)
    df = load_data()
    if df is None:
        st.error("load_data() returned None. Check your data source.")
        return
    if df.empty:
        st.info("No data available. Run the simulator or provide runway_data.")
        return

    # Normalize / fill columns to avoid errors
    df = format_and_fill_columns(df)

    # Sidebar: thresholds
    st.sidebar.header("Alert Thresholds (adjust values)")
    stress_th = st.sidebar.slider("Stress threshold", min_value=10, max_value=500, value=100, step=5)
    rubber_th = st.sidebar.slider("Min rubber thickness (mm)", min_value=0.0, max_value=20.0, value=2.0, step=0.1)
    cracks_th = st.sidebar.slider("Cracks threshold (mm)", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
    water_th = st.sidebar.slider("Water accumulation (mm)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
    fod_th = st.sidebar.slider("FOD weight threshold (g)", min_value=0, max_value=2000, value=50, step=1)

    thresholds = {
        "stress": stress_th,
        "rubber_mm": rubber_th,
        "cracks_mm": cracks_th,
        "water_mm": water_th,
        "fod_weight_g": fod_th
    }

    # Evaluate severity column
    df_eval = categorize_thresholds(df, thresholds)

    # Derived partitions
    anomalies = df_eval[df_eval["anomaly"] == 1].copy()
    threshold_alerts = df_eval[df_eval["severity"] != "Normal"].copy()
    combined_alerts = pd.concat([anomalies, threshold_alerts]).drop_duplicates().reset_index(drop=True)

    # Summary KPIs
    total_records = len(df_eval)
    total_anomalies = int(df_eval["anomaly"].sum()) if "anomaly" in df_eval else 0
    total_threshold_alerts = len(threshold_alerts)
    worst_zone = threshold_alerts.groupby("zone").size().sort_values(ascending=False).index[0] if not threshold_alerts.empty else None

    st.subheader("Alert Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total records", total_records)
    c2.metric("Anomalies flagged", total_anomalies)
    c3.metric("Threshold alerts", total_threshold_alerts)
    c4.metric("Top alert zone", int(worst_zone) if worst_zone is not None else "—")

    st.markdown("---")

    # Section 1: Explicit anomalies
    st.subheader("1) Explicit Anomalies (anomaly == 1)")
    if anomalies.empty:
        st.info("No explicit anomalies found.")
    else:
        st.write(f"{len(anomalies)} explicit anomaly records found.")
        st.download_button("Download anomalies (CSV)", create_csv_bytes(anomalies), file_name="anomalies.csv", mime="text/csv")
        st.dataframe(anomalies.sort_values("timestamp", ascending=False).reset_index(drop=True))

    st.markdown("---")

    # Section 2: Threshold-based alerts
    st.subheader("2) Threshold-based Alerts")
    if threshold_alerts.empty:
        st.success("No threshold-based alerts at current thresholds.")
    else:
        # Identify reasons for each alert
        ta = threshold_alerts.copy()
        ta["reason"] = ""
        checks = [
            ("High Stress", ta["stress"] >= thresholds["stress"]),
            ("Low Rubber", ta["rubber_mm"] <= thresholds["rubber_mm"]),
            ("High Cracks", ta["cracks_mm"] >= thresholds["cracks_mm"]),
            ("Water Accumulation", ta["water_mm"] >= thresholds["water_mm"]),
            ("High FOD", ta["fod_weight_g"] >= thresholds["fod_weight_g"])
        ]
        for label, cond in checks:
            ta.loc[cond & (ta["reason"] == ""), "reason"] = label
            ta.loc[cond & (ta["reason"] != ""), "reason"] = ta.loc[cond & (ta["reason"] != ""), "reason"].astype(str) + ", " + label

        # Severity counts and top zones
        severity_counts = ta["severity"].value_counts().reindex(["Critical", "High", "Medium", "Normal"], fill_value=0)
        st.write("Severity counts")
        st.bar_chart(severity_counts)

        st.write("Top zones by alert count")
        top_zones = ta.groupby("zone").size().reset_index(name="alert_count").sort_values("alert_count", ascending=False)
        st.dataframe(top_zones.head(10))

        # Show detailed table and download
        st.write("Detailed threshold alerts")
        # Streamlit displays DataFrame well; additionally show colored style as HTML (optional)
        try:
            # show plain DataFrame first
            st.dataframe(ta.sort_values(["severity", "timestamp"], ascending=[True, False]).reset_index(drop=True))
        except Exception:
            st.write(ta)

        st.download_button("Download threshold alerts (CSV)", create_csv_bytes(ta), file_name="threshold_alerts.csv", mime="text/csv")

    st.markdown("---")

    # Section 3: Combined alerts
    st.subheader("3) Combined alerts (anomalies + threshold alerts)")
    if combined_alerts.empty:
        st.info("No combined alerts.")
    else:
        st.write(f"Total combined alerts: {len(combined_alerts)}")
        st.download_button("Download combined alerts (CSV)", create_csv_bytes(combined_alerts), file_name="combined_alerts.csv", mime="text/csv")
        st.dataframe(combined_alerts.sort_values("timestamp", ascending=False).reset_index(drop=True))

    st.markdown("---")

    # Section 4: Alerts over time
    st.subheader("4) Alerts over time")
    df_time = df_eval.copy()
    df_time["alert_flag"] = ((df_time["anomaly"] == 1) | (df_time["severity"] != "Normal")).astype(int)

    if "timestamp" in df_time.columns and not df_time["timestamp"].isna().all():
        df_time["hour"] = df_time["timestamp"].dt.floor("H")
        time_series = df_time.groupby("hour")["alert_flag"].sum().reset_index()
        if not time_series.empty:
            fig = px.line(time_series, x="hour", y="alert_flag", title="Alerts per Hour", labels={"hour": "Hour", "alert_flag": "Number of Alerts"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to render time-series.")
    else:
        st.info("Timestamp column missing or invalid; cannot show time-series.")

    st.markdown("---")

    # Section 5: Quick actions / exports
    st.subheader("5) Quick actions")
    qa1, qa2 = st.columns([1, 1])
    # Provide direct download buttons (download available even without clicking extra buttons)
    if not combined_alerts.empty:
        qa1.download_button("Download All Alerts (CSV)", create_csv_bytes(combined_alerts), file_name="all_alerts.csv", mime="text/csv")
    else:
        qa1.button("Download All Alerts (CSV)", disabled=True)

    # Summary text
    summary_text = (
        f"Total records: {total_records}\n"
        f"Anomalies (flagged): {total_anomalies}\n"
        f"Threshold alerts: {total_threshold_alerts}\n"
        f"Top alert zone: {int(worst_zone) if worst_zone is not None else '—'}"
    )
    if qa2.button("Show Summary (copyable)"):
        st.code(summary_text)

    st.markdown("End of alerts dashboard.")