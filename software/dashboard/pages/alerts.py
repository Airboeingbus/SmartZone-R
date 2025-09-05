import streamlit as st
import sys
sys.path.append("..")
from utils import load_data

def app():
    st.title("Alerts")
    df = load_data()

    st.subheader("Anomalies")
    anomalies = df[df["anomaly"] == 1]
    
    if anomalies.empty:
        st.success("No anomalies detected!")
    else:
        st.error(f"{len(anomalies)} anomalies detected!")
        st.dataframe(anomalies)
