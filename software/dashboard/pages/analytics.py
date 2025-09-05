import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append("..")
from utils import load_data


def app():
    st.title("Analytics")
    df = load_data()

    st.subheader("Runway Sensor Overview")
    st.dataframe(df.head(20))

    # Select only numeric columns for correlation
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    if not numeric_df.empty:
        st.subheader("Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No numeric columns available for correlation analysis")

    st.subheader("Rubber Thickness Distribution by Zone")
    if 'rubber_mm' in df.columns and 'zone' in df.columns:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.boxplot(x="zone", y="rubber_mm", data=df, ax=ax2)
        st.pyplot(fig2)
    else:
        st.warning("Required columns 'rubber_mm' or 'zone' not found in the dataset")
