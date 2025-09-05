import streamlit as st
import plotly.express as px
import sys
sys.path.append("..")
from utils import load_data

def app():
    st.title("Runway Maps")
    df = load_data()

    st.subheader("Average Stress per Zone")
    zone_stress = df.groupby("zone")["stress"].mean().reset_index()
    fig = px.bar(zone_stress, x="zone", y="stress", color="stress", title="Average Stress by Zone")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("FOD Weight Heatmap")
    fod_map = df.groupby("zone")["fod_weight_g"].mean().reset_index()
    fig2 = px.bar(fod_map, x="zone", y="fod_weight_g", color="fod_weight_g", title="Average FOD Weight by Zone")
    st.plotly_chart(fig2, use_container_width=True)
