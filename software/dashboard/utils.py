# software/dashboard/utils.py
import sqlite3
import pandas as pd
import os
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/smartzone_r.db")

def load_data():
    """
    Load runway data.
    1. First try to fetch from SQLite DB.
    2. If SQLite fails, fall back to local CSV (data/runway_data.csv).
    Returns: DataFrame
    """
    # Try SQLite first
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT * FROM runway_data", conn, parse_dates=["timestamp"])
            conn.close()
            st.sidebar.success("Data source: SQLite")
            return df
        else:
            raise FileNotFoundError(f"SQLite DB not found at {DB_PATH}")

    except Exception as db_error:
        st.warning(f"SQLite connection failed. Falling back to CSV. Error: {db_error}")
        try:
            csv_path = os.path.join(os.path.dirname(__file__), "../data/runway_data.csv")
            df = pd.read_csv(csv_path, parse_dates=["timestamp"])
            st.sidebar.info("Data source: CSV")
            return df
        except Exception as csv_error:
            st.error(f"Failed to load both SQLite DB and CSV: {csv_error}")
            return pd.DataFrame()